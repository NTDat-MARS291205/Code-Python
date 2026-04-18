


class ChamCong:
    def __init__(self, maNV, ten, vao, ra):
        self.maNV = maNV
        self.ten = ten
        self.vao = vao
        self.ra = ra
        self.gio, self.phut = self.solve()
        self.trangThai = "DU" if self.gio*60 + self.phut >= 480 else "THIEU"

    def solve(self):
        start = list(map(int, self.vao.split(':')))
        end = list(map(int, self.ra.split(':')))
        total = end[0]*60 + end[1] - start[0]*60 - start[1] - 60
        gi = total // 60
        phu = total % 60
        return gi, phu

    def __str__(self):
        return f"{self.maNV} {self.ten} {self.gio} gio {self.phut} phut {self.trangThai}"

tc = int(input())
ds = []
for i in range(tc):
    maNV = input()
    ten = input()
    vao = input()
    ra = input()
    ds.append(ChamCong(maNV, ten, vao, ra))
ds.sort(key = lambda x: -(x.gio*60 + x.phut))
for d in ds:
    print(d)