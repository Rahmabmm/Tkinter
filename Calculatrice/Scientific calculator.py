import tkinter as tk
import math

class Calculator:
    def __init__(self, window):
        self.window = window
        window.title("Scientific Calculator")
        window.resizable(False, False)

        self.bg = "#202020"
        self.display_bg = "#1E1E1E"
        self.num_bg = "#2D2D2D"
        self.op_bg = "#4C4C4C"
        self.sci_bg = "#333333"
        self.equal_bg = "#0184FE"
        self.text_color = "white"
        window.configure(bg=self.bg)

        self.expression = ""        
        self.current_input = ""      
        self.operator_pending = False

        self.label = tk.Label(
            window, text="0", font=("Segoe UI", 30),
            bg=self.display_bg, fg=self.text_color,
            anchor="e", padx=15
        )
        self.label.grid(row=0, column=0, columnspan=6, sticky="we", pady=5)

        self.buttons = [
            ["sin", "cos", "tan", "log", "xʸ", "exp"],
            ["7", "8", "9", "÷", "sqrt", "1/x"],
            ["4", "5", "6", "×", "^2", "π"],
            ["1", "2", "3", "-", "+", "x!"],
            ["0", ".", "AC", "+/-", "%", "="]
        ]

        self.create_buttons()

        window.update()
        w, h = window.winfo_width(), window.winfo_height()
        sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def create_buttons(self):
        for r, row in enumerate(self.buttons):
            for c, value in enumerate(row):
                btn = tk.Button(
                    self.window, text=value, font=("Segoe UI", 18),
                    fg=self.text_color, width=5, height=2,
                    bd=0,
                    command=lambda v=value: self.clicked(v)
                )

              
                if value in ["+", "-", "×", "÷", "xʸ"]:
                    btn.configure(bg=self.op_bg)
                elif value == "=":
                    btn.configure(bg=self.equal_bg)
                elif value in ["sin", "cos", "tan", "log", "sqrt", "1/x", "x!", "10ˣ", "exp", "^2", "π"]:
                    btn.configure(bg=self.sci_bg)
                elif value in ["AC", "+/-", "%"]:
                    btn.configure(bg=self.op_bg)
                else:
                    btn.configure(bg=self.num_bg)

                btn.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)

        for i in range(6):
            self.window.columnconfigure(i, weight=1)

    def update_display(self):
        if self.expression == "" and self.current_input == "":
            display_text = "0"
        else:
            display_text = self.expression + self.current_input
        self.label.config(text=display_text)

    def clicked(self, value):
        text = self.current_input

        if value == "AC":
            self.expression = ""
            self.current_input = ""
            self.operator_pending = False
            self.update_display()
            return

        if value == "+/-":
            try:
                if text:
                    self.current_input = str(-float(text))
                else:
                    self.current_input = "0"
            except:
                self.current_input = "Error"
            self.update_display()
            return

        if value == "%":
            try:
                if text:
                    self.current_input = str(float(text)/100)
                else:
                    self.current_input = "0"
            except:
                self.current_input = "Error"
            self.update_display()
            return

        if value == "π":
            self.current_input = str(math.pi)
            self.update_display()
            return

        try:
            num = float(text) if text else 0
            if value == "sin":
                self.current_input = str(math.sin(math.radians(num)))
                self.update_display()
                return
            if value == "cos":
                self.current_input = str(math.cos(math.radians(num)))
                self.update_display()
                return
            if value == "tan":
                self.current_input = str(math.tan(math.radians(num)))
                self.update_display()
                return
            if value == "log":
                self.current_input = str(math.log10(num))
                self.update_display()
                return
            if value == "sqrt":
                self.current_input = str(math.sqrt(num))
                self.update_display()
                return
            if value == "1/x":
                self.current_input = str(1 / num)
                self.update_display()
                return
            if value == "x!":
                self.current_input = str(math.factorial(int(num)))
                self.update_display()
                return
            if value == "^2":
                self.current_input = str(num ** 2)
                self.update_display()
                return
            if value == "10ˣ":
                self.current_input = str(10 ** num)
                self.update_display()
                return
            if value == "exp":
                self.current_input = str(math.exp(num))
                self.update_display()
                return
        except:
            self.current_input = "Error"
            self.update_display()
            return

        if value in ["+", "-", "×", "÷", "xʸ"]:
            if self.current_input == "" and self.expression:
                # replace last operator
                if self.expression[-1] in "+-*/**":
                    self.expression = self.expression[:-1]
            else:
                if value == "xʸ":
                    op = "**"
                else:
                    op = value.replace("×", "*").replace("÷", "/")
                self.expression += self.current_input + op
                self.current_input = ""
            self.operator_pending = True
            self.update_display()
            return

        if value == "=":
            self.expression += self.current_input
            try:
                result = eval(self.expression)
                self.current_input = str(result)
                self.expression = ""
            except:
                self.current_input = "Error"
                self.expression = ""
            self.update_display()
            self.operator_pending = False
            return

        if text == "0" and value not in ["."]:
            self.current_input = value
        else:
            self.current_input += value
        self.operator_pending = False
        self.update_display()

window = tk.Tk()
Calculator(window)
window.mainloop()

