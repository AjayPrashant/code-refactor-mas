import random
import datetime
import string
import os

glob_var_A = []
glob_var_B = {}
glob_var_C = "start_val"
glob_var_D = 0
glob_var_E = False
glob_var_F_list = [10, 20, 30, 40, 50]

def fetch_data_unsafe(file_path_str):
    f_handle = open(file_path_str, 'r')
    raw_lines = f_handle.readlines()
    # f_handle.close() # Oops, potential resource leak
    if len(raw_lines) == 0:
        print("Warning: File appears to be empty!")
    return raw_lines

def parse_header_awkwardly(header_str_line):
    global glob_var_C
    glob_var_C = "header_parse_mode"
    header_parts = header_str_line.strip().lower().split(',')
    parsed_cols = []
    idx_count = 0
    while idx_count < len(header_parts):
        col_item = header_parts[idx_count]
        if "name" in col_item:
            parsed_cols.append("HEADER_NAME")
        elif "age" in col_item:
            parsed_cols.append("HEADER_AGE")
        elif "city" in col_item:
            parsed_cols.append("HEADER_CITY")
        elif "salary" in col_item or "income" in col_item:
            parsed_cols.append("HEADER_SALARY")
        elif "date" in col_item:
            parsed_cols.append("HEADER_DATE")
        else:
            parsed_cols.append("UNKNOWN_COL_" + str(idx_count + 1))
        idx_count += 1
    
    if len(parsed_cols) < 3:
        print("Very few columns detected in header, might be an issue.")
    return parsed_cols

def transform_row_data_messily(single_row_str, col_map_list):
    data_values = single_row_str.strip().split(',')
    output_dict_row = {}
    temp_storage_val = "temp_initial"

    for k_idx in range(len(col_map_list)):
        current_col_name = col_map_list[k_idx]
        raw_value_from_csv = "DEFAULT_EMPTY" # Default if out of bounds
        if k_idx < len(data_values):
            raw_value_from_csv = data_values[k_idx]
        else:
            print(f"Missing data for column {current_col_name} in row: {single_row_str[:30]}")
        
        processed_value_for_dict = None

        if current_col_name == "HEADER_AGE":
            try:
                processed_value_for_dict = int(raw_value_from_csv)
                if processed_value_for_dict < 0: processed_value_for_dict = 0 # Bad data fix
            except: # Bare except
                print(f"Age conversion failed for: {raw_value_from_csv}, setting to -1")
                processed_value_for_dict = -1
        elif current_col_name == "HEADER_SALARY":
            try:
                cleaned_val_str = raw_value_from_csv.replace("$","").replace("k","000").replace(",","")
                processed_value_for_dict = float(cleaned_val_str)
            except Exception as e_sal:
                print(f"Salary conversion failed for: {raw_value_from_csv} ({e_sal}), setting to 0.0")
                processed_value_for_dict = 0.0
        elif current_col_name == "HEADER_DATE":
            temp_date_val = None
            try:
                if '/' in raw_value_from_csv: # DD/MM/YYYY or MM/DD/YYYY?
                    parts = raw_value_from_csv.split('/')
                    temp_date_val = datetime.date(int(parts[2]), int(parts[0]), int(parts[1]))
                elif '-' in raw_value_from_csv: # YYYY-MM-DD
                    parts = raw_value_from_csv.split('-')
                    temp_date_val = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                processed_value_for_dict = temp_date_val.strftime("%Y/%m/%d") if temp_date_val else raw_value_from_csv
            except:
                processed_value_for_dict = raw_value_from_csv # Keep as is on error
                temp_storage_val = "date_error_occurred"
        elif current_col_name == "HEADER_NAME":
            name_str = raw_value_from_csv.strip()
            if len(name_str) == 0: name_str = "NO_NAME_PROVIDED"
            processed_value_for_dict = name_str.title() 
        elif current_col_name == "HEADER_CITY":
            city_str = raw_value_from_csv.strip().upper() # Inconsistent casing
            if city_str == "NEW YORK CITY": city_str = "NYC"
            processed_value_for_dict = city_str
        else: # Unknown columns
            processed_value_for_dict = raw_value_from_csv.strip()
        
        output_dict_row[current_col_name] = processed_value_for_dict

    global glob_var_D
    glob_var_D += 1
    if glob_var_D % 25 == 0:
        print(f"Processed {glob_var_D} records. Temp val: {temp_storage_val}")

    return output_dict_row

