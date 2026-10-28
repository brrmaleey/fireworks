"""Главное окно и цикл анимации."""

import tkinter as tk

from src.models.fireworks_model import FPS, FireworksModel
from src.renderers.renderer import BACKGROUND, Renderer

WIDTH = 800
HEIGHT = 600
FRAME_DELAY_MS = 1000 // FPS     # 16 мс, примерно 60 кадров в секунду


class App:
    """Окно с холстом, на котором идёт анимация."""

    def __init__(self):
        """Создать окно, холст, модель и отрисовщик."""
        self.window = tk.Tk()
        self.window.title("Фейерверки")
        self.window.resizable(False, False)

        self.canvas = tk.Canvas(self.window, width=WIDTH, height=HEIGHT,
                                bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack()

        self.model = FireworksModel(WIDTH, HEIGHT)
        self.renderer = Renderer(self.canvas)

    def update(self):
        """Сдвинуть всё на кадр, перерисовать и запланировать новый кадр."""
        self.model.step()
        self.renderer.draw(self.model)
        self.window.after(FRAME_DELAY_MS, self.update)

    def run(self):
        """Запустить цикл анимации и главный цикл tkinter."""
        self.update()
        self.window.mainloop()
