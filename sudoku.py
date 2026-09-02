import random
import tkinter as tk
from tkinter import font as tkfont



PINK_BG      = "#f7d9e3"
CARD         = "#ffffff"
GRID_LINE    = "#e3aac4"
BOX_LINE     = "#b083d4"
DARK_PURPLE  = "#7a5fb0"
GIVEN_TXT    = "#5a4a86"   # fixed clue numbers
USER_TXT     = "#d36a9a"   # player-entered numbers
NOTE_TXT     = "#a98fd6"
SEL_BG       = "#e9def9"   # selected cell
PEER_BG      = "#f6eefc"   # same row/col/box as selection
SAME_BG      = "#fbe4ef"   # same number as selection
CONFLICT_BG  = "#ffd2dc"   # rule-breaking cell
BTN_BG       = "#c9b8ef"
BTN_ACTIVE   = "#b6a0e8"
PAD_BG       = "#fdeef5"
PAD_ACTIVE   = "#f8d8e8"

DIFFICULTY = {"Easy": 42, "Medium": 34, "Hard": 28}   # number of clues



def is_valid(grid, r, c, n):
    for i in range(9):
        if grid[r][i] == n or grid[i][c] == n:
            return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if grid[i][j] == n:
                return False
    return True


def _fill(grid):
    for idx in range(81):
        r, c = divmod(idx, 9)
        if grid[r][c] == 0:
            nums = list(range(1, 10))
            random.shuffle(nums)
            for n in nums:
                if is_valid(grid, r, c, n):
                    grid[r][c] = n
                    if _fill(grid):
                        return True
                    grid[r][c] = 0
            return False
    return True


def make_full_solution():
    grid = [[0] * 9 for _ in range(9)]
    _fill(grid)
    return grid


def count_solutions(grid, limit=2):
    """Count solutions up to `limit` (used to verify uniqueness)."""
    for idx in range(81):
        r, c = divmod(idx, 9)
        if grid[r][c] == 0:
            total = 0
            for n in range(1, 10):
                if is_valid(grid, r, c, n):
                    grid[r][c] = n
                    total += count_solutions(grid, limit)
                    grid[r][c] = 0
                    if total >= limit:
                        return total
            return total
    return 1


def make_puzzle(clues=34):
    """Return (puzzle, solution). Puzzle has a unique solution."""
    solution = make_full_solution()
    puzzle = [row[:] for row in solution]
    cells = list(range(81))
    random.shuffle(cells)
    to_remove = 81 - clues
    removed = 0
    for idx in cells:
        if removed >= to_remove:
            break
        r, c = divmod(idx, 9)
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        test = [row[:] for row in puzzle]
        if count_solutions(test, 2) != 1:
            puzzle[r][c] = saved      # removal broke uniqueness -> undo
        else:
            removed += 1
    return puzzle, solution