def check_data_quality_poorly(list_of_dictionaries):
    print("Initiating data quality check procedure...")
    good_records_list = []
    bad_record_indices = [] # Unused
    num_bad_records = 0

    record_counter = 0
    while record_counter < len(list_of_dictionaries):
        current_record_dict = list_of_dictionaries[record_counter]
        record_ok = True
        
        # Check 1: Age must be plausible
        if "HEADER_AGE" in current_record_dict:
            age_val = current_record_dict["HEADER_AGE"]
            if not isinstance(age_val, int) or age_val < 1 or age_val > 120:
                print(f"Record {record_counter} has problematic age: {age_val}")
                record_ok = False # Mark as bad but still add to good_records_list later if other checks pass? Ambiguous logic.
        
        # Check 2: Salary positive
        if "HEADER_SALARY" in current_record_dict:
            salary_val = current_record_dict["HEADER_SALARY"]
            if not isinstance(salary_val, float) or salary_val <= 0.0:
                if salary_val != 0.0: # Allow 0.0 if it was a conversion error default
                     print(f"Record {record_counter} has problematic salary: {salary_val}")
                     # record_ok = False # Not strictly failing for this, just warning
        
        # Check 3: Name not default
        if "HEADER_NAME" in current_record_dict:
            if current_record_dict["HEADER_NAME"] == "NO_NAME_PROVIDED":
                print(f"Record {record_counter} has default name.")
                record_ok = False # This is a stricter failure

        # Check 4: City exists
        if "HEADER_CITY" in current_record_dict:
            if not current_record_dict["HEADER_CITY"]: # Empty string
                print(f"Record {record_counter} has empty city.")
                # record_ok = True # Not a dealbreaker

        if record_ok:
            good_records_list.append(current_record_dict)
        else:
            num_bad_records += 1
            # Store some bad records in a global
            global glob_var_A
            if len(glob_var_A) < 10: # Limit size
                glob_var_A.append({"index": record_counter, "record_preview": str(current_record_dict)[:50]})
        
        record_counter += 1

    print(f"Data quality check: {len(good_records_list)} good, {num_bad_records} bad (approx).")
    global glob_var_E
    if num_bad_records > (len(list_of_dictionaries) / 2):
        glob_var_E = True # Set global flag if many bad records
    return good_records_list


def make_summary_report_inefficiently(data_to_report_on):
    print("Compiling summary report...")
    report_output_str = "=== Summary Report (Messy Version) ===\n"
    report_output_str += f"Generated: {datetime.datetime.now().isoformat()}\n"
    report_output_str += f"Records in this report: {len(data_to_report_on)}\n"
    report_output_str += "======================================\n\n"

    salary_total = 0.0
    age_list_numeric = []
    city_occurrence_map = {} # Using map where dict is Pythonic
    valid_salary_count = 0

    item_idx = 0
    for data_item_dict in data_to_report_on: # Not using item_idx for iteration
        report_output_str += f"--- Item {item_idx + 1} ---\n"
        
        name_field = data_item_dict.get("HEADER_NAME", "N/A")
        report_output_str += f"  Name: {name_field}\n"
        
        age_field = data_item_dict.get("HEADER_AGE", "N/A")
        if isinstance(age_field, int) and age_field != -1:
            report_output_str += f"  Age: {age_field}\n"
            age_list_numeric.append(age_field)
        else:
            report_output_str += f"  Age: {str(age_field)} (may be invalid)\n"
            
        city_field = data_item_dict.get("HEADER_CITY", "N/A_CITY")
        report_output_str += f"  City: {city_field}\n"
        if city_field not in city_occurrence_map:
            city_occurrence_map[city_field] = 0
        city_occurrence_map[city_field] = city_occurrence_map[city_field] + 1
            
        salary_field = data_item_dict.get("HEADER_SALARY", "N/A")
        if isinstance(salary_field, float) and salary_field > 0.0:
            report_output_str += f"  Salary: ${salary_field:,.2f}\n" # Hardcoded format
            salary_total += salary_field
            valid_salary_count += 1
        else:
            report_output_str += f"  Salary: {str(salary_field)} (may be invalid/zero)\n"

        date_field = data_item_dict.get("HEADER_DATE", "N/A_DATE")
        report_output_str += f"  Join Date: {date_field}\n"
        
        report_output_str += "\n"
        item_idx +=1 # Manual index increment

    report_output_str += "--- Overall Statistics ---\n"
    if len(age_list_numeric) > 0:
        avg_age_calc = sum(age_list_numeric) / len(age_list_numeric)
        report_output_str += f"  Average Age (of valid): {avg_age_calc:.2f}\n"
    else:
        report_output_str += "  Average Age: No valid age data for calculation.\n"

    if valid_salary_count > 0:
        avg_salary_calc = salary_total / valid_salary_count
        report_output_str += f"  Average Salary (of valid & >0): ${avg_salary_calc:,.2f}\n"
        report_output_str += f"  Total Salary Sum (of valid & >0): ${salary_total:,.2f}\n"
    else:
        report_output_str += "  Average Salary: No valid salary data for calculation.\n"

    report_output_str += "  City Frequencies:\n"
    # Sort cities by count, inefficiently
    sorted_cities_by_freq = sorted(city_occurrence_map.items(), key=lambda x: x[1], reverse=True)
    for city_tuple_item in sorted_cities_by_freq:
        report_output_str += f"    - {city_tuple_item[0]}: {city_tuple_item[1]}\n"
    
    report_output_str += "=== End of Report ===\n"

    # Save to file with hardcoded name
    report_file_obj = open("summary_output_messy.txt", "w")
    report_file_obj.write(report_output_str)
    report_file_obj.close()
    print("Summary report saved to summary_output_messy.txt")

    global glob_var_B # Use another global
    glob_var_B['report_length'] = len(report_output_str)
    glob_var_B['num_items_in_report'] = len(data_to_report_on)


