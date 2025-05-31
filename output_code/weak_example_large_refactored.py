import random
import datetime
import string
import os
from collections import Counter

# --- Constants ---
DEFAULT_ERROR_AGE = -1
DEFAULT_ERROR_SALARY = 0.0
REPORT_FILENAME = "refactored_summary_output.txt"
INPUT_CSV_FILENAME = "refactored_input_data.csv"

# --- Helper Functions for Data Transformation and Validation ---

def parse_age(age_str):
    try:
        age = int(age_str)
        return 0 if age < 0 else age # Correct negative ages to 0
    except ValueError:
        return DEFAULT_ERROR_AGE

def parse_salary(salary_str):
    try:
        cleaned_val_str = salary_str.replace("$", "").replace("k", "000").replace(",", "")
        return float(cleaned_val_str)
    except ValueError:
        return DEFAULT_ERROR_SALARY

def parse_date_flexible(date_str):
    formats_to_try = [
        ("%d/%m/%Y", None), # DD/MM/YYYY
        ("%m/%d/%Y", None), # MM/DD/YYYY (common ambiguity)
        ("%Y-%m-%d", None), # YYYY-MM-DD
        ("%Y/%m/%d", None)  # YYYY/MM/DD
    ]
    for fmt, _ in formats_to_try:
        try:
            dt_obj = datetime.datetime.strptime(date_str, fmt).date()
            return dt_obj.isoformat() # Standardize to ISO format string
        except ValueError:
            continue
    return date_str # Return original if no format matches

def transform_name(name_str):
    name = name_str.strip()
    return name.title() if name else "No Name Provided"

def transform_city(city_str):
    city = city_str.strip().upper()
    if city == "NEW YORK CITY":
        return "NYC"
    return city

# --- Core Data Processing Functions ---

