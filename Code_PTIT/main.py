import sys

class ThiSinh:
    def __init__(self, name, birth, subject1, subject2, subject3):
        self.name = name
        self.birth = birth
        self.subject1 = subject1
        self.subject2 = subject2
        self.subject3 = subject3
    def total(self):
        return self.subject1 + self.subject2 + self.subject3

tmp = sys.stdin.read().split()
name = " ".join(tmp[:3]).strip()
a = ThiSinh(name, tmp[3], float(tmp[4]), float(tmp[5]), float(tmp[6]))
print(f"{a.name} {a.birth} {a.total():.1f}")