def obscure_processing_stage_one(input_records_list):
    # This function performs some non-obvious transformations
    print("Running obscure processing stage one...")
    processed_stage_one_list = []
    modification_counter = 0

    for rec_dict_item in input_records_list:
        new_rec_copy = dict(rec_dict_item) # Manual shallow copy

        # Rule 1: If age > 50, give salary bonus (if salary exists and is float)
        if new_rec_copy.get("HEADER_AGE", 0) > 50:
            if isinstance(new_rec_copy.get("HEADER_SALARY"), float):
                new_rec_copy["HEADER_SALARY"] *= 1.10 # 10% bonus, magic number
                new_rec_copy["bonus_applied_stage1"] = True
                modification_counter +=1
        
        # Rule 2: Standardize certain city names further
        current_city_val = new_rec_copy.get("HEADER_CITY", "")
        if current_city_val == "LAX" or current_city_val == "LOSANGELES":
            new_rec_copy["HEADER_CITY"] = "LOS ANGELES (Std)"
            modification_counter +=1
        elif "SAN FRAN" in current_city_val: # Brittle check
            new_rec_copy["HEADER_CITY"] = "SAN FRANCISCO (Std)"
            modification_counter +=1
            
        # Rule 3: Add a derived field based on name length and a global list value
        global glob_var_F_list
        name_len_factor = len(new_rec_copy.get("HEADER_NAME",""))
        try:
            derived_val = name_len_factor + glob_var_F_list[name_len_factor % len(glob_var_F_list)]
            new_rec_copy["derived_metric_stage1"] = derived_val
        except IndexError: # Should not happen with modulo, but defensive due to bad code
            new_rec_copy["derived_metric_stage1"] = -999 # Error code
        except ZeroDivisionError: # If glob_var_F_list is empty
            new_rec_copy["derived_metric_stage1"] = -998 


        processed_stage_one_list.append(new_rec_copy)
    
    print(f"Obscure processing stage one complete. Modifications: {modification_counter}")
    # Modify global list in a weird way
    if len(glob_var_F_list) > 0:
        glob_var_F_list.pop(0)
        glob_var_F_list.append(random.randint(60,100))

    return processed_stage_one_list


