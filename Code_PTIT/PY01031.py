tc = int(input())
for _ in range(tc):
    n, b = map(int, input().split())
    s = ""
    while n > 0:
        du = n % b
        n = n // b
        if du < 10:
            s += str(du)
        else:
            tmp = ord("A") + (du - 10)
            s += chr(tmp)
    print(s[::-1])
# 148