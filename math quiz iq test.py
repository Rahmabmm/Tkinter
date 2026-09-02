"""
Math Grid Puzzle App
A Tkinter app that generates "find the missing number" grid puzzles

Features:
- Difficulty levels: Easy / Medium / Hard
- Each difficulty uses a different underlying mathematical pattern
- Hint system: choose between a LOGIC HINT (the formula / reasoning)
  or the FULL ANSWER
- Score tracking + "New Puzzle" button
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random


def generate_easy():
    d = random.randint(2, 4)                 # column step
    row_starts = random.sample(range(1, 15), 4)
    row_starts.sort()

    grid = []
    for start in row_starts:
        row = [start + c * d for c in range(4)]
        grid.append(row)

    blank_row = random.randint(0, 3)
    blank_col = random.randint(0, 3)
    answer = grid[blank_row][blank_col]
    grid[blank_row][blank_col] = None

    hint = (
        f"Look across each row: the numbers increase by the SAME amount "
        f"each time you move one column to the right (a common difference). "
        f"Work out that step size from a row you can see fully, then apply "
        f"it to the row with the missing number."
    )
    return {"grid": grid, "blank": (blank_row, blank_col),
            "answer": answer, "hint": hint}


def generate_medium():
    grid = [[random.randint(1, 9) for _ in range(4)] for _ in range(3)]
    last_row = [sum(grid[r][c] for r in range(3)) for c in range(4)]
    grid.append(last_row)

    blank_col = random.randint(0, 3)
    answer = grid[3][blank_col]
    grid[3][blank_col] = None

    hint = (
        "Add the numbers straight down each column (rows 1 + 2 + 3). "
        "The result is the number that belongs in row 4 of that same "
        "column."
    )
    return {"grid": grid, "blank": (3, blank_col),
            "answer": answer, "hint": hint}


def generate_hard():
    """Combined-operation pattern: last row = (row1 * row2) - row3,
    column by column — mimics the trickier IQ-test style images."""
    grid = [[random.randint(1, 6) for _ in range(4)] for _ in range(3)]
    last_row = [(grid[0][c] * grid[1][c]) - grid[2][c] for c in range(4)]
    grid.append(last_row)

    blank_col = random.randint(0, 3)
    answer = grid[3][blank_col]
    grid[3][blank_col] = None

    hint = (
        "For each column: multiply row 1 by row 2, then subtract row 3. "
        "Formula: row4 = (row1 x row2) - row3. Apply that to the column "
        "with the missing number."
    )
    return {"grid": grid, "blank": (3, blank_col),
            "answer": answer, "hint": hint}


DIFFICULTY_GENERATORS = {
    "Easy": generate_easy,
    "Medium": generate_medium,
    "Hard": generate_hard,
}

class MathQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Math Grid Puzzle")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(bg="#1f2430")

        self.difficulty = tk.StringVar(value="Easy")
        self.score = 0
        self.total = 0
        self.current_puzzle = None
        self.cell_labels = {}       # (r, c) -> Label widget
        self.answer_entry = None
        self.hint_visible = False

        self._build_top_bar()
        self._build_grid_frame()
        self._build_controls()
        self._build_status_bar()

        self.new_puzzle()

    def _build_top_bar(self):
        top = tk.Frame(self, bg="#1f2430")
        top.pack(pady=(15, 5))

        tk.Label(top, text="MATH GRID PUZZLE", font=("Helvetica", 18, "bold"),
                  fg="#f5c542", bg="#1f2430").pack()

        diff_frame = tk.Frame(self, bg="#1f2430")
        diff_frame.pack(pady=10)
        tk.Label(diff_frame, text="Difficulty:", font=("Helvetica", 11),
                  fg="white", bg="#1f2430").pack(side="left", padx=(0, 10))

        for level in ("Easy", "Medium", "Hard"):
            b = tk.Radiobutton(
                diff_frame, text=level, variable=self.difficulty, value=level,
                font=("Helvetica", 11), fg="white", bg="#1f2430",
                selectcolor="#3a3f52", activebackground="#1f2430",
                activeforeground="#f5c542", command=self.new_puzzle
            )
            b.pack(side="left", padx=5)

    def _build_grid_frame(self):
        self.grid_frame = tk.Frame(self, bg="#2b3040", bd=2, relief="ridge")
        self.grid_frame.pack(pady=15)

        for r in range(4):
            for c in range(4):
                lbl = tk.Label(
                    self.grid_frame, text="", width=5, height=2,
                    font=("Helvetica", 16, "bold"), bg="#eae3d3",
                    fg="#1f2430", relief="solid", bd=1
                )
                lbl.grid(row=r, column=c, padx=1, pady=1)
                self.cell_labels[(r, c)] = lbl

    def _build_controls(self):
        controls = tk.Frame(self, bg="#1f2430")
        controls.pack(pady=15)

        tk.Label(controls, text="Your answer:", font=("Helvetica", 11),
                  fg="white", bg="#1f2430").grid(row=0, column=0, padx=5)

        self.answer_entry = tk.Entry(controls, font=("Helvetica", 13), width=8,
                                      justify="center")
        self.answer_entry.grid(row=0, column=1, padx=5)
        self.answer_entry.bind("<Return>", lambda e: self.check_answer())

        check_btn = tk.Button(controls, text="Check", font=("Helvetica", 11, "bold"),
                                bg="#4caf50", fg="white", relief="flat",
                                padx=10, command=self.check_answer)
        check_btn.grid(row=0, column=2, padx=5)

        btn_row = tk.Frame(self, bg="#1f2430")
        btn_row.pack(pady=5)

        hint_btn = tk.Button(btn_row, text="Hint", font=("Helvetica", 11, "bold"),
                               bg="#f5c542", fg="#1f2430", relief="flat",
                               padx=12, command=self.show_hint_menu)
        hint_btn.grid(row=0, column=0, padx=8)

        new_btn = tk.Button(btn_row, text="New Puzzle", font=("Helvetica", 11, "bold"),
                              bg="#5c6bc0", fg="white", relief="flat",
                              padx=12, command=self.new_puzzle)
        new_btn.grid(row=0, column=1, padx=8)

        self.hint_label = tk.Label(self, text="", font=("Helvetica", 10, "italic"),
                                     fg="#f5c542", bg="#1f2430", wraplength=420,
                                     justify="left")
        self.hint_label.pack(pady=(5, 0))

    def _build_status_bar(self):
        self.status_label = tk.Label(self, text="Score: 0 / 0",
                                       font=("Helvetica", 11), fg="white",
                                       bg="#1f2430")
        self.status_label.pack(side="bottom", pady=10)

    #puzzle logic
    def new_puzzle(self):
        generator = DIFFICULTY_GENERATORS[self.difficulty.get()]
        self.current_puzzle = generator()
        self.hint_visible = False
        self.hint_label.config(text="")
        self.answer_entry.delete(0, tk.END)
        self._render_grid()

    def _render_grid(self):
        grid = self.current_puzzle["grid"]
        blank = self.current_puzzle["blank"]
        for r in range(4):
            for c in range(4):
                lbl = self.cell_labels[(r, c)]
                if (r, c) == blank:
                    lbl.config(text="?", fg="#c0392b", bg="#f2d9d9")
                else:
                    lbl.config(text=str(grid[r][c]), fg="#1f2430", bg="#eae3d3")

    def check_answer(self):
        user_input = self.answer_entry.get().strip()
        if not user_input:
            messagebox.showinfo("Enter an answer", "Type a number first.")
            return
        try:
            user_val = int(user_input)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a whole number.")
            return

        self.total += 1
        correct = self.current_puzzle["answer"]
        if user_val == correct:
            self.score += 1
            messagebox.showinfo("Correct!", "Nice work, that's right!")
            self.new_puzzle()
        else:
            messagebox.showwarning("Not quite", "That's not correct. Try again "
                                                  "or use a hint.")
        self._update_status()

    def _update_status(self):
        self.status_label.config(text=f"Score: {self.score} / {self.total}")

    def show_hint_menu(self):
        popup = tk.Toplevel(self)
        popup.title("Hint")
        popup.geometry("320x150")
        popup.configure(bg="#2b3040")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="What kind of help would you like?",
                  font=("Helvetica", 12), fg="white", bg="#2b3040",
                  wraplength=280).pack(pady=15)

        btn_frame = tk.Frame(popup, bg="#2b3040")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Show Logic / Formula",
                   font=("Helvetica", 10, "bold"), bg="#f5c542", fg="#1f2430",
                   relief="flat", padx=8,
                   command=lambda: self._reveal_hint(popup, full_answer=False)
                   ).grid(row=0, column=0, padx=8)

        tk.Button(btn_frame, text="Show Full Answer",
                   font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white",
                   relief="flat", padx=8,
                   command=lambda: self._reveal_hint(popup, full_answer=True)
                   ).grid(row=0, column=1, padx=8)

    def _reveal_hint(self, popup, full_answer):
        popup.destroy()
        if full_answer:
            self.hint_label.config(
                text=f"Answer: {self.current_puzzle['answer']}  "
                     f"({self.current_puzzle['hint']})"
            )
        else:
            self.hint_label.config(text=f"Hint: {self.current_puzzle['hint']}")


if __name__ == "__main__":
    app = MathQuizApp()
    app.mainloop()