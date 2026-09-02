import os
import random
import tkinter as tk
from tkinter import ttk, font as tkfont
import pygame
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

BG_DARK = "#1b1035"
BG_PANEL = "#241448"
ACCENT = "#8a5cf6"
ACCENT_HOVER = "#a480ff"
ACCENT_SOFT = "#3a2166"
TEXT_LIGHT = "#f5f2ff"
TEXT_MUTED = "#b9aee0"
DANGER = "#ef4b6b"
SUCCESS = "#3ddc97"
GOLD = "#f5c144"

FONT_TITLE = ("Georgia", 34, "bold")
FONT_SUBTITLE = ("Segoe UI", 13)
FONT_BUTTON = ("Segoe UI", 14, "bold")
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_SMALL = ("Segoe UI", 10)

PALETTE = [
    "#f2b6c6", "#b8dcf2", "#bdeecb", "#f4e2a0", "#d7c0f2",
    "#f6c39a", "#a9e6de", "#e8b6e2",
]

DIFFICULTIES = {
    "Easy":   {"n": 6, "time_limit": 600, "base_score": 1000},
    "Medium": {"n": 7, "time_limit": 420, "base_score": 1500},
    "Hard":   {"n": 8, "time_limit": 300, "base_score": 2000},
}
MAX_HINTS = 3
SCORE_TIME_FACTOR = 1.2
SCORE_HINT_PENALTY = 120

NIVEAU_SEEDS = {}
for diff in DIFFICULTIES:
    for lvl in (1, 2, 3):
        NIVEAU_SEEDS[(diff, lvl)] = hash((diff, lvl)) % 100000


# PUZZLE GENERATION
def generate_solution(n, rnd):
    solution = [-1] * n
    used_cols = set()

    def backtrack(row):
        if row == n:
            return True
        candidates = [c for c in range(n) if c not in used_cols]
        rnd.shuffle(candidates)
        for c in candidates:
            if row > 0 and abs(c - solution[row - 1]) <= 1:
                continue
            solution[row] = c
            used_cols.add(c)
            if backtrack(row + 1):
                return True
            used_cols.discard(c)
            solution[row] = -1
        return False

    backtrack(0)
    return solution


def grow_regions(n, solution, rnd):
    """Randomly grow N connected regions, one seeded at each queen cell."""
    regions = [[-1] * n for _ in range(n)]
    for i, c in enumerate(solution):
        regions[i][c] = i

    frontier = []

    def add_neighbors(reg, r, c):
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and regions[nr][nc] == -1:
                frontier.append((reg, nr, nc))

    for i, c in enumerate(solution):
        add_neighbors(i, i, c)

    assigned = n
    total = n * n
    while assigned < total and frontier:
        idx = rnd.randrange(len(frontier))
        reg, r, c = frontier.pop(idx)
        if regions[r][c] == -1:
            regions[r][c] = reg
            assigned += 1
            add_neighbors(reg, r, c)

    return regions


def count_solutions(regions, n, cap=2):
    count = 0
    cols_used = [False] * n
    region_used = [False] * n
    placed_cols = [-1] * n

    def backtrack(row):
        nonlocal count
        if count >= cap:
            return
        if row == n:
            count += 1
            return
        for c in range(n):
            if cols_used[c]:
                continue
            reg = regions[row][c]
            if region_used[reg]:
                continue
            if row > 0:
                pc = placed_cols[row - 1]
                if pc != -1 and abs(pc - c) <= 1:
                    continue
            cols_used[c] = True
            region_used[reg] = True
            placed_cols[row] = c
            backtrack(row + 1)
            cols_used[c] = False
            region_used[reg] = False
            placed_cols[row] = -1
            if count >= cap:
                return

    backtrack(0)
    return count


def generate_puzzle(n, seed):
    rnd = random.Random(seed)
    regions, solution = None, None
    for _ in range(400):
        solution = generate_solution(n, rnd)
        regions = grow_regions(n, solution, rnd)
        if count_solutions(regions, n, cap=2) == 1:
            return regions, solution
    return regions, solution


