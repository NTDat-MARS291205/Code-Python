tc = int(input())
for _ in range(tc):
    n, b = map(int, input().split())
    s = ""
    while n > 0:
        d = n % b
        n = n // b
        if d < 10:
            s += str(d)
        else:
            tmp = ord("A") + (d - 10)
            s += chr(tmp)
    print(s[::-1])