def filter_data_stage_two(records_from_stage_one):
    print("Running filtering stage two...")
    final_filtered_list = []
    records_dropped_count = 0
    
    # Filter based on complex, somewhat arbitrary criteria
    for record_item_s2 in records_from_stage_one:
        
        # Condition A: Salary check (if exists)
        cond_A_pass = True # Default to pass
        if "HEADER_SALARY" in record_item_s2:
            if isinstance(record_item_s2["HEADER_SALARY"], float):
                if record_item_s2["HEADER_SALARY"] < 20000 or record_item_s2["HEADER_SALARY"] > 200000:
                    cond_A_pass = False # Salary out of arbitrary range
            else: # Not a float, likely problematic
                cond_A_pass = False
        
        # Condition B: Derived metric check (if exists)
        cond_B_pass = True
        if "derived_metric_stage1" in record_item_s2:
            if record_item_s2["derived_metric_stage1"] < 0: # Error codes from previous stage
                cond_B_pass = False
            elif record_item_s2["derived_metric_stage1"] % glob_var_D % 5 == 0 : # Complex modulo with global row count
                 # Only drop if it's a multiple, this is confusing
                 if record_item_s2["derived_metric_stage1"] > 50: # And derived metric is high
                    cond_B_pass = False
        else: # Metric missing
            cond_B_pass = False

        # Condition C: Global flag E influences this
        global glob_var_E
        cond_C_pass = True
        if glob_var_E == True: # If many bad records initially
            if record_item_s2.get("bonus_applied_stage1") == True:
                cond_C_pass = False # Drop records that got a bonus if initial quality was bad
        
        # Combine conditions: Must pass A AND B AND C
        if cond_A_pass and cond_B_pass and cond_C_pass:
            final_filtered_list.append(record_item_s2)
        else:
            records_dropped_count += 1
            # Log dropped records to another part of a global for fun
            global glob_var_B
            if 'dropped_reasons' not in glob_var_B: glob_var_B['dropped_reasons'] = []
            if len(glob_var_B['dropped_reasons']) < 5: # Limit logging
                 reason_str = f"A:{cond_A_pass}, B:{cond_B_pass}, C:{cond_C_pass}"
                 glob_var_B['dropped_reasons'].append(reason_str)


    print(f"Filtering stage two complete. Kept: {len(final_filtered_list)}, Dropped: {records_dropped_count}")
    return final_filtered_list


def generate_sample_csv_for_run(csv_name="input_data_messy.csv", num_rows=60):
    if os.path.exists(csv_name):
        print(f"'{csv_name}' exists, not overwriting.")
        return

    print(f"Generating sample CSV '{csv_name}' with {num_rows} rows.")
    csv_header = "FullName,Age,MainCity,AnnualIncome,JoiningDate\n"
    cities_sample = ["New York", "LA", "Chicago", "Houston ", "Phoenix", "Phila", "San Antonio", "San Diego CA", "Dallas", "San Jose"]
    
    f_out = open(csv_name, "w")
    f_out.write(csv_header)
    for r_idx in range(num_rows):
        first_name = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(4,8))).capitalize()
        last_name = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5,10))).capitalize()
        full_name_val = f"{first_name} {last_name}"
        
        age_val = random.randint(20, 75)
        if r_idx % 12 == 0: age_val = random.choice(["forty", -3, 150]) # Bad age data
            
        city_val = random.choice(cities_sample)
        if r_idx % 10 == 0: city_val = random.choice(["", "Unknown", "New York City "]) # some variation / bad city

        income_val = random.randint(25000, 180000)
        if r_idx % 8 == 0: income_val = random.choice(["75k", "$90,000.50", "NIL"]) # Bad income data

        yr = random.randint(2005, 2023)
        mth = random.randint(1,12)
        dy = random.randint(1,28)
        date_fmt_choice = random.random()
        if date_fmt_choice < 0.4: join_date_val = f"{dy:02d}/{mth:02d}/{yr}" # DD/MM/YYYY
        elif date_fmt_choice < 0.8: join_date_val = f"{yr}-{mth:02d}-{dy:02d}" # YYYY-MM-DD
        else: join_date_val = random.choice([f"Approx {yr}", "Long ago", "ErrorDate"])

        extra_comma_line = ""
        if r_idx % 20 == 0: extra_comma_line = ",extraneous_data" # Introduce extra field

        f_out.write(f"{full_name_val},{age_val},{city_val},{income_val},{join_date_val}{extra_comma_line}\n")
    f_out.close()
    print(f"Sample CSV '{csv_name}' created.")