def find_conflicts(board, regions, n):
    queens = [(r, c) for r in range(n) for c in range(n) if board[r][c] == "Q"]
    conflict_cells = set()
    row_count, col_count, reg_count = {}, {}, {}
    for (r, c) in queens:
        row_count[r] = row_count.get(r, 0) + 1
        col_count[c] = col_count.get(c, 0) + 1
        reg = regions[r][c]
        reg_count[reg] = reg_count.get(reg, 0) + 1
    for (r, c) in queens:
        reg = regions[r][c]
        if row_count[r] > 1 or col_count[c] > 1 or reg_count[reg] > 1:
            conflict_cells.add((r, c))
    for i, (r1, c1) in enumerate(queens):
        for (r2, c2) in queens[i + 1:]:
            if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                conflict_cells.add((r1, c1))
                conflict_cells.add((r2, c2))
    return conflict_cells


# 
# IMAGE HELPER
def load_image(path, max_size=(320, 320)):
    if not os.path.exists(path):
        return None
    try:
        if PIL_AVAILABLE:
            img = Image.open(path)
            img.thumbnail(max_size)
            return ImageTk.PhotoImage(img)
        else:
            return tk.PhotoImage(file=path)
    except Exception:
        return None

# 
# WIDGET HELPERS
def make_button(parent, text, command, bg=ACCENT, fg=TEXT_LIGHT, hover=ACCENT_HOVER,
                 font=FONT_BUTTON, padx=18, pady=10, state="normal"):
    btn = tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg, font=font,
        activebackground=hover, activeforeground=fg, relief="flat",
        cursor="hand2", padx=padx, pady=pady, bd=0, state=state,
        disabledforeground="#7a7a8c",
    )

    def on_enter(_e):
        if btn["state"] != "disabled":
            btn.configure(bg=hover)

    def on_leave(_e):
        if btn["state"] != "disabled":
            btn.configure(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


# MAIN APPLICATION
class QueensApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("\u265B Queens Puzzle")
        self.geometry("1000x760")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)


        # Music setup
        pygame.mixer.init()

        self.music_playing = True
        self.music_path = os.path.join(ASSETS_DIR, "music.mp3")

        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)  # loop forever




        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True)

        self.menu_frame = MenuFrame(self.container, self)
        self.instructions_frame = InstructionsFrame(self.container, self)
        self.level_frame = None
        self.game_frame = None

        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.instructions_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_menu()

    # navigation
    def show_menu(self):
        self._stop_game_timer()
        self.menu_frame.lift()

    def show_instructions(self):
        self.instructions_frame.lift()

    def show_level_select(self, difficulty):
        if self.level_frame is not None:
            self.level_frame.destroy()
        self.level_frame = LevelFrame(self.container, self, difficulty)
        self.level_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.level_frame.lift()

    def start_game(self, difficulty, niveau):
        self._stop_game_timer()
        if self.game_frame is not None:
            self.game_frame.destroy()
        self.game_frame = GameFrame(self.container, self, difficulty, niveau)
        self.game_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.game_frame.lift()

    def _stop_game_timer(self):
        if self.game_frame is not None:
            self.game_frame.stop_timer()
    
    #mute/ unmute music
    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
            self.music_button.config(text="🔇 Music")
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            self.music_button.config(text="🔊 Music")


# MENU FRAME

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        wrap = tk.Frame(self, bg=BG_DARK)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrap, text="\u265B  QUEENS PUZZLE", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(0, 6))
        tk.Label(wrap, text="One queen per row, column & color \u2014 and none may touch.",
                 font=FONT_SUBTITLE, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=(0, 40))

        card = tk.Frame(wrap, bg=BG_PANEL, padx=40, pady=36)
        card.pack()

        tk.Label(card, text="Choose a difficulty", font=FONT_LABEL,
                 bg=BG_PANEL, fg=TEXT_LIGHT).pack(pady=(0, 18))

        colors = {"Easy": SUCCESS, "Medium": GOLD, "Hard": DANGER}
        for diff in ("Easy", "Medium", "Hard"):
            b = make_button(card, f"{diff}  \u2022  {DIFFICULTIES[diff]['n']}x{DIFFICULTIES[diff]['n']} board",
                             lambda d=diff: controller.show_level_select(d),
                             bg=colors[diff], hover=colors[diff], fg="#1b1035")
            b.pack(fill="x", pady=8, ipadx=10)

        tk.Frame(card, bg=BG_PANEL, height=14).pack()
        make_button(card, "How to Play", controller.show_instructions,
                    bg=ACCENT_SOFT, hover=ACCENT).pack(fill="x", pady=(10, 0))

        tk.Label(wrap, text="Made for you \u2764", font=FONT_SMALL,
                 bg=BG_DARK, fg=TEXT_MUTED).pack(pady=(24, 0))
        
        controller.music_button = make_button(
            card,
            "🔊 Music",
            controller.toggle_music,
            bg=ACCENT_SOFT,
            hover=ACCENT
        )

        controller.music_button.pack(fill="x", pady=8)

