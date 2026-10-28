"""Главное окно и цикл анимации."""

import tkinter as tk

WIDTH = 800
HEIGHT = 600
BACKGROUND = "#05070f"


class App:
    """Окно с холстом, на котором идёт анимация."""

    def __init__(self):
        """Создать окно и холст."""
        self.window = tk.Tk()
        self.window.title("Фейерверки")
        self.window.resizable(False, False)

        self.canvas = tk.Canvas(self.window, width=WIDTH, height=HEIGHT,
                                bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack()

    def run(self):
        """Запустить главный цикл tkinter."""
        self.window.mainloop()
