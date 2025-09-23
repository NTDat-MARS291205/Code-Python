from math import gcd
class PhanSo:
    def __init__(self, tu, mau):
        ucln = gcd(tu, mau)
        self.tu = tu // ucln
        self.mau = mau // ucln
    
    def add(self, other):
        self.tu = self.tu * other.mau + other.tu * self.mau
        self.mau = self.mau * other.mau
        return PhanSo(self.tu, self.mau)

    def __str__(self):
        return f"{self.tu}/{self.mau}"
    
tu1, mau1, tu2, mau2 = map(int, input().split())
p1 = PhanSo(tu1, mau1)
p2 = PhanSo(tu2, mau2)
print(p1.add(p2))

