word1=input("Enter word1")
word2=input("Enter word2")
for i in range(1,len(word1)):
    for j in range(1,len(word2)) :
        if word1[:i+1]==word2[:j+1]:
            a=word1[:j+1]
b=0
for c in word1:
    if c not in a:
        b+=1
print(b)
if b>0:
    print("")
else:
    print(a)