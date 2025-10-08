import sys, math

EPS = 1e-9

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Triangle:
    def __init__(self, A, B, C):
        self.a = A.distance(B)
        self.b = B.distance(C)
        self.c = C.distance(A)
    def is_valid(self):
        if self.a <= 0.0 or self.b <= 0.0 or self.c <= 0.0:
            return False
        return (self.a + self.b > self.c and
                self.a + self.c > self.b and
                self.b + self.c > self.a)
    def area(self):
        p = (self.a + self.b + self.c)/2.0
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

tokens = sys.stdin.read().split()
t = int(float(tokens[0]))
i = 1
out = []
for _ in range(t):
    x1, y1, x2, y2, x3, y3 = map(float, tokens[i:i+6]); i += 6
    A, B, C = Point(x1, y1), Point(x2, y2), Point(x3, y3)
    tri = Triangle(A, B, C)
    out.append(f"{tri.area():.2f}" if tri.is_valid() else "INVALID")

print("\n".join(out))
