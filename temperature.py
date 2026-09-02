import tkinter as tk

window = tk.Tk()
window.title("Temperature Converter")
window.geometry("500x400")


# FRAME
frame = tk.Frame(
    window,
    width=400,
    height=300,
    bg="lightblue",
    relief="raised",
    borderwidth=5
)

frame.pack(pady=50)

# TITLE
title = tk.Label(
    frame,
    text="Temperature Converter",
    font=("Georgia", 17, "bold"),
    bg="lightblue"
)

title.pack(pady=20)

# CELSIUS LABEL
celsius_label = tk.Label(
    frame,
    text="Enter temperature in Celsius:",
    font=("Georgia", 16),
    bg="lightblue"
)

celsius_label.pack()

# ENTRY
celsius_entry = tk.Entry(frame)

celsius_entry.pack(pady=10)


# FUNCTION
def convert_temperature():

    try:
        celsius = float(celsius_entry.get())
        fahrenheit = celsius * 9 / 5 + 32
        result_label.config(
            text=f"Temperature: {fahrenheit:.2f} °F",
            font=("Georgia", 16, "bold"),
            fg="black"
        )
    except ValueError:
        result_label.config(
            text="Please enter a valid number!",
            font=("Georgia", 16, "bold"),
            fg="red"
        )


# BUTTON
convert_button = tk.Button(
    frame,
    text="Convert",
    font=("Georgia", 13),
    command=convert_temperature
)

convert_button.pack(pady=10)

# RESULT
result_label = tk.Label(
    frame,
    text="Temperature: ",
    bg="lightblue",
    font=("Georgia", 14)
)

result_label.pack(pady=10)

# RUN APPLICATION
window.mainloop()