# INSTRUCTIONS FRAME

class InstructionsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        wrap = tk.Frame(self, bg=BG_DARK)
        wrap.place(relx=0.5, rely=0.5, anchor="center", width=760)

        tk.Label(wrap, text="How to Play", font=("Georgia", 26, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(0, 18))

        card = tk.Frame(wrap, bg=BG_PANEL, padx=30, pady=26)
        card.pack(fill="both")

        rules = [
            ("\U0001F451", "Goal", "Place exactly one Queen in every row, every column "
                                    "and every colored region of the board."),
            ("\u2716\uFE0F", "No touching", "Two queens can never touch each other \u2014 "
                                            "not horizontally, vertically, or diagonally."),
            ("\U0001F5B1\uFE0F", "Left click", "Place or remove a Queen on a cell."),
            ("\U0001F5B1\uFE0F", "Right click", "Mark or unmark a cell with an X, "
                                                 "to remind yourself it can't hold a queen."),
            ("\U0001F4A1", "Hints", f"You get {MAX_HINTS} hints per puzzle. Each hint reveals "
                                     "one correctly placed queen, but costs points."),
            ("\u21A9\uFE0F", "Undo", "Step back through your last moves one at a time."),
            ("\U0001F9F9", "Clear", "Wipe the board clean and try the same puzzle again."),
            ("\U0001F504", "New Puzzle", "Start a brand new puzzle of the same difficulty."),
            ("\u23F1\uFE0F", "Timer", "Solve the puzzle before time runs out, or it's game over!"),
        ]
        for icon, title, text in rules:
            row = tk.Frame(card, bg=BG_PANEL)
            row.pack(fill="x", pady=7, anchor="w")
            tk.Label(row, text=icon, font=("Segoe UI Emoji", 16), bg=BG_PANEL,
                     fg=TEXT_LIGHT, width=3).pack(side="left", anchor="n")
            textcol = tk.Frame(row, bg=BG_PANEL)
            textcol.pack(side="left", fill="x")
            tk.Label(textcol, text=title, font=FONT_LABEL, bg=BG_PANEL,
                     fg=GOLD, anchor="w", justify="left").pack(anchor="w")
            tk.Label(textcol, text=text, font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_MUTED,
                     wraplength=600, justify="left", anchor="w").pack(anchor="w")

        make_button(wrap, "\u2190 Back to Menu", controller.show_menu,
                    bg=ACCENT, hover=ACCENT_HOVER).pack(pady=(20, 0))


# LEVEL SELECT FRAME (scrollable list of 3 niveaus)

class LevelFrame(tk.Frame):
    def __init__(self, parent, controller, difficulty):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.difficulty = difficulty
        info = DIFFICULTIES[difficulty]

        wrap = tk.Frame(self, bg=BG_DARK)
        wrap.place(relx=0.5, rely=0.5, anchor="center", width=700, height=600)

        tk.Label(wrap, text=f"{difficulty} Mode", font=("Georgia", 26, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(0, 4))
        tk.Label(wrap, text=f"{info['n']}x{info['n']} board  \u2022  "
                             f"{info['time_limit'] // 60} min time limit",
                 font=FONT_SUBTITLE, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=(0, 20))

        # Scrollable area
        outer = tk.Frame(wrap, bg=BG_PANEL)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG_PANEL, highlightthickness=0, height=380)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG_PANEL)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=650)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        descriptions = {
            1: "A gentle warm-up puzzle to get comfortable with the rules.",
            2: "A balanced challenge with a bit more region twisting.",
            3: "The trickiest layout of this difficulty \u2014 for sharp minds!",
        }
        stars = {1: "\u2605\u2606\u2606", 2: "\u2605\u2605\u2606", 3: "\u2605\u2605\u2605"}

        for lvl in (1, 2, 3):
            card = tk.Frame(inner, bg=ACCENT_SOFT, padx=20, pady=16)
            card.pack(fill="x", pady=10, padx=10)

            top = tk.Frame(card, bg=ACCENT_SOFT)
            top.pack(fill="x")
            tk.Label(top, text=f"Niveau {lvl}", font=FONT_LABEL,
                     bg=ACCENT_SOFT, fg=TEXT_LIGHT).pack(side="left")
            tk.Label(top, text=stars[lvl], font=FONT_LABEL,
                     bg=ACCENT_SOFT, fg=GOLD).pack(side="right")

            tk.Label(card, text=descriptions[lvl], font=FONT_SMALL, bg=ACCENT_SOFT,
                     fg=TEXT_MUTED, wraplength=480, justify="left").pack(
                anchor="w", pady=(6, 12))

            make_button(card, "Play", lambda l=lvl: controller.start_game(difficulty, l),
                        bg=ACCENT, hover=ACCENT_HOVER, padx=14, pady=6,
                        font=("Segoe UI", 12, "bold")).pack(anchor="e")

        make_button(wrap, "\u2190 Back", controller.show_menu,
                    bg=BG_PANEL, hover=ACCENT_SOFT).pack(pady=(16, 0))