def read_csv_data(file_path):
    """Reads all lines from a CSV file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if not lines:
            print(f"Warning: File '{file_path}' is empty.")
        return lines
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return [] # Return empty list to prevent crash

def parse_csv_header(header_line):
    """Parses the header line to determine column names."""
    header_parts = [part.strip().lower() for part in header_line.split(',')]
    column_mapping = {}
    for i, part in enumerate(header_parts):
        if "name" in part:
            column_mapping[i] = "Name"
        elif "age" in part:
            column_mapping[i] = "Age"
        elif "city" in part:
            column_mapping[i] = "City"
        elif "salary" in part or "income" in part:
            column_mapping[i] = "Salary"
        elif "date" in part:
            column_mapping[i] = "Date"
        else:
            column_mapping[i] = f"Unknown_Col_{i+1}"
    return column_mapping

def process_row(row_str, header_map):
    """Transforms a single CSV row string into a dictionary with typed values."""
    values = row_str.strip().split(',')
    processed_dict = {}

    for idx, col_name_key in header_map.items():
        raw_value = values[idx].strip() if idx < len(values) else ""

        if col_name_key == "Name":
            processed_dict[col_name_key] = transform_name(raw_value)
        elif col_name_key == "Age":
            processed_dict[col_name_key] = parse_age(raw_value)
        elif col_name_key == "City":
            processed_dict[col_name_key] = transform_city(raw_value)
        elif col_name_key == "Salary":
            processed_dict[col_name_key] = parse_salary(raw_value)
        elif col_name_key == "Date":
            processed_dict[col_name_key] = parse_date_flexible(raw_value)
        else: # Unknown columns
            processed_dict[col_name_key] = raw_value
            
    return processed_dict

def validate_processed_data(records):
    """Validates a list of processed records based on defined criteria."""
    valid_records = []
    invalid_record_details = []

    for i, record in enumerate(records):
        is_valid_record = True
        errors = []

        age = record.get("Age", DEFAULT_ERROR_AGE)
        if not (isinstance(age, int) and 0 <= age <= 120 and age != DEFAULT_ERROR_AGE) :
            is_valid_record = False
            errors.append(f"Invalid Age: {age}")

        salary = record.get("Salary", DEFAULT_ERROR_SALARY)
        if not (isinstance(salary, float) and salary >= 0.0): # Allow 0.0
            is_valid_record = False
            errors.append(f"Invalid Salary: {salary}")
        
        if record.get("Name") == "No Name Provided":
            is_valid_record = False
            errors.append("Missing Name")
        
        if not record.get("City"):
            # Assuming city is optional for "validity" but good to note
            pass # errors.append("Missing City")

        if is_valid_record:
            valid_records.append(record)
        else:
            invalid_record_details.append({"index": i, "record_preview": str(record)[:70], "errors": errors})
            
    print(f"Data validation: {len(valid_records)} valid, {len(invalid_record_details)} invalid records.")
    return valid_records, invalid_record_details

def apply_custom_transformations_stage1(records, bonus_threshold_age=50, salary_bonus_factor=1.10):
    """Applies a first stage of custom business logic transformations."""
    transformed_records = []
    transformation_log = {"bonuses_applied": 0, "city_standardized": 0}

    for record in records:
        # Create a copy to avoid modifying the original list of dicts directly
        # if these records are used elsewhere.
        new_record = record.copy()

        if new_record.get("Age", 0) > bonus_threshold_age and isinstance(new_record.get("Salary"), float):
            new_record["Salary"] *= salary_bonus_factor
            new_record["bonus_applied_s1"] = True
            transformation_log["bonuses_applied"] += 1
        
        city = new_record.get("City", "")
        standardized_cities = {
            "LAX": "LOS ANGELES (Std)",
            "LOSANGELES": "LOS ANGELES (Std)",
        }
        if city in standardized_cities:
            new_record["City"] = standardized_cities[city]
            transformation_log["city_standardized"] += 1
        elif "SAN FRAN" in city: # More robust check might be needed
            new_record["City"] = "SAN FRANCISCO (Std)"
            transformation_log["city_standardized"] += 1
        
        # Example of a new derived field (less arbitrary than before)
        name_length = len(new_record.get("Name", ""))
        age_val = new_record.get("Age",0)
        if age_val != DEFAULT_ERROR_AGE:
            new_record["name_age_metric"] = name_length + age_val

        transformed_records.append(new_record)
        
    print(f"Custom transformations stage 1 complete. Log: {transformation_log}")
    return transformed_records

def filter_records_stage2(records, min_salary=20000.0, max_salary=200000.0):
    """Applies a second stage of filtering based on defined criteria."""
    filtered_records = []
    dropped_count = 0

    for record in records:
        keep_record = True
        
        salary = record.get("Salary")
        if not (isinstance(salary, float) and min_salary <= salary <= max_salary):
            keep_record = False
        
        name_age_metric = record.get("name_age_metric")
        if name_age_metric is None or name_age_metric < 0 : # Handle missing or error metric
             # Example: drop if metric suggests issue or is very low (e.g. < 25 for young person with short name)
            if name_age_metric is None or name_age_metric < (record.get("Age",0) if record.get("Age",0) > 0 else 20): # More meaningful condition
                keep_record = False
        
        if keep_record:
            filtered_records.append(record)
        else:
            dropped_count += 1
            
    print(f"Filtering stage 2 complete. Kept: {len(filtered_records)}, Dropped: {dropped_count}")
    return filtered_records

# --- Reporting Function ---

def generate_summary_report_data(records):
    """Aggregates data for the summary report."""
    if not records:
        return {
            "total_records": 0, "avg_age": 0, "avg_salary": 0,
            "city_counts": Counter(), "ages": [], "salaries": []
        }

    ages = [r["Age"] for r in records if isinstance(r.get("Age"), int) and r["Age"] != DEFAULT_ERROR_AGE]
    salaries = [r["Salary"] for r in records if isinstance(r.get("Salary"), float) and r["Salary"] > 0.0] # exclude 0 or error salary
    cities = [r.get("City", "N/A_City") for r in records]

    return {
        "total_records": len(records),
        "avg_age": sum(ages) / len(ages) if ages else 0,
        "avg_salary": sum(salaries) / len(salaries) if salaries else 0,
        "city_counts": Counter(cities),
        "ages": ages, # for potential further analysis like median/mode
        "salaries": salaries
    }

def format_summary_report(report_data, records_for_detail):
    """Formats the aggregated data and detailed records into a string report."""
    report_str = []
    report_str.append("=== Refactored Summary Report ===\n")
    report_str.append(f"Generated: {datetime.datetime.now().isoformat()}\n")
    report_str.append(f"Total Records in Detail Section: {report_data['total_records']}\n")
    report_str.append("=================================\n\n")

    report_str.append("--- Overall Statistics ---\n")
    report_str.append(f"  Average Age (Valid): {report_data['avg_age']:.2f}")
    report_str.append(f"  Average Salary (Valid & >0): ${report_data['avg_salary']:,.2f}")
    report_str.append("  City Frequencies:")
    for city, count in report_data['city_counts'].most_common(): # Display most common first
        report_str.append(f"    - {city}: {count}")
    report_str.append("\n")

    report_str.append("--- Detailed Records --- (First 10 or all)\n")
    for i, record in enumerate(records_for_detail[:10]): # Show details for first few records
        report_str.append(f"--- Item {i + 1} ---")
        report_str.append(f"  Name: {record.get('Name', 'N/A')}")
        report_str.append(f"  Age: {record.get('Age', 'N/A')}")
        report_str.append(f"  City: {record.get('City', 'N/A')}")
        report_str.append(f"  Salary: ${record.get('Salary', 0.0):,.2f}")
        report_str.append(f"  Join Date: {record.get('Date', 'N/A')}")
        if 'bonus_applied_s1' in record:
            report_str.append("  Note: Stage 1 Bonus Applied")
        if 'name_age_metric' in record:
            report_str.append(f"  Metric (NameLen+Age): {record['name_age_metric']}")
        report_str.append("") # Blank line for spacing

    if len(records_for_detail) > 10:
        report_str.append(f"... and {len(records_for_detail) - 10} more records not detailed.")
    
    report_str.append("\n=== End of Report ===")
    return "\n".join(report_str)

def write_report_to_file(report_content, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report successfully saved to '{filename}'")
    except IOError:
        print(f"Error: Could not write report to '{filename}'.")


# --- Sample CSV Generation (Utility) ---
def create_sample_csv(filename=INPUT_CSV_FILENAME, num_rows=70):
    """Generates a sample CSV file for processing if it doesn't exist."""
    if os.path.exists(filename):
        print(f"Sample CSV '{filename}' already exists. Using existing file.")
        return

    print(f"Generating sample CSV '{filename}' with {num_rows} rows.")
    header = "FullName,CurrentAge,LivingCity,AnnualIncome,StartDate\n"
    cities_sample = ["New York", "LA", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write(header)
        for i in range(num_rows):
            first_name = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(3,7))).capitalize()
            last_name = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(4,9))).capitalize()
            full_name = f"{first_name} {last_name}"
            
            age = str(random.randint(18, 80))
            if i % 10 == 0: age = random.choice(["thirty-five", "-5", "130", "NULL"]) # Introduce bad data

            city = random.choice(cities_sample)
            if i % 12 == 0: city = random.choice(["", "Unknown City", "New York City "]) # More varied city data

            income = str(random.randint(20000, 250000))
            if i % 9 == 0: income = random.choice(["80k", "$100,000.75", "Not Available", "0"])

            year, month, day = random.randint(2000, 2023), random.randint(1,12), random.randint(1,28)
            date_format_choice = random.random()
            if date_format_choice < 0.33: start_date = f"{day:02d}/{month:02d}/{year}"
            elif date_format_choice < 0.66: start_date = f"{year}-{month:02d}-{day:02d}"
            else: start_date = random.choice([f"{month}/{day}/{str(year)[2:]}", "Sometime ago", "InvalidDate"])
            
            extra_field = ""
            if i % 15 == 0: extra_field = ",BonusData" # Introduce occasional extra field

            f.write(f"{full_name},{age},{city},{income},{start_date}{extra_field}\n")
    print(f"Sample CSV '{filename}' created.")

