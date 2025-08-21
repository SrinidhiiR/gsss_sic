import tax_level_2 

if (tax_level_2.taxable_income >= 0 and tax_level_2.taxable_income <=300000):
    tax_percentage = 0
elif tax_level_2.taxable_income <=600000:
    tax_percentage = 5
elif tax_level_2.taxable_income <=900000:
    tax_percentage = 10
elif tax_level_2.taxable_income <=1200000:
    tax_percentage = 15
elif tax_level_2.taxable_income <=1500000:
    tax_percentage = 20
else :
    tax_percentage = 30
rebate_choice = input("Do you come under Section 87A Rebate (yes or no)")

tax_applied = (tax_level_2.taxable_income * tax_percentage)/100
cess = (4 * tax_applied)/100
tax_payable = tax_applied + cess

print ("Tax Scale : ")
print('''o ₹0 - ₹3,00,000: 0% \n o ₹3,00,001 - ₹6,00,000: 5% \n o ₹6,00,001 - ₹9,00,000: 10% \n o ₹9,00,001 - ₹12,00,000: 15% \n o ₹12,00,001 - ₹15,00,000: 20% \no Above ₹15,00,000: 30%''')
print(f'cess amount = {cess}')
print(f'Tax amount applied = {tax_applied}')
match rebate_choice :
    case 'yes':
        if tax_level_2.taxable_income <= 700000:
            print (f'Tax payable amount = 0')
    case _ :print (f'Tax payable amount = {tax_payable}')