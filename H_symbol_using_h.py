n=int(input("Enter value for design"))
for i in range(1,n+1):
    for j in range(n-i,0,-1):
        print(" ",end="")
    for j in range(2*i-1):
        print("H",end="")
    print("\n")   
for i in range(n+1):
    for j in range(n+2):
        if j==0 or j==1:
            print(" ",end="")
        else:
            print("H",end="")
    for j in range(3*n+1):
        print(" ",end="")
    for j in range(n):
        print("H",end="")
    print("\n")
for i in range(n-2):
    for j in range(6*n-2):
        if j==0 or j==1:
            print(" ",end="")
        else:
            print("H",end="")
    print("\n")  
for i in range(n+1):
    for j in range(n+2):
        if j==0 or j==1:
            print(" ",end="")
        else:
            print("H",end="")
    for j in range(3*n+1):
        print(" ",end="")
    for j in range(n):
        print("H",end="")
    print("\n")
for i in range(n):
    for j in range(4*n+1+i):
        print(" ",end="")
    for j in range(2*n-2*i-1):
        print("H",end="")
    print("\n")  