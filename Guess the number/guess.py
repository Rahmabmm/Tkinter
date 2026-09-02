import tkinter as tk
import random
from PIL import Image, ImageTk
from tkinter import messagebox

# WINDOW

window = tk.Tk()
window.title("Guess the Number")
window.geometry("500x600")
window.resizable(False, False)


# COLORS

bg_color = "#EAF2F8"
card_color = "#FFFFFF"
title_color = "#2C3E50"
button_color = "#3498DB"
replay_color = "#2ECC71"
quit_color = "#E74C3C"


# GAME VARIABLES


number = random.randint(1, 20)
attempts = 0
game_over = False

# LOAD IMAGES

wrong = Image.open(
    r"Guess the number\images\looser.png"
)
wrong = wrong.resize((100, 100))

correct = Image.open(
    r"Guess the number\images\winner.png"
)
correct = correct.resize((100, 100))

correct_image = ImageTk.PhotoImage(correct)
wrong_image = ImageTk.PhotoImage(wrong)


# CANVAS

canvas = tk.Canvas(
    window,
    width=500,
    height=600,
    bg=bg_color,
    highlightthickness=0
)

canvas.pack()


# BACKGROUND CARD

canvas.create_rectangle(
    40, 30,
    460, 570,
    fill=card_color,
    outline=""
)


# TITLE

canvas.create_text(
    250, 70,
    text="🎯 GUESS THE NUMBER",
    font=("Arial", 22, "bold"),
    fill=title_color
)

canvas.create_text(
    250, 105,
    text="Guess a number between 1 and 20",
    font=("Arial", 12),
    fill="#7F8C8D"
)


# ENTRY

entry = tk.Entry(
    window,
    font=("Arial", 18),
    justify="center",
    width=10
)

canvas.create_window(
    250, 155,
    window=entry
)


# GUESS BUTTON

guess_button = tk.Button(
    window,
    text="🎯  GUESS",
    font=("Arial", 12, "bold"),
    bg=button_color,
    fg="white",
    activebackground="#2980B9",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=lambda: check_guess()
)

canvas.create_window(
    250, 205,
    window=guess_button,
    width=130,
    height=40
)


# RESULT

result_label = tk.Label(
    window,
    text="Make your guess!",
    font=("Arial", 14, "bold"),
    bg=card_color,
    fg=title_color
)

canvas.create_window(
    250, 250,
    window=result_label
)


# IMAGE

image_label = tk.Label(
    window,
    bg=card_color
)

canvas.create_window(
    250, 340,
    window=image_label
)


# ATTEMPTS

attempts_label = tk.Label(
    window,
    text="Attempts: 0",
    font=("Arial", 11),
    bg=card_color,
    fg="#7F8C8D"
)

canvas.create_window(
    250, 410,
    window=attempts_label
)


# REPLAY BUTTON

reset_button = tk.Button(
    window,
    text="🔄  Replay",
    font=("Arial", 11, "bold"),
    bg=replay_color,
    fg="white",
    activebackground="#27AE60",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=lambda: reset_game()
)

canvas.create_window(
    190, 470,
    window=reset_button,
    width=120,
    height=40
)


# QUIT BUTTON

quit_button = tk.Button(
    window,
    text="❌  Quit",
    font=("Arial", 11, "bold"),
    bg=quit_color,
    fg="white",
    activebackground="#C0392B",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=lambda: quit_game()
)

canvas.create_window(
    310, 470,
    window=quit_button,
    width=120,
    height=40
)


# FUNCTIONS

def check_guess():
    global attempts
    global game_over

    # Don't allow guesses after the game is over
    if game_over:
        return

    try:
        guess = int(entry.get())
        attempts += 1

        attempts_label.config(
            text=f"Attempts: {attempts}"
        )

        if guess < number:
            result_label.config(
                text="📉 Too low!",
                fg="#E67E22"
            )

            image_label.config(
                image=wrong_image
            )

        elif guess > number:
            result_label.config(
                text="📈 Too high!",
                fg="#E67E22"
            )

            image_label.config(
                image=wrong_image
            )

        else:
            # GAME WON
            game_over = True

            result_label.config(
                text="🎉 You guessed it!",
                fg="#27AE60"
            )

            image_label.config(
                image=correct_image
            )

            # Disable guessing
            entry.config(state="disabled")
            guess_button.config(state="disabled")

    except ValueError:
        result_label.config(
            text="⚠️ Please enter a number!",
            fg="#E74C3C"
        )

        image_label.config(
            image=wrong_image
        )

def reset_game():
    global number
    global attempts
    global game_over

    number = random.randint(1, 20)
    attempts = 0
    game_over = False

    entry.config(state="normal")
    guess_button.config(state="normal")

    entry.delete(0, tk.END)

    result_label.config(
        text="Make your guess!",
        fg=title_color
    )

    attempts_label.config(
        text="Attempts: 0"
    )

    image_label.config(
        image=""
    )

    entry.focus()


def quit_game():
    answer = messagebox.askyesno(
        "Quit Game",
        "Are you sure you want to quit?"
    )

    if answer:
        window.destroy()


# START
window.mainloop()