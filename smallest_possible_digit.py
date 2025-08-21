n=input("enter a number : ")
list=[element for element in n]
sd=-1
P = 0
for i in range(len(list)-1,0,-1):
    if(list[i-1]<list[i]):
        p=i-1
        break
if p==0:
    print("")    
if list[p] < list[sd]:
    list[p],list[sd]=list[sd],list[p]
else:
    list[p],list[p+1]=list[p+1],list[p]
 
list[p+1:] = reversed(list[p+1:])
smallest=''.join(list)
print(smallest)