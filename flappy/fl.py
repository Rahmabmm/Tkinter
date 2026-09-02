from PIL import Image, ImageTk
import tkinter as tk
from pygame import mixer
import random

mixer.init()

window = tk.Tk()
window.geometry('1000x600')
window.title('Flappy Bird')
window.resizable(False, False)

x = 150
y = 300
score = 0
speed = 10
game_over = False
game_started = False


# Background
# Start background
img_start_background = Image.open('flappy/images/background.png')
img_start_background = img_start_background.resize((1000, 600))
img_start_background = ImageTk.PhotoImage(img_start_background)

# Game background
img_game_background = Image.open(r'flappy\images\flappy_bird_backdrop_by_lenaxux_dg34rsu-fullview.jpg')
img_game_background = img_game_background.resize((1000, 600))
img_game_background = ImageTk.PhotoImage(img_game_background)

# Bird
img_bird = Image.open('flappy/images/bird.png')
img_bird = ImageTk.PhotoImage(img_bird)

# Pipes
img_pipe_down = Image.open('flappy/images/pipe.png')
img_pipe_top = img_pipe_down.rotate(180)

img_pipe_down = ImageTk.PhotoImage(img_pipe_down)
img_pipe_top = ImageTk.PhotoImage(img_pipe_top)

# Reset button
img_reset = Image.open('flappy/images/reiniciar.png')
img_reset = ImageTk.PhotoImage(img_reset)


canvas = tk.Canvas(
    window,
    width=1000,
    height=600,
    highlightthickness=0
)

canvas.pack()

background = canvas.create_image(
    0,
    0,
    anchor='nw',
    image=img_start_background
)


title = canvas.create_text(
    500,
    150,
    fill='white',
    font=('Arial', 50, 'bold')
)

start_button = tk.Button(
    window,
    text='START GAME',
    font=('Arial', 20, 'bold'),
    bg='white',
    fg='black',
    padx=30,
    pady=10,
    command=lambda: start_game()
)

start_button.place(
    relx=0.5,
    rely=0.55,
    anchor='center'
)


text_score = canvas.create_text(
    50,
    50,
    text='0',
    fill='white',
    font=('Arial', 30, 'bold')
)

bird = canvas.create_image(
    x,
    y,
    anchor='nw',
    image=img_bird
)

pipe_top = canvas.create_image(
    1200,
    -550,
    anchor='nw',
    image=img_pipe_top
)

pipe_down = canvas.create_image(
    1200,
    550,
    anchor='nw',
    image=img_pipe_down
)

# Hide game objects at the beginning
canvas.itemconfigure(bird, state='hidden')
canvas.itemconfigure(pipe_top, state='hidden')
canvas.itemconfigure(pipe_down, state='hidden')
canvas.itemconfigure(text_score, state='hidden')



def start_game():
    global game_started

    game_started = True

    # Change background
    canvas.itemconfigure(
        background,
        image=img_game_background
    )

    # Hide start screen
    start_button.place_forget()
    canvas.itemconfigure(title, state='hidden')

    # Show game objects
    canvas.itemconfigure(bird, state='normal')
    canvas.itemconfigure(pipe_top, state='normal')
    canvas.itemconfigure(pipe_down, state='normal')
    canvas.itemconfigure(text_score, state='normal')

    # Start music
    mixer.music.load('flappy/music/swoosh.wav')
    mixer.music.play(loops=0)

    # Start game
    move_bird()
    move_pipe()


def move_bird_key(event):

    global x, y

    if game_started and not game_over:

        y -= 30

        canvas.coords(bird,x,y)

        mixer.music.load('flappy/music/wing.wav')
        mixer.music.play(loops=0)


window.bind('<space>', move_bird_key)


def move_bird():
    global x, y
    if game_started and not game_over:

        y += 5

        canvas.coords(bird,x,y)

        if y < 0 or y > window.winfo_height():

            game_end()

        if not game_over:

            window.after(50,move_bird)

def move_pipe():

    global score
    global game_over
    global speed

    if game_started and not game_over:

        canvas.move(
            pipe_top,
            -speed,
            0
        )

        canvas.move(
            pipe_down,
            -speed,
            0
        )

        # Pipe passed
        if canvas.coords(pipe_down)[0] < -100:

            score += 1
            speed += 1

            canvas.itemconfigure(
                text_score,
                text=str(score)
            )

            h = window.winfo_height()

            num = random.choice(
                [i for i in range(160, h, 160)]
            )

            canvas.coords(
                pipe_down,
                window.winfo_width(),
                num + 160
            )

            canvas.coords(
                pipe_top,
                window.winfo_width(),
                num - 900
            )

        # Point sound
        if 0 < canvas.coords(pipe_down)[0] < 160:

            channel = mixer.Channel(1)

            channel.set_volume(1.0)

            sound = mixer.Sound('flappy/music/point.wav')

            channel.play(
                sound,
                loops=0)

        # Collision
        if canvas.bbox(bird) and canvas.bbox(pipe_down):

            if (
                canvas.bbox(bird)[0]
                < canvas.bbox(pipe_down)[2]
                and
                canvas.bbox(bird)[2]
                > canvas.bbox(pipe_down)[0]
            ):

                if (
                    canvas.bbox(bird)[1]
                    < canvas.bbox(pipe_top)[3]
                    or
                    canvas.bbox(bird)[3]
                    > canvas.bbox(pipe_down)[1]
                ):

                    game_end()

        if not game_over:

            window.after(
                50,
                move_pipe
            )


# =========================
# RESET GAME
# =========================

def reset_game():

    global x
    global y
    global score
    global speed
    global game_over

    x = 150
    y = 300
    score = 0
    speed = 10
    game_over = False

    canvas.coords(
        bird,
        x,
        y
    )

    canvas.coords(
        pipe_top,
        1200,
        -550
    )

    canvas.coords(
        pipe_down,
        1200,
        550
    )

    canvas.itemconfigure(
        text_score,
        text='0'
    )

    lbl_game_over.place_forget()
    bt_reset.place_forget()

    mixer.music.load(
        'flappy/music/swoosh.wav'
    )

    mixer.music.play(
        loops=0
    )

    move_bird()
    move_pipe()


# =========================
# GAME OVER
# =========================

def game_end():

    global game_over

    game_over = True

    lbl_game_over.place(
        relx=0.5,
        rely=0.5,
        anchor='center'
    )

    bt_reset.place(
        relx=0.5,
        rely=0.7,
        anchor='center'
    )

    mixer.music.load(
        'flappy/music/hit.wav'
    )

    mixer.music.play(
        loops=0
    )

lbl_game_over = tk.Label(
    window,
    text='Game Over!',
    font=('Arial', 30, 'bold'),
    fg='white',
    bg='#00bfff'
)

bt_reset = tk.Button(
    window,
    border=0,
    image=img_reset,
    activebackground='#00bfff',
    bg='#00bfff',
    command=reset_game
)



lbl_game_over.place_forget()
bt_reset.place_forget()

window.call(
    'wm',
    'iconphoto',
    window._w,
    img_bird
)

window.mainloop()