# GAME FRAME

class GameFrame(tk.Frame):
    def __init__(self, parent, controller, difficulty, niveau):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller
        self.difficulty = difficulty
        self.niveau = niveau

        info = DIFFICULTIES[difficulty]
        self.n = info["n"]
        self.time_limit = info["time_limit"]
        self.base_score = info["base_score"]

        self.cell_size = {6: 62, 7: 56, 8: 50}[self.n]
        self.origin_x = 30
        self.origin_y = 30

        self.seed = NIVEAU_SEEDS[(difficulty, niveau)]
        self.regions, self.solution = generate_puzzle(self.n, self.seed)
        self.board = [["" for _ in range(self.n)] for _ in range(self.n)]

        self.move_stack = []
        self.hints_used = 0
        self.remaining = self.time_limit
        self.timer_id = None
        self.game_over = False
        self._popup_images = []

        self._build_ui()
        self.draw_board()
        self.start_timer()

    # UI
    def _build_ui(self):
        top = tk.Frame(self, bg=BG_DARK)
        top.pack(fill="x", padx=24, pady=(18, 6))

        tk.Label(top, text=f"\u265B {self.difficulty} \u2022 Niveau {self.niveau}",
                 font=("Georgia", 18, "bold"), bg=BG_DARK, fg=TEXT_LIGHT).pack(side="left")

        make_button(top, "\u2190 Menu", self.controller.show_menu, bg=BG_PANEL,
                    hover=ACCENT_SOFT, font=("Segoe UI", 11, "bold"),
                    padx=12, pady=6).pack(side="right")
        make_button(top, "\u2753 Instructions", self.controller.show_instructions,
                    bg=BG_PANEL, hover=ACCENT_SOFT, font=("Segoe UI", 11, "bold"),
                    padx=12, pady=6).pack(side="right", padx=8)
        
        self.music_btn = make_button(
            top,
            "🔊 Music",
            self.controller.toggle_music,
            bg=BG_PANEL,
            hover=ACCENT_SOFT,
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=6
        )

        self.music_btn.pack(side="right", padx=8)

        stats = tk.Frame(self, bg=BG_DARK)
        stats.pack(fill="x", padx=24, pady=(0, 10))

        self.timer_label = tk.Label(stats, text="", font=("Segoe UI", 15, "bold"),
                                     bg=BG_PANEL, fg=TEXT_LIGHT, padx=16, pady=8)
        self.timer_label.pack(side="left")

        self.score_label = tk.Label(stats, text="", font=("Segoe UI", 15, "bold"),
                                 bg=BG_PANEL, fg=GOLD, padx=16, pady=8)
        self.score_label.pack(side="left", padx=10)

        self.hints_label = tk.Label(stats, text="", font=("Segoe UI", 15, "bold"),
                                     bg=BG_PANEL, fg=TEXT_LIGHT, padx=16, pady=8)
        self.hints_label.pack(side="left")

        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=24, pady=6)

        board_wrap = tk.Frame(body, bg=BG_DARK)
        board_wrap.pack(side="left", padx=(0, 24))

        canvas_size = self.origin_x * 2 + self.cell_size * self.n
        self.canvas = tk.Canvas(board_wrap, width=canvas_size, height=canvas_size,
                                 bg=BG_DARK, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.status_label = tk.Label(board_wrap, text="Place your queens!",
                                      font=FONT_SUBTITLE, bg=BG_DARK, fg=TEXT_MUTED)
        self.status_label.pack(pady=(10, 0))

        side = tk.Frame(body, bg=BG_PANEL, padx=20, pady=20)
        side.pack(side="left", fill="y")

        tk.Label(side, text="Controls", font=FONT_LABEL, bg=BG_PANEL,
                 fg=TEXT_LIGHT).pack(pady=(0, 14))

        self.hint_btn = make_button(side, "\U0001F4A1 Hint", self.use_hint,
                                     bg=GOLD, hover="#ffd670", fg="#1b1035")
        self.hint_btn.pack(fill="x", pady=6)

        self.undo_btn = make_button(side, "\u21A9\uFE0F Undo", self.undo_move,
                                     bg=ACCENT_SOFT, hover=ACCENT)
        self.undo_btn.pack(fill="x", pady=6)

        make_button(side, "\U0001F9F9 Clear Board", self.clear_board,
                    bg=ACCENT_SOFT, hover=ACCENT).pack(fill="x", pady=6)

        make_button(side, "\U0001F504 New Puzzle", self.new_puzzle,
                    bg=ACCENT_SOFT, hover=ACCENT).pack(fill="x", pady=6)
        
        make_button(side, "✅ Check Board", self.check_board, 
                    bg=SUCCESS, hover=SUCCESS, fg="#1b1035").pack(fill="x", pady=6)



        tk.Frame(side, bg=BG_PANEL, height=10).pack()
        legend = tk.Label(
            side,
            text="Left click: place/remove Queen\nRight click: mark/unmark X",
            font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_MUTED, justify="left"
        )
        legend.pack(anchor="w", pady=(10, 0))

        self._refresh_side_panel()

    def _refresh_side_panel(self):
        self.hints_label.config(text=f"\U0001F4A1 {self.hints_used}/{MAX_HINTS}")
        self.hint_btn.config(state=("disabled" if self.hints_used >= MAX_HINTS else "normal"))
        self.undo_btn.config(state=("disabled" if not self.move_stack else "normal"))
        self._update_score_preview()

    def _update_score_preview(self):
        used_time = self.time_limit - self.remaining
        score = self.base_score - used_time * SCORE_TIME_FACTOR - self.hints_used * SCORE_HINT_PENALTY
        score = max(0, int(score))
        self.score_label.config(text=f"\U0001F3C6 {score}")
        return score

    # drawing
    def draw_board(self):
        c = self.canvas
        c.delete("all")
        n, cs = self.n, self.cell_size
        ox, oy = self.origin_x, self.origin_y

        for r in range(n):
            for col in range(n):
                x0, y0 = ox + col * cs, oy + r * cs
                x1, y1 = x0 + cs, y0 + cs
                color = PALETTE[self.regions[r][col] % len(PALETTE)]
                c.create_rectangle(x0, y0, x1, y1, fill=color, outline="#ffffff", width=1)

        for r in range(n):
            for col in range(n):
                reg = self.regions[r][col]
                x0, y0 = ox + col * cs, oy + r * cs
                x1, y1 = x0 + cs, y0 + cs
                if r == 0 or self.regions[r - 1][col] != reg:
                    c.create_line(x0, y0, x1, y0, fill="#2b2b2b", width=3)
                if r == n - 1 or self.regions[r + 1][col] != reg:
                    c.create_line(x0, y1, x1, y1, fill="#2b2b2b", width=3)
                if col == 0 or self.regions[r][col - 1] != reg:
                    c.create_line(x0, y0, x0, y1, fill="#2b2b2b", width=3)
                if col == n - 1 or self.regions[r][col + 1] != reg:
                    c.create_line(x1, y0, x1, y1, fill="#2b2b2b", width=3)

        c.create_rectangle(ox, oy, ox + n * cs, oy + n * cs, outline="#111111", width=4)

        conflicts = find_conflicts(self.board, self.regions, n)
        for r in range(n):
            for col in range(n):
                val = self.board[r][col]
                cx, cy = ox + col * cs + cs / 2, oy + r * cs + cs / 2
                if val == "Q":
                    color = DANGER if (r, col) in conflicts else "#1a1a1a"
                    c.create_text(cx, cy, text="\u265B",
                                   font=("Segoe UI Symbol", int(cs * 0.55)), fill=color)
                elif val == "X":
                    c.create_text(cx, cy, text="\u2715",
                                   font=("Segoe UI", int(cs * 0.4)), fill="#555555")

        self._refresh_side_panel()

    def _cell_from_event(self, event):
        n, cs = self.n, self.cell_size
        col = (event.x - self.origin_x) // cs
        row = (event.y - self.origin_y) // cs
        if 0 <= row < n and 0 <= col < n:
            return int(row), int(col)
        return None

    def on_left_click(self, event):
        if self.game_over:
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        prev = self.board[r][c]
        new = "" if prev == "Q" else "Q"
        self._apply_move(r, c, prev, new)
        self.draw_board()
        self.check_win()

    def on_right_click(self, event):
        if self.game_over:
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        prev = self.board[r][c]
        new = "" if prev == "X" else "X"
        self._apply_move(r, c, prev, new)
        self.draw_board()

    def _apply_move(self, r, c, prev, new):
        self.board[r][c] = new
        self.move_stack.append((r, c, prev, new))

    #actions
    def use_hint(self):
        if self.game_over or self.hints_used >= MAX_HINTS:
            return
        candidate_rows = [r for r in range(self.n) if self.board[r][self.solution[r]] != "Q"]
        if not candidate_rows:
            return
        r = random.choice(candidate_rows)
        c = self.solution[r]
        prev = self.board[r][c]
        self._apply_move(r, c, prev, "Q")
        self.hints_used += 1
        self.status_label.config(text="Hint used \u2014 a correct queen was revealed.",
                                  fg=GOLD)
        self.draw_board()
        self.check_win()

    #Check if the board is valid and update the status label accordingly
    def check_board(self):
        # Count placed queens
        queens = sum(
            1
            for r in range(self.n)
            for c in range(self.n)
            if self.board[r][c] == "Q"
        )

        conflicts = find_conflicts(
            self.board,
            self.regions,
            self.n
        )

        # Empty board
        if queens == 0:
            self.status_label.config(
                text="⚠️ Your board is empty. Place some queens first!",
                fg=GOLD
            )

        # Only X marks or not enough queens
        elif queens < self.n:
            if conflicts:
                self.status_label.config(
                   text=f"❌ There are {len(conflicts)} queen conflicts. Check your moves!",
                   fg=DANGER
                )
                self.draw_board()
            else:
                self.status_label.config(
                   text="✅ Perfect! Your solution is correct so far!",
                   fg=SUCCESS
                )

        # Full board
        else:
            if conflicts:
                self.status_label.config(
                    text=f"❌ There are {len(conflicts)} queen conflicts. Check your moves!",
                    fg=DANGER
                )
                self.draw_board()
            else:
                self.status_label.config(
                    text="🎉 Perfect! Your solution is correct!",
                    fg=SUCCESS
                )



    def undo_move(self):
        if self.game_over or not self.move_stack:
            return
        r, c, prev, _new = self.move_stack.pop()
        self.board[r][c] = prev
        self.status_label.config(text="Move undone.", fg=TEXT_MUTED)
        self.draw_board()

    def clear_board(self):
        if self.game_over:
            return
        self.board = [["" for _ in range(self.n)] for _ in range(self.n)]
        self.move_stack.clear()
        self.status_label.config(text="Board cleared \u2014 same puzzle, fresh start.",
                                  fg=TEXT_MUTED)
        self.draw_board()

    def new_puzzle(self):
        self.stop_timer()
        self.seed = random.randint(0, 999999)
        self.regions, self.solution = generate_puzzle(self.n, self.seed)
        self.board = [["" for _ in range(self.n)] for _ in range(self.n)]
        self.move_stack.clear()
        self.hints_used = 0
        self.remaining = self.time_limit
        self.game_over = False
        self.status_label.config(text="New puzzle! Good luck.", fg=TEXT_MUTED)
        self.draw_board()
        self.start_timer()

    #timer
    def start_timer(self):
        self._update_timer_label()
        self.timer_id = self.after(1000, self._tick)

    def stop_timer(self):
        if self.timer_id is not None:
            try:
                self.after_cancel(self.timer_id)
            except Exception:
                pass
            self.timer_id = None

    def _tick(self):
        if self.game_over:
            return
        self.remaining -= 1
        self._update_timer_label()
        self._update_score_preview()
        if self.remaining <= 0:
            self.lose_game()
            return
        self.timer_id = self.after(1000, self._tick)

    def _update_timer_label(self):
        m, s = divmod(max(0, self.remaining), 60)
        color = DANGER if self.remaining <= 30 else TEXT_LIGHT
        self.timer_label.config(text=f"\u23F1\uFE0F {m:02d}:{s:02d}", fg=color)

    #win/lose
    def check_win(self):
        queens = sum(1 for r in range(self.n) for c in range(self.n) if self.board[r][c] == "Q")
        if queens != self.n:
            return
        conflicts = find_conflicts(self.board, self.regions, self.n)
        if not conflicts:
            self.win_game()
        else:
            self.status_label.config(
                text=f"{len(conflicts)} queen(s) are conflicting \u2014 keep adjusting!",
                fg=DANGER)

    def win_game(self):
        self.game_over = True
        self.stop_timer()
        score = self._update_score_preview()
        self.status_label.config(text="Solved! \U0001F389", fg=SUCCESS)
        self._show_end_popup(win=True, score=score)

    def lose_game(self):
        self.game_over = True
        self.stop_timer()
        self.status_label.config(text="Time's up!", fg=DANGER)
        self._show_end_popup(win=False, score=0)

    def _show_end_popup(self, win, score):
        popup = tk.Toplevel(self)
        popup.title("You Win!" if win else "Time's Up")
        popup.configure(bg=BG_PANEL)
        popup.resizable(False, False)
        popup.grab_set()

        w, h = 420, 460
        self.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")

        img_path = os.path.join(ASSETS_DIR, "winner.png" if win else "looser.png")
        img = load_image(img_path, max_size=(250, 250))

        tk.Label(popup, text=("\U0001F451 You Solved It!" if win else "\u23F0 Out of Time"),
                 font=("Georgia", 20, "bold"), bg=BG_PANEL,
                 fg=(SUCCESS if win else DANGER)).pack(pady=(24, 10))

        if img is not None:
            self._popup_images.append(img)
            tk.Label(popup, image=img, bg=BG_PANEL).pack(pady=6)
        else:
            tk.Label(popup, text=("\U0001F3C6" if win else "\U0001F614"),
                     font=("Segoe UI Emoji", 80), bg=BG_PANEL).pack(pady=14)

        if win:
            tk.Label(popup, text=f"Score: {score}", font=("Segoe UI", 16, "bold"),
                     bg=BG_PANEL, fg=GOLD).pack(pady=(4, 0))
            tk.Label(popup, text=f"Hints used: {self.hints_used}/{MAX_HINTS}",
                     font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_MUTED).pack(pady=(2, 14))
        else:
            tk.Label(popup, text="Better luck next time!", font=FONT_SMALL,
                     bg=BG_PANEL, fg=TEXT_MUTED).pack(pady=(4, 14))

        btn_row = tk.Frame(popup, bg=BG_PANEL)
        btn_row.pack(pady=6)

        def play_again():
            popup.destroy()
            self.controller.start_game(self.difficulty, self.niveau)

        def go_menu():
            popup.destroy()
            self.controller.show_menu()

        make_button(btn_row, "\U0001F504 Play Again", play_again,
                    bg=ACCENT, hover=ACCENT_HOVER, padx=14, pady=8).pack(side="left", padx=6)
        make_button(btn_row, "\u2190 Menu", go_menu,
                    bg=BG_PANEL, hover=ACCENT_SOFT, padx=14, pady=8).pack(side="left", padx=6)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QueensApp()
    app.mainloop()