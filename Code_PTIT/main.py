import tkinter as tk
from tkinter import ttk, messagebox

# ====================== TAB 1: THAY THẾ TRANG ======================

class PageReplacementTab:
    def __init__(self, parent):
        self.parent = parent

        # STATE
        self.frames = []
        self.ref_string = []
        self.current_index = 0
        self.hits = 0
        self.faults = 0
        self.algorithm = "FIFO"

        self.last_highlight_index = None
        self.last_is_hit = None

        # FIFO
        self.fifo_queue = []

        # LRU
        self.lru_last_used = {}

        # CLOCK
        self.clock_bits = []
        self.clock_pointer = 0

        self.build_ui()

    def build_ui(self):
        outer = ttk.Frame(self.parent)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Điều khiển
        control = ttk.LabelFrame(outer, text="Thay thế trang")
        control.pack(fill=tk.X)

        # Hàng 1
        ttk.Label(control, text="Số khung trang:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_frames = ttk.Entry(control, width=6)
        self.entry_frames.grid(row=0, column=1, padx=5, pady=5)
        self.entry_frames.insert(0, "3")

        ttk.Label(control, text="Thuật toán:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.combo_algo = ttk.Combobox(
            control,
            values=["FIFO", "LRU", "CLOCK"],
            state="readonly",
            width=10,
        )
        self.combo_algo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.combo_algo.current(0)

        # Hàng 2
        ttk.Label(control, text="Chuỗi tham chiếu:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_ref = ttk.Entry(control, width=50)
        self.entry_ref.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        self.entry_ref.insert(0, "1 2 3 2 4 1 5 2 4 5")

        # Hàng 3 – nút
        btn_frame = ttk.Frame(control)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(5, 8), sticky="e")

        self.btn_start = ttk.Button(btn_frame, text="Khởi động lại", command=self.start_simulation)
        self.btn_start.pack(side=tk.LEFT, padx=3)

        self.btn_step = ttk.Button(btn_frame, text="Bước tiếp ▶", command=self.next_step, state=tk.DISABLED)
        self.btn_step.pack(side=tk.LEFT, padx=3)

        # Trạng thái
        info = ttk.LabelFrame(outer, text="Trạng thái")
        info.pack(fill=tk.X, pady=(8, 5))

        self.label_step = ttk.Label(info, text="Bước: 0")
        self.label_step.grid(row=0, column=0, padx=5, pady=3, sticky="w")

        self.label_hits = ttk.Label(info, text="Hit: 0")
        self.label_hits.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        self.label_faults = ttk.Label(info, text="Fault: 0")
        self.label_faults.grid(row=0, column=2, padx=5, pady=3, sticky="w")

        self.label_ratio = ttk.Label(info, text="Tỉ lệ hit: 0.0%")
        self.label_ratio.grid(row=0, column=3, padx=5, pady=3, sticky="w")

        self.label_status = ttk.Label(info, text="Trạng thái: Chưa bắt đầu")
        self.label_status.grid(row=1, column=0, columnspan=4, padx=5, pady=(0, 5), sticky="w")

        # Canvas
        self.canvas = tk.Canvas(
            outer,
            bg="#020617",
            highlightthickness=1,
            highlightbackground="#1f2937",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.draw_empty_canvas()

    def draw_empty_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            10,
            10,
            anchor="nw",
            text="Khung trang sẽ hiển thị ở đây sau khi bấm 'Khởi động lại'.",
            font=("Segoe UI", 10),
            fill="#9ca3af",
        )

    def draw_frames(self):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 300:
            width = 300
        if height < 200:
            height = 200

        margin_left = 80
        margin_top = 40
        frame_width = 180
        frame_height = 40
        gap = 10

        self.canvas.create_text(
            20,
            10,
            text="Bộ nhớ (Frames)",
            font=("Segoe UI", 11, "bold"),
            anchor="nw",
            fill="#e5e7eb",
        )

        for i, page in enumerate(self.frames):
            x1 = margin_left
            y1 = margin_top + i * (frame_height + gap)
            x2 = x1 + frame_width
            y2 = y1 + frame_height

            fill_color = "#020617"
            outline_color = "#4b5563"
            text_color = "#e5e7eb"

            if self.last_highlight_index is not None and i == self.last_highlight_index:
                if self.last_is_hit:
                    fill_color = "#064e3b"   # hit – xanh đậm
                    outline_color = "#22c55e"
                else:
                    fill_color = "#450a0a"   # fault – đỏ đậm
                    outline_color = "#f87171"

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=outline_color,
                width=2,
                fill=fill_color,
            )

            frame_label = f"Frame {i}"
            self.canvas.create_text(
                x1 + 8,
                y1 + 10,
                anchor="w",
                text=frame_label,
                font=("Segoe UI", 9, "bold"),
                fill="#9ca3af",
            )

            page_text = "-" if page is None else str(page)
            self.canvas.create_text(
                x1 + frame_width / 2,
                y1 + frame_height / 2 + 5,
                anchor="center",
                text=page_text,
                font=("Segoe UI", 14, "bold"),
                fill=text_color,
            )

        # Vẽ chuỗi tham chiếu bên phải
        if self.ref_string:
            offset_x = margin_left + frame_width + 60
            self.canvas.create_text(
                offset_x,
                10,
                text="Chuỗi tham chiếu:",
                font=("Segoe UI", 10, "bold"),
                anchor="nw",
                fill="#e5e7eb",
            )
            ref_str = " ".join(str(x) for x in self.ref_string)
            self.canvas.create_text(
                offset_x,
                30,
                text=ref_str,
                font=("Segoe UI", 9),
                anchor="nw",
                fill="#9ca3af",
            )

            if 0 <= self.current_index < len(self.ref_string):
                prev = " ".join(str(x) for x in self.ref_string[: self.current_index])
                approx_width = len(prev) * 7
                self.canvas.create_polygon(
                    offset_x + approx_width + 4,
                    52,
                    offset_x + approx_width + 12,
                    52,
                    offset_x + approx_width + 8,
                    60,
                    fill="#2563eb",
                    outline="",
                )

    # ---------- Logic mô phỏng ----------

    def start_simulation(self):
        try:
            num_frames = int(self.entry_frames.get())
            if num_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số khung trang phải là số nguyên dương!")
            return

        ref_text = self.entry_ref.get().strip()
        if not ref_text:
            messagebox.showerror("Lỗi", "Chuỗi tham chiếu không được để trống!")
            return

        try:
            ref_list = [int(x) for x in ref_text.split()]
        except ValueError:
            messagebox.showerror("Lỗi", "Chuỗi tham chiếu chỉ chứa số nguyên, cách nhau bởi khoảng trắng!")
            return

        self.algorithm = self.combo_algo.get()
        self.frames = [None] * num_frames
        self.ref_string = ref_list
        self.current_index = 0
        self.hits = 0
        self.faults = 0
        self.last_highlight_index = None
        self.last_is_hit = None

        self.fifo_queue = []
        self.lru_last_used = {}
        self.clock_bits = [0] * num_frames
        self.clock_pointer = 0

        self.btn_step.config(state=tk.NORMAL)

        self.label_step.config(text=f"Bước: 0 / {len(self.ref_string)}")
        self.label_hits.config(text="Hit: 0")
        self.label_faults.config(text="Fault: 0")
        self.label_ratio.config(text="Tỉ lệ hit: 0.0%")
        self.update_info("Đã khởi tạo. Bấm 'Bước tiếp ▶' để chạy từng bước.")
        self.draw_frames()

    def next_step(self):
        if self.current_index >= len(self.ref_string):
            self.update_info("Đã hết chuỗi tham chiếu.")
            self.btn_step.config(state=tk.DISABLED)
            return

        current_page = self.ref_string[self.current_index]
        frame_index, is_hit = self.apply_algorithm(current_page)

        self.last_highlight_index = frame_index
        self.last_is_hit = is_hit

        if is_hit:
            self.hits += 1
        else:
            self.faults += 1

        self.current_index += 1

        self.label_step.config(text=f"Bước: {self.current_index} / {len(self.ref_string)}")
        self.label_hits.config(text=f"Hit: {self.hits}")
        self.label_faults.config(text=f"Fault: {self.faults}")

        total = self.hits + self.faults
        ratio = (self.hits / total) * 100 if total > 0 else 0.0
        self.label_ratio.config(text=f"Tỉ lệ hit: {ratio:.1f}%")

        status_text = f"Trang yêu cầu: {current_page} - "
        status_text += "HIT ✅" if is_hit else f"FAULT ❌, đưa vào frame {frame_index}"
        self.update_info(status_text)

        self.draw_frames()

        if self.current_index >= len(self.ref_string):
            self.btn_step.config(state=tk.DISABLED)
            self.update_info(status_text + " - ĐÃ HẾT CHUỖI.")

    def update_info(self, text):
        self.label_status.config(text="Trạng thái: " + text)

    def apply_algorithm(self, page):
        if self.algorithm == "FIFO":
            return self.algo_fifo(page)
        elif self.algorithm == "LRU":
            return self.algo_lru(page)
        elif self.algorithm == "CLOCK":
            return self.algo_clock(page)
        else:
            raise ValueError("Thuật toán không hợp lệ")

    # FIFO
    def algo_fifo(self, page):
        if page in self.frames:
            frame_index = self.frames.index(page)
            return frame_index, True

        if None in self.frames:
            empty_index = self.frames.index(None)
            self.frames[empty_index] = page
            self.fifo_queue.append(empty_index)
            return empty_index, False

        victim_index = self.fifo_queue.pop(0)
        self.frames[victim_index] = page
        self.fifo_queue.append(victim_index)
        return victim_index, False

    # LRU
    def algo_lru(self, page):
        step = self.current_index

        if page in self.frames:
            frame_index = self.frames.index(page)
            self.lru_last_used[page] = step
            return frame_index, True

        if None in self.frames:
            empty_index = self.frames.index(None)
            self.frames[empty_index] = page
            self.lru_last_used[page] = step
            return empty_index, False

        lru_page = min(self.lru_last_used, key=self.lru_last_used.get)
        victim_index = self.frames.index(lru_page)

        del self.lru_last_used[lru_page]
        self.frames[victim_index] = page
        self.lru_last_used[page] = step

        return victim_index, False

    # CLOCK
    def algo_clock(self, page):
        num_frames = len(self.frames)

        if page in self.frames:
            idx = self.frames.index(page)
            self.clock_bits[idx] = 1
            return idx, True

        if None in self.frames:
            empty_index = self.frames.index(None)
            self.frames[empty_index] = page
            self.clock_bits[empty_index] = 1
            return empty_index, False

        while True:
            idx = self.clock_pointer
            if self.clock_bits[idx] == 0:
                victim_index = idx
                self.frames[victim_index] = page
                self.clock_bits[victim_index] = 1
                self.clock_pointer = (victim_index + 1) % num_frames
                return victim_index, False
            else:
                self.clock_bits[idx] = 0
                self.clock_pointer = (idx + 1) % num_frames


