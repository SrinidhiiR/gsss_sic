import math
def is_perfect_square(number):
    if number<0:
        print(f"The number {number} is not a perfect square")
    else:
        root = math.sqrt(number)
        if root * root == number:
            print(f"The number {number} is a perfect square")
        else:
            print(f"The number {number} is  not a perfect square")
        
number = int(input("Enter a number to check if it is a perfect square:"))
is_perfect_square(number)