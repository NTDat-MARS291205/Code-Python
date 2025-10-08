n, m = map(int, input().split())
arr = []
for i in range(n):
    row = list(map(int, input().split()))
    arr.append(row)
max_val = -1
for i in range(n):
    for j in range(m):
        tmp = str(arr[i][j])
        if (len(tmp) > 1) and (tmp == tmp[::-1]):
            max_val = max(max_val, arr[i][j])
if max_val != -1:
    print(max_val)
    for i in range(n):
        for j in range(m):
            if arr[i][j] == max_val:
                print(f"Vi tri [{i}][{j}]")
else:
    print("NOT FOUND")
# 190