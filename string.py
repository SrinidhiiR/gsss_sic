def string_find(*var_args): 
    string = var_args[1]
    substring = var_args[2]
    start = var_args[3]
    end = len(string)

    if len(var_args) == 3:
        start = var_args[2]
    elif len(var_args) == 4:
        start, end = var_args[2], var_args[3]

    len_string = len(string)
    len_substring = len(substring)

    if len_substring == 0:
        return start

    for i in range(start, min(end, len_string) - len_substring + 1):
        if string[i:i+len_substring] == substring:
            return i
    return -1




n = input("Enter a number: ")
digits = list(n)
i = len(digits) - 2
while i >= 0 and digits[i] >= digits[i+1]:
    i -= 1

if i == -1:
    print("Not possible")
else:
    # step 2: find just bigger digit on right side
    j = len(digits) - 1
    while digits[j] <= digits[i]:
        j -= 1

    # step 3: swap
    digits[i], digits[j] = digits[j], digits[i]

    # step 4: sort the remaining part
    digits[i+1:] = sorted(digits[i+1:])

    print("Next smallest bigger number:", ''.join(digits))
