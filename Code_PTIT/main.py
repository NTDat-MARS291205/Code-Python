import math

def convert(s):
    sum = 0
    if s[0] == '1':
        sum += 4
    if s[1] == '1':
       sum += 2
    if s[2] == '1':
        sum += 1
    return str(sum)

num = input()
num = num.zfill(len(num) + (3 - len(num) % 3) % 3)
res = ""
for i in range(0, len(num), 3):
    tmp = num[i:i+3]
    res += convert(tmp)
print(res)