class CuteSudoku:
    CELL = 52
    MARGIN = 4

    def __init__(self, root):
        self.root = root
        root.title("Cute Sudoku")
        root.configure(bg=PINK_BG)
        root.resizable(False, False)

        self.board_px = self.CELL * 9
        self.notes_mode = False
        self.selected = (0, 0)
        self.mistakes = 0
        self.seconds = 0
        self.timer_running = False
        self.won = False

        self.title_font = tkfont.Font(family="Comic Sans MS", size=22, weight="bold")
        self.num_font   = tkfont.Font(family="Comic Sans MS", size=22, weight="bold")
        self.note_font  = tkfont.Font(family="Arial", size=9)
        self.info_font  = tkfont.Font(family="Comic Sans MS", size=12, weight="bold")
        self.btn_font   = tkfont.Font(family="Comic Sans MS", size=11, weight="bold")

        self._build_header()
        self._build_board()
        self._build_pad()
        self._build_actions()
        self._bind_keys()

        self.new_game("Easy")

    def _build_header(self):
        tk.Label(self.root, text="\u273f Cute Sudoku \u273f", font=self.title_font,
                 bg=PINK_BG, fg=DARK_PURPLE).pack(pady=(14, 4))

        info = tk.Frame(self.root, bg=PINK_BG)
        info.pack(fill="x", padx=20)

        self.time_lbl = tk.Label(info, text="\u23f1 00:00", font=self.info_font,
                                 bg=PINK_BG, fg=DARK_PURPLE)
        self.time_lbl.pack(side="left")

        self.mist_lbl = tk.Label(info, text="\u2716 0", font=self.info_font,
                                 bg=PINK_BG, fg=USER_TXT)
        self.mist_lbl.pack(side="left", padx=14)

        self.diff_var = tk.StringVar(value="Easy")
        diff = tk.OptionMenu(info, self.diff_var, *DIFFICULTY.keys(),
                             command=self.new_game)
        diff.config(font=self.btn_font, bg=BTN_BG, fg="white", relief="flat",
                    activebackground=BTN_ACTIVE, activeforeground="white",
                    highlightthickness=0, bd=0, width=7)
        diff["menu"].config(bg=CARD, fg=DARK_PURPLE, font=self.btn_font)
        diff.pack(side="right")

    def _build_board(self):
        wrap = tk.Frame(self.root, bg=BOX_LINE, padx=4, pady=4)
        wrap.pack(pady=10)
        size = self.board_px
        self.canvas = tk.Canvas(wrap, width=size, height=size,
                                bg=CARD, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

    def _build_pad(self):
        pad = tk.Frame(self.root, bg=PINK_BG)
        pad.pack(pady=(0, 4))
        for i, n in enumerate(range(1, 10)):
            b = tk.Button(pad, text=str(n), font=self.num_font, width=3, height=1,
                          bg=PAD_BG, fg=DARK_PURPLE, relief="flat", bd=0,
                          activebackground=PAD_ACTIVE,
                          command=lambda v=n: self.enter_number(v))
            b.grid(row=i // 3, column=i % 3, padx=4, pady=4)

    def _build_actions(self):
        bar = tk.Frame(self.root, bg=PINK_BG)
        bar.pack(pady=(2, 14))

        def mkbtn(text, cmd):
            return tk.Button(bar, text=text, font=self.btn_font, bg=BTN_BG,
                             fg="white", relief="flat", bd=0, padx=8, pady=4,
                             activebackground=BTN_ACTIVE, activeforeground="white",
                             command=cmd)

        self.notes_btn = mkbtn("\u270e Notes: off", self.toggle_notes)
        self.notes_btn.grid(row=0, column=0, padx=4)
        mkbtn("\u232b Erase", lambda: self.enter_number(0)).grid(row=0, column=1, padx=4)
        mkbtn("\u2728 Hint", self.hint).grid(row=0, column=2, padx=4)
        mkbtn("\u2713 Check", self.check).grid(row=0, column=3, padx=4)
        mkbtn("\u21bb New", lambda: self.new_game(self.diff_var.get())).grid(
            row=0, column=4, padx=4)

    def _bind_keys(self):
        for n in range(1, 10):
            self.root.bind(str(n), lambda e, v=n: self.enter_number(v))
        for k in ("0", "<BackSpace>", "<Delete>"):
            self.root.bind(k, lambda e: self.enter_number(0))
        self.root.bind("<Up>",    lambda e: self._move(-1, 0))
        self.root.bind("<Down>",  lambda e: self._move(1, 0))
        self.root.bind("<Left>",  lambda e: self._move(0, -1))
        self.root.bind("<Right>", lambda e: self._move(0, 1))
        self.root.bind("n", lambda e: self.toggle_notes())

    def new_game(self, difficulty):
        self.diff_var.set(difficulty)
        self.puzzle, self.solution = make_puzzle(DIFFICULTY[difficulty])
        self.given = [[self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.grid = [row[:] for row in self.puzzle]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.selected = (0, 0)
        self.mistakes = 0
        self.seconds = 0
        self.won = False
        self.mist_lbl.config(text="\u2716 0")
        if not self.timer_running:
            self.timer_running = True
            self._tick()
        self.draw()

    def _tick(self):
        if not self.won:
            self.seconds += 1
            m, s = divmod(self.seconds, 60)
            self.time_lbl.config(text=f"\u23f1 {m:02d}:{s:02d}")
        self.root.after(1000, self._tick)

    def _on_click(self, event):
        c = event.x // self.CELL
        r = event.y // self.CELL
        if 0 <= r < 9 and 0 <= c < 9:
            self.selected = (r, c)
            self.draw()

    def _move(self, dr, dc):
        r, c = self.selected
        self.selected = ((r + dr) % 9, (c + dc) % 9)
        self.draw()

    def toggle_notes(self):
        self.notes_mode = not self.notes_mode
        self.notes_btn.config(text=f"\u270e Notes: {'on' if self.notes_mode else 'off'}")

    def enter_number(self, n):
        if self.won:
            return
        r, c = self.selected
        if self.given[r][c]:
            return

        if self.notes_mode and n != 0:
            if n in self.notes[r][c]:
                self.notes[r][c].discard(n)
            else:
                self.notes[r][c].add(n)
            self.grid[r][c] = 0
        elif n == 0:
            self.grid[r][c] = 0
            self.notes[r][c].clear()
        else:
            self.grid[r][c] = n
            self.notes[r][c].clear()
            if n != self.solution[r][c]:
                self.mistakes += 1
                self.mist_lbl.config(text=f"\u2716 {self.mistakes}")

        self.draw()
        self._check_win()

    def hint(self):
        if self.won:
            return
        r, c = self.selected
        if self.given[r][c] or self.grid[r][c] == self.solution[r][c]:
            # pick any empty/incorrect cell instead
            empties = [(i, j) for i in range(9) for j in range(9)
                       if not self.given[i][j] and self.grid[i][j] != self.solution[i][j]]
            if not empties:
                return
            r, c = random.choice(empties)
            self.selected = (r, c)
        self.grid[r][c] = self.solution[r][c]
        self.notes[r][c].clear()
        self.draw()
        self._check_win()

    def check(self):
        """Flash any filled cells that disagree with the solution."""
        self._flash = [(r, c) for r in range(9) for c in range(9)
                       if self.grid[r][c] != 0 and not self.given[r][c]
                       and self.grid[r][c] != self.solution[r][c]]
        self.draw()
        self.root.after(900, lambda: (setattr(self, "_flash", []), self.draw()))

    def _conflicts(self):
        bad = set()
        for r in range(9):
            for c in range(9):
                v = self.grid[r][c]
                if v == 0:
                    continue
                self.grid[r][c] = 0
                if not is_valid(self.grid, r, c, v):
                    bad.add((r, c))
                self.grid[r][c] = v
        return bad

    def _check_win(self):
        if any(self.grid[r][c] == 0 for r in range(9) for c in range(9)):
            return
        if all(self.grid[r][c] == self.solution[r][c]
               for r in range(9) for c in range(9)):
            self.won = True
            self.draw()
            self._win_banner()

    def draw(self):
        cv = self.canvas
        cv.delete("all")
        sr, sc = self.selected
        sel_val = self.grid[sr][sc]
        conflicts = self._conflicts()
        flash = getattr(self, "_flash", [])

        for r in range(9):
            for c in range(9):
                x0, y0 = c * self.CELL, r * self.CELL
                x1, y1 = x0 + self.CELL, y0 + self.CELL
                bg = CARD
                same_box = (r // 3 == sr // 3 and c // 3 == sc // 3)
                if r == sr and c == sc:
                    bg = SEL_BG
                elif r == sr or c == sc or same_box:
                    bg = PEER_BG
                if sel_val != 0 and self.grid[r][c] == sel_val and (r, c) != (sr, sc):
                    bg = SAME_BG
                if (r, c) in conflicts or (r, c) in flash:
                    bg = CONFLICT_BG
                cv.create_rectangle(x0, y0, x1, y1, fill=bg, outline="")

        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            col = BOX_LINE if i % 3 == 0 else GRID_LINE
            cv.create_line(0, i * self.CELL, self.board_px, i * self.CELL,
                           fill=col, width=w)
            cv.create_line(i * self.CELL, 0, i * self.CELL, self.board_px,
                           fill=col, width=w)

        for r in range(9):
            for c in range(9):
                cx = c * self.CELL + self.CELL / 2
                cy = r * self.CELL + self.CELL / 2
                v = self.grid[r][c]
                if v != 0:
                    color = GIVEN_TXT if self.given[r][c] else USER_TXT
                    cv.create_text(cx, cy, text=str(v), font=self.num_font, fill=color)
                elif self.notes[r][c]:
                    for n in self.notes[r][c]:
                        nx = c * self.CELL + 9 + ((n - 1) % 3) * (self.CELL / 3)
                        ny = r * self.CELL + 9 + ((n - 1) // 3) * (self.CELL / 3)
                        cv.create_text(nx, ny, text=str(n),
                                       font=self.note_font, fill=NOTE_TXT)

    def _win_banner(self):
        cv = self.canvas
        cv.create_rectangle(0, self.board_px / 2 - 60, self.board_px,
                            self.board_px / 2 + 60, fill="#ffffff", outline=BOX_LINE,
                            width=3)
        m, s = divmod(self.seconds, 60)
        cv.create_text(self.board_px / 2, self.board_px / 2 - 18,
                       text="\u2728 You did it! \u2728", font=self.title_font,
                       fill=DARK_PURPLE)
        cv.create_text(self.board_px / 2, self.board_px / 2 + 20,
                       text=f"Time {m:02d}:{s:02d}   \u2022   Mistakes {self.mistakes}",
                       font=self.info_font, fill=USER_TXT)


if __name__ == "__main__":
    root = tk.Tk()
    CuteSudoku(root)
    root.mainloop()