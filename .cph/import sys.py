import sys

# Khởi tạo danh sách để lưu số Catalan
catalan = [0] * 105

def init(n):
    if n <= 1:
        return 1
    catalan[0], catalan[1] = 1, 1
    
    for i in range(2, n + 1):
        catalan[i] = 0
        for j in range(i):
            catalan[i] += catalan[j] * catalan[i - j - 1]
    
    return catalan[n]

def main():
    # Đọc tất cả input cùng lúc để tăng tốc độ xử lý
    input_data = sys.stdin.read().split()
    t = int(input_data[0])
    
    results = []
    for i in range(1, t + 1):
        n = int(input_data[i])
        results.append(str(init(n)))
    
    # In kết quả một lần để tránh chậm khi in từng dòng
    print("\n".join(results))

if __name__ == "__main__":
    main()