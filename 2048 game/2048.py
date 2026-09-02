import tkinter as tk
import random

# basic board setup: 4x4 array full of zeroes at start
board = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

score = 0

# colors dict for numbers, got these RGB values online
tile_colors = {
    0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
}

# setting up main Tk window frame
window = tk.Tk()
window.title("2048 - Simple Version")
window.configure(bg="#faf8ef")
window.resizable(False, False)


# pick random zero spot and add 2 or 4 (mostly 2)
def add_tile():
    empty = []
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                empty.append((i, j))

    if empty:
        i, j = random.choice(empty)
        # 90% chance for 2, 10% chance for 4
        board[i][j] = 2 if random.random() < 0.9 else 4


# shift all numbers left and merge same values next to each other
def move_line(line):
    global score

    # filter out zeros
    new = [num for num in line if num != 0]
    while len(new) < 4:
        new.append(0)

    # merge adjacent numbers if equal
    for i in range(3):
        if new[i] != 0 and new[i] == new[i + 1]:
            new[i] *= 2
            score += new[i]
            new[i + 1] = 0

    # filter zero again after merge
    result = [num for num in new if num != 0]
    while len(result) < 4:
        result.append(0)

    return result


def move_left():
    old_board = [row[:] for row in board]
    for i in range(4):
        board[i] = move_line(board[i])
    return old_board != board


def move_right():
    old_board = [row[:] for row in board]
    for i in range(4):
        board[i] = move_line(board[i][::-1])[::-1]
    return old_board != board


def move_up():
    old_board = [row[:] for row in board]
    for j in range(4):
        column = [board[i][j] for i in range(4)]
        column = move_line(column)
        for i in range(4):
            board[i][j] = column[i]
    return old_board != board


def move_down():
    old_board = [row[:] for row in board]
    for j in range(4):
        column = [board[i][j] for i in range(4)]
        column = move_line(column[::-1])[::-1]
        for i in range(4):
            board[i][j] = column[i]
    return old_board != board


# re-render grid on screen after every key press
def render_board(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    for i in range(4):
        for j in range(4):
            num = board[i][j]
            txt = "" if num == 0 else str(num)
            color = tile_colors.get(num, "#3c3a32")
            txt_color = "#776e65" if num <= 4 else "white"

            lbl = tk.Label(
                frame, text=txt, font=("Arial", 24, "bold"),
                width=4, height=2, bg=color, fg=txt_color
            )
            lbl.grid(row=i, column=j, padx=5, pady=5)


# key controls handler function
def on_key(event):
    changed = False
    if event.keysym == "Left": changed = move_left()
    elif event.keysym == "Right": changed = move_right()
    elif event.keysym == "Up": changed = move_up()
    elif event.keysym == "Down": changed = move_down()

    if changed:
        add_tile()
        render_board(board_frame)


# simple start setup for part 1 testing
board_frame = tk.Frame(window, bg="#bbada0")
board_frame.pack(pady=20, padx=20)

add_tile()
add_tile()
render_board(board_frame)

window.bind("<Left>", on_key)
window.bind("<Right>", on_key)
window.bind("<Up>", on_key)
window.bind("<Down>", on_key)

if __name__ == "__main__":
    window.mainloop()