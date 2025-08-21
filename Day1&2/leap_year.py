def is_leap_year(year):
    if ( year % 4 == 0 and year % 100 != 0 ) or ( year % 400 == 0):
        print(f"{year} is a Leap Year")
    else:
        print(f"{year} is not a Leap Year")

year = int(input("Enter a year to check if it is a Leap Year: "))
is_leap_year(year)