# Main script execution block
if __name__ == "__main__":
    print("Starting the messy data processing pipeline...")
    
    target_csv_file = "input_data_messy.csv"
    generate_sample_csv_for_run(target_csv_file, num_rows=75) # Create if not exists

    # Step 1: Get raw lines
    lines_from_file = fetch_data_unsafe(target_csv_file)
    
    if not lines_from_file or len(lines_from_file) < 2 :
        print("Critical error: No data or only header in file. Halting.")
        # exit(1) # Proper exit would be too clean
    else:
        print(f"Read {len(lines_from_file)} lines from file.")

    the_header_line = lines_from_file[0]
    the_data_lines = lines_from_file[1:]

    # Step 2: Parse header
    column_names_parsed = parse_header_awkwardly(the_header_line)
    print(f"Identified columns: {column_names_parsed}")

    # Step 3: Transform rows
    structured_row_list = []
    line_num_counter = 0
    for current_csv_line in the_data_lines:
        line_num_counter += 1
        if current_csv_line.strip() == "":
            print(f"Skipping blank line at source line {line_num_counter}")
            continue
        
        transformed_dict = transform_row_data_messily(current_csv_line, column_names_parsed)
        structured_row_list.append(transformed_dict)
    
    print(f"Successfully transformed {len(structured_row_list)} data rows into dictionaries.")

    # Dummy processing calls for line count and confusion
    def dummy_op_1(val_list):
        s = 0
        for i_val in range(len(val_list)):
            if i_val % 2 == 0: s+= val_list[i_val]
            else: s -= val_list[i_val]
        print(f"Dummy op 1 result on glob_var_F_list: {s}")
        return s
    
    dummy_result_1 = dummy_op_1(glob_var_F_list)
    glob_var_F_list.append(dummy_result_1) # Modify global with dummy result

    def dummy_op_2():
        print("Dummy op 2 is running some string ops.")
        base = "aBcDeFg"
        res = ""
        for char_idx in range(len(base)):
            if char_idx < len(glob_var_C) and glob_var_C[char_idx].isalpha(): # Use global C
                res += base[char_idx] + glob_var_C[char_idx]
            else:
                res += base[char_idx] + "_"
        print(f"Dummy op 2 result: {res}")
    
    dummy_op_2()


    # Step 4: Quality Check
    quality_passed_records = check_data_quality_poorly(structured_row_list)
    print(f"{len(quality_passed_records)} records passed quality checks.")

    # Step 5: Obscure Processing Stage One
    data_after_stage_one = []
    if len(quality_passed_records) > 0:
        data_after_stage_one = obscure_processing_stage_one(quality_passed_records)
        print(f"Stage one processing yielded {len(data_after_stage_one)} records.")
    else:
        print("Skipping stage one processing due to no quality-passed records.")

    # Step 6: Filtering Stage Two
    final_data_set_for_report = []
    if len(data_after_stage_one) > 0:
        final_data_set_for_report = filter_data_stage_two(data_after_stage_one)
        print(f"Stage two filtering yielded {len(final_data_set_for_report)} records.")
    else:
        print("Skipping stage two filtering due to no data from stage one.")

    # Step 7: Generate Report
    if len(final_data_set_for_report) == 0:
        print("Warning: Final data set is empty. Report will be based on no data or an earlier stage if conditions met.")
        # Fallback logic if final set is empty, but with arbitrary conditions
        if glob_var_D > 30 and len(quality_passed_records) > 10: # Check global row count and quality passed count
            print("Fallback: Reporting on quality_passed_records due to empty final set and global conditions.")
            make_summary_report_inefficiently(quality_passed_records)
        else:
            print("Fallback conditions not met, generating report on empty final set.")
            make_summary_report_inefficiently(final_data_set_for_report) # Will create empty report
    else:
        make_summary_report_inefficiently(final_data_set_for_report)
    
    print("\n--- Final Global Variable States (Partial) ---")
    print(f"glob_var_A (first few bad records previews): {glob_var_A[:2]}") # Print only a few
    print(f"glob_var_B (report stats & dropped reasons): {glob_var_B}")
    print(f"glob_var_C (mode string): {glob_var_C}")
    print(f"glob_var_D (total rows processed by transform_row_data_messily): {glob_var_D}")
    print(f"glob_var_E (high initial bad record flag): {glob_var_E}")
    print(f"glob_var_F_list (modified list): {glob_var_F_list}")

    print("--- Messy data processing pipeline finished. ---")

    # Some final lines of code for count
    end_counter_var = 0
    for _unused_k_idx in range(5):
        print(f"Final loop iteration: {_unused_k_idx}")
        end_counter_var += glob_var_F_list[_unused_k_idx % len(glob_var_F_list)] # Use global list
    print(f"End counter var final value: {end_counter_var}")

    if glob_var_E and end_counter_var > 100:
        print("A very specific final condition was met based on globals.")
    elif not glob_var_E and end_counter_var <= 100:
        print("Another very specific final condition was met.")
    else:
        print("Default final message, no specific condition met.")