# --- Main Execution Pipeline ---
def main_pipeline():
    """Runs the main data processing pipeline."""
    print("--- Starting Refactored Data Processing Pipeline ---")

    create_sample_csv() # Ensure sample data exists

    raw_lines = read_csv_data(INPUT_CSV_FILENAME)
    if not raw_lines or len(raw_lines) < 2:
        print("Pipeline halted: No data to process.")
        return

    header_line = raw_lines[0]
    data_lines = raw_lines[1:]

    column_map = parse_csv_header(header_line)
    print(f"CSV Header parsed. Column map: {column_map}")

    processed_records = []
    for i, line in enumerate(data_lines):
        if not line.strip():
            print(f"Skipping empty line at source index {i}.")
            continue
        processed_records.append(process_row(line, column_map))
    print(f"Initial processing complete: {len(processed_records)} records.")

    validated_records, invalid_details = validate_processed_data(processed_records)
    if invalid_details:
        print(f"Found {len(invalid_details)} invalid records. First few error details:")
        for detail in invalid_details[:3]: # Print details for first 3 invalid records
            print(f"  - Index {detail['index']}: {detail['errors']} (Preview: {detail['record_preview']})")
    
    if not validated_records:
        print("No valid records after validation. Cannot proceed further.")
        # Optionally, generate a report for invalid records or stop.
        report_data = generate_summary_report_data([]) # Empty data
        report_content = format_summary_report(report_data, [])
        write_report_to_file(report_content, REPORT_FILENAME)
        return

    transformed_s1_records = apply_custom_transformations_stage1(validated_records)
    filtered_s2_records = filter_records_stage2(transformed_s1_records)

    if not filtered_s2_records:
        print("No records remaining after filtering stage 2. Report will be based on earlier stage or be minimal.")
        # Decide what to report: e.g. transformed_s1_records or an empty set
        final_records_for_report = transformed_s1_records # Report on data before it was all filtered out
    else:
        final_records_for_report = filtered_s2_records
        
    report_data_aggregated = generate_summary_report_data(final_records_for_report)
    final_report_string = format_summary_report(report_data_aggregated, final_records_for_report)
    write_report_to_file(final_report_string, REPORT_FILENAME)

    print("--- Refactored Data Processing Pipeline Finished ---")

if __name__ == "__main__":
    main_pipeline()

# Summary of Refactoring Changes:
#
# This refactored code addresses numerous issues from the original "bad" CSV processing script.
# The key improvements include:
#
# * **Modularity and Single Responsibility:** Complex operations were broken down into smaller,
#     focused helper functions (e.g., `parse_age`, `parse_salary`, `transform_name`, `parse_date_flexible`).
#     Each function now has a clearer, more defined purpose.
# * **Reduced Global Variable Usage:** The reliance on numerous global variables (`glob_var_A` to `glob_var_F_list`)
#     for managing state and passing data has been significantly minimized. Data is now primarily
#     passed as arguments to functions and returned as results, improving clarity and reducing side effects.
# * **Improved File Handling:** Implemented `with open(...)` for reading and writing files, ensuring
#     that files are properly closed even if errors occur. Switched to UTF-8 encoding by default.
# * **Specific Error Handling:** Replaced bare `except:` clauses with more specific exception
#     handling (e.g., `ValueError`, `FileNotFoundError`), making debugging easier and the program more robust.
# * **Clearer Data Flow and Pipeline:** The main execution logic in `main_pipeline` now follows a more
#     logical sequence of operations, making the overall data processing flow easier to understand.
# * **Pythonic Practices:**
#     * Introduced list comprehensions (e.g., in `generate_summary_report_data`).
#     * Used `collections.Counter` for efficient frequency counting (e.g., city counts).
#     * Employed f-strings for formatted string interpolation in report generation and print statements.
#     * Functions now generally return values rather than printing directly, enhancing reusability.
# * **Introduction of Constants:** Defined constants (e.g., `DEFAULT_ERROR_AGE`, `REPORT_FILENAME`)
#     at the beginning of the script to replace magic numbers and hardcoded strings, improving maintainability.
# * **Structured Data Transformation:** Type conversions and data cleaning steps are now more explicit
#     and handled by dedicated functions, making the transformation logic more transparent.
# * **Enhanced Reporting:** The reporting function was split into data aggregation (`generate_summary_report_data`)
#     and formatting (`format_summary_report`), improving separation of concerns. The report content is also more structured.
# * **Readability and Naming:** While not a primary focus for every line, an effort was made to use
#     clearer function and variable names compared to the intentionally obscure ones in the "bad" version.
#