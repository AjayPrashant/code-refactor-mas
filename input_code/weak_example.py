# weak_example.py

def greet(name):
 print("hello " + name + "!!!")
 
def calc_area(radius):
 pi = 3.14
 area = pi * radius * radius
 print("Area is:", area)
 
def is_even(n):
    if n % 2 == 0:
        return True
    else:
        return False
        
numbers = [1,2,3,4,5,6]
for i in range(len(numbers)):
    print(numbers[i], "is even:", is_even(numbers[i]))
