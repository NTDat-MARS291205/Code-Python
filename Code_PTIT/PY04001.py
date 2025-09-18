import math
class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


tc = int(input())
for _ in range(tc):
    x1, y1, x2, y2 = map(float, input().split())
    p1 = Point(x1, y1)
    p2 = Point(x2, y2)
    print(f"{p1.distance(p2):.4f}")