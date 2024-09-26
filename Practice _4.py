word1="abc"
word2="pqr"
list1=[]
merged=""
for i in range(0,2*len(word1),2):
    list1.insert(i,word1[i//2])
for i in range(1,2*len(word2),2):
    list1.insert(i,word2[i//2])
merged="".join(list1)
print(merged)