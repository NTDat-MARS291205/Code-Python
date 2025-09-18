s1 = input()
s2 = input()
p = int(input())
# cu phap (slicing) cat chuoi, s[start:end:step], step mac dinh la 1
res = s1[: p - 1] + s2 + s1[p - 1 :] 
print(res)
# 143