# ====================== TAB 2: PHÂN TRANG (PAGE SIZE + SCROLL, VẼ TRỰC TIẾP CANVAS) ======================

class PagingTab:
    def __init__(self, parent):
        self.parent = parent
        self.page_table = []
        self.num_frames = 0
        self.page_size = 1024
        self.build_ui()

    def build_ui(self):
        outer = ttk.Frame(self.parent)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control = ttk.LabelFrame(outer, text="Phân trang")
        control.pack(fill=tk.X)

        # Hàng 1
        ttk.Label(control, text="Số trang (N):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_pages = ttk.Entry(control, width=6)
        self.entry_pages.grid(row=0, column=1, padx=5, pady=5)
        self.entry_pages.insert(0, "5")

        ttk.Label(control, text="Số khung:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_frames = ttk.Entry(control, width=6)
        self.entry_frames.grid(row=0, column=3, padx=5, pady=5)
        self.entry_frames.insert(0, "4")

        # Hàng 2: Page size
        ttk.Label(control, text="Kích thước trang (bytes):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_pagesize = ttk.Entry(control, width=10)
        self.entry_pagesize.grid(row=1, column=1, padx=5, pady=5)
        self.entry_pagesize.insert(0, "1024")

        # Hàng 3: Page table
        ttk.Label(control, text="Bảng trang (frame cho mỗi trang, -1 = không có):").grid(
            row=2, column=0, columnspan=4, padx=5, pady=5, sticky="w"
        )
        self.entry_table = ttk.Entry(control, width=60)
        self.entry_table.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        self.entry_table.insert(0, "0 2 1 -1 3")

        btn = ttk.Button(control, text="Vẽ bảng trang", command=self.draw_page_table)
        btn.grid(row=3, column=4, padx=5, pady=5)

        # Dịch địa chỉ
        trans = ttk.LabelFrame(outer, text="Dịch địa chỉ luận lý (page, offset)")
        trans.pack(fill=tk.X, pady=(8, 5))

        ttk.Label(trans, text="Trang (p):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_p = ttk.Entry(trans, width=6)
        self.entry_p.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(trans, text="Offset (d):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_d = ttk.Entry(trans, width=10)
        self.entry_d.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(trans, text="Dịch địa chỉ", command=self.translate_address).grid(row=0, column=4, padx=5, pady=5)

        self.label_result = ttk.Label(trans, text="Địa chỉ vật lý: ?")
        self.label_result.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="w")

        # Canvas + scrollbar
        canvas_frame = ttk.Frame(outer)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#020617",
            highlightthickness=1,
            highlightbackground="#1f2937",
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Hướng dẫn ban đầu
        self.canvas.create_text(
            10,
            10,
            anchor="nw",
            text="Nhập bảng trang và kích thước trang, sau đó nhấn 'Vẽ bảng trang'.",
            font=("Segoe UI", 10),
            fill="#9ca3af",
        )

    def draw_page_table(self):
        try:
            n = int(self.entry_pages.get())
            f = int(self.entry_frames.get())
            ps = int(self.entry_pagesize.get())
            if n <= 0 or f <= 0 or ps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số trang / số khung / page size phải là số nguyên dương!")
            return

        arr = self.entry_table.get().strip().split()
        if len(arr) != n:
            messagebox.showerror("Lỗi", f"Bảng trang phải có đúng {n} số!")
            return

        try:
            self.page_table = [int(x) for x in arr]
        except:
            messagebox.showerror("Lỗi", "Bảng trang phải là số nguyên!")
            return

        self.num_frames = f
        self.page_size = ps

        self.canvas.delete("all")

        margin_left = 40
        row_h = 35
        col_w = 80

        # Đặt scrollregion theo số dòng
        total_height = 40 + max(len(self.page_table), self.num_frames) * row_h + 40
        self.canvas.config(scrollregion=(0, 0, 600, total_height))

        # Header
        self.canvas.create_text(
            margin_left,
            10,
            text="Trang",
            font=("Segoe UI", 10, "bold"),
            fill="#e5e7eb",
            anchor="w",
        )
        self.canvas.create_text(
            margin_left + col_w + 40,
            10,
            text="Khung",
            font=("Segoe UI", 10, "bold"),
            fill="#e5e7eb",
            anchor="w",
        )

        # Bảng trang
        for i, frame in enumerate(self.page_table):
            y = 40 + i * row_h

            # ô trang
            self.canvas.create_rectangle(
                margin_left,
                y,
                margin_left + col_w,
                y + row_h,
                outline="#4b5563",
                width=1,
                fill="#020617",
            )
            self.canvas.create_text(
                margin_left + col_w / 2,
                y + row_h / 2,
                text=str(i),
                font=("Segoe UI", 11),
                fill="#e5e7eb",
            )

            # ô khung
            self.canvas.create_rectangle(
                margin_left + col_w,
                y,
                margin_left + 2 * col_w,
                y + row_h,
                outline="#4b5563",
                width=1,
                fill="#020617",
            )
            txt = "-" if frame < 0 else str(frame)
            color = "#9ca3af" if frame < 0 else "#22c55e"
            self.canvas.create_text(
                margin_left + col_w + col_w / 2,
                y + row_h / 2,
                text=txt,
                font=("Segoe UI", 11, "bold"),
                fill=color,
            )

        # Khung vật lý
        start_x = margin_left + 2 * col_w + 60
        self.canvas.create_text(
            start_x,
            10,
            text="Frame",
            font=("Segoe UI", 10, "bold"),
            fill="#e5e7eb",
            anchor="w",
        )

        for j in range(self.num_frames):
            y = 40 + j * row_h
            self.canvas.create_rectangle(
                start_x,
                y,
                start_x + col_w,
                y + row_h,
                outline="#4b5563",
                width=1,
                fill="#020617",
            )
            self.canvas.create_text(
                start_x + col_w / 2,
                y + row_h / 2,
                text=f"F{j}",
                font=("Segoe UI", 11),
                fill="#e5e7eb",
            )

        # Vẽ mũi tên page -> frame
        for i, frame in enumerate(self.page_table):
            if frame < 0 or frame >= self.num_frames:
                continue
            y_page = 40 + i * row_h + row_h / 2
            y_frame = 40 + frame * row_h + row_h / 2
            x_page = margin_left + 2 * col_w
            x_frame = start_x

            self.canvas.create_line(
                x_page,
                y_page,
                x_frame,
                y_frame,
                fill="#22c55e",
                width=1.5,
                arrow=tk.LAST,
            )

    def translate_address(self):
        if not self.page_table:
            messagebox.showwarning("Chú ý", "Hãy vẽ bảng trang trước.")
            return

        try:
            p = int(self.entry_p.get())
            d = int(self.entry_d.get())
        except:
            messagebox.showerror("Lỗi", "Trang và offset phải là số nguyên!")
            return

        if p < 0 or p >= len(self.page_table):
            self.label_result.config(text="Địa chỉ vật lý: trang không hợp lệ.")
            return

        frame = self.page_table[p]
        if frame < 0:
            self.label_result.config(text="Page fault: trang chưa nằm trong khung.")
            return

        if d < 0 or d >= self.page_size:
            self.label_result.config(text=f"Offset phải nằm trong [0, {self.page_size - 1}]")
            return

        phys_addr = frame * self.page_size + d

        self.label_result.config(
            text=f"Địa chỉ vật lý = frame({frame}) * {self.page_size} + {d} = {phys_addr}"
        )


# ====================== TAB 3: PHÂN ĐOẠN ======================

class SegmentationTab:
    def __init__(self, parent):
        self.parent = parent
        self.segments = []   # list of (base, limit)
        self.last_seg_index = None
        self.build_ui()

    def build_ui(self):
        outer = ttk.Frame(self.parent)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control = ttk.LabelFrame(outer, text="Phân đoạn")
        control.pack(fill=tk.X)

        ttk.Label(
            control,
            text="Danh sách đoạn (base-limit; base-limit; ...):",
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_segments = ttk.Entry(control, width=70)
        self.entry_segments.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        self.entry_segments.insert(0, "0-100; 200-350; 400-500")

        btn_draw = ttk.Button(control, text="Vẽ các đoạn", command=self.draw_segments)
        btn_draw.grid(row=1, column=4, padx=5, pady=5, sticky="e")

        trans = ttk.LabelFrame(outer, text="Dịch địa chỉ luận lý (segment, offset)")
        trans.pack(fill=tk.X, pady=(8, 5))

        ttk.Label(trans, text="Segment (s):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_s = ttk.Entry(trans, width=6)
        self.entry_s.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(trans, text="Offset:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_off = ttk.Entry(trans, width=10)
        self.entry_off.grid(row=0, column=3, padx=5, pady=5)

        btn_trans = ttk.Button(trans, text="Dịch địa chỉ", command=self.translate)
        btn_trans.grid(row=0, column=4, padx=5, pady=5)

        self.label_result = ttk.Label(trans, text="Địa chỉ vật lý: ?")
        self.label_result.grid(row=1, column=0, columnspan=5, padx=5, pady=(0, 5), sticky="w")

        self.canvas = tk.Canvas(
            outer,
            bg="#020617",
            highlightthickness=1,
            highlightbackground="#1f2937",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.canvas.create_text(
            10,
            10,
            anchor="nw",
            text="Nhập danh sách đoạn rồi bấm 'Vẽ các đoạn' để hiển thị bộ nhớ.",
            font=("Segoe UI", 10),
            fill="#9ca3af",
        )

    def parse_segments(self):
        text = self.entry_segments.get().strip()
        if not text:
            messagebox.showerror("Lỗi", "Danh sách đoạn không được để trống!")
            return None
        segs = []
        try:
            parts = [p.strip() for p in text.split(";") if p.strip()]
            for p in parts:
                base_str, limit_str = p.split("-")
                base = int(base_str.strip())
                limit = int(limit_str.strip())
                if limit <= 0:
                    raise ValueError
                segs.append((base, limit))
        except Exception:
            messagebox.showerror("Lỗi", "Định dạng sai. Ví dụ: 0-100; 200-350; 400-500")
            return None
        return segs

    def draw_segments(self):
        segs = self.parse_segments()
        if segs is None:
            return
        self.segments = segs
        self.last_seg_index = None

        self.canvas.delete("all")

        if not self.segments:
            return

        max_addr = max(base + limit for base, limit in self.segments)
        if max_addr == 0:
            max_addr = 1

        margin_top = 20
        margin_bottom = 20
        margin_left = 80
        bar_width = 60

        height = self.canvas.winfo_height()
        if height < 200:
            height = 300

        total_h = height - margin_top - margin_bottom

        self.canvas.create_text(
            margin_left - 40,
            margin_top,
            text="0",
            font=("Segoe UI", 9),
            fill="#9ca3af",
            anchor="w",
        )
        self.canvas.create_text(
            margin_left - 40,
            margin_top + total_h,
            text=str(max_addr),
            font=("Segoe UI", 9),
            fill="#9ca3af",
            anchor="w",
        )

        self.canvas.create_rectangle(
            margin_left,
            margin_top,
            margin_left + bar_width,
            margin_top + total_h,
            outline="#4b5563",
            width=2,
            fill="#020617",
        )

        for idx, (base, limit) in enumerate(self.segments):
            start_y = margin_top + (base / max_addr) * total_h
            end_y = margin_top + ((base + limit) / max_addr) * total_h

            fill_color = "#0f172a"
            outline_color = "#38bdf8"
            if self.last_seg_index is not None and idx == self.last_seg_index:
                fill_color = "#1e293b"
                outline_color = "#22c55e"

            self.canvas.create_rectangle(
                margin_left + 2,
                start_y,
                margin_left + bar_width - 2,
                end_y,
                outline=outline_color,
                width=2,
                fill=fill_color,
            )

            self.canvas.create_text(
                margin_left + bar_width + 10,
                (start_y + end_y) / 2,
                text=f"S{idx}\n[{base}, {base+limit})",
                font=("Segoe UI", 9),
                fill="#e5e7eb",
                anchor="w",
            )

    def translate(self):
        if not self.segments:
            messagebox.showwarning("Chú ý", "Hãy vẽ các đoạn trước.")
            return
        try:
            s = int(self.entry_s.get())
            off = int(self.entry_off.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Segment và offset phải là số nguyên!")
            return

        if s < 0 or s >= len(self.segments):
            self.label_result.config(text="Địa chỉ vật lý: segment ngoài phạm vi.")
            return

        base, limit = self.segments[s]
        if off < 0 or off >= limit:
            self.label_result.config(text="Địa chỉ vật lý: lỗi (offset vượt quá limit của đoạn).")
            return

        phys = base + off
        self.last_seg_index = s
        self.label_result.config(
            text=f"Địa chỉ vật lý: base={base}, offset={off} → {phys}"
        )
        self.draw_segments()


# ====================== APP CHÍNH (DARK MODE) ======================

class MemoryVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trực quan hóa quản lý bộ nhớ - Dark Mode")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        self.setup_style()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)

        notebook.add(tab1, text="Thay thế trang")
        notebook.add(tab2, text="Phân trang")
        notebook.add(tab3, text="Phân đoạn")

        PageReplacementTab(tab1)
        PagingTab(tab2)
        SegmentationTab(tab3)

    def setup_style(self):
        self.root.configure(bg="#020617")
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(".", background="#020617", foreground="#e5e7eb", fieldbackground="#020617")
        style.configure("TLabel", background="#020617", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("TFrame", background="#020617")
        style.configure("TLabelframe", background="#020617", foreground="#e5e7eb", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#020617", foreground="#e5e7eb")
        style.configure("TEntry", fieldbackground="#020617", foreground="#e5e7eb", insertcolor="#e5e7eb")
        style.configure("TButton", background="#0f172a", foreground="#e5e7eb", padding=5)
        style.map("TButton", background=[("active", "#111827")])
        style.configure("TNotebook", background="#020617", borderwidth=0)
        style.configure("TNotebook.Tab", background="#020617", foreground="#9ca3af", padding=(10, 5))
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#111827")],
            foreground=[("selected", "#e5e7eb")],
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryVisualizerApp(root)
    root.mainloop()
