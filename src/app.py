"""Главное окно и цикл анимации."""

import tkinter as tk

from src.models.fireworks_model import FPS, FireworksModel
from src.renderers.renderer import BACKGROUND, Renderer

WIDTH = 800
HEIGHT = 600
FRAME_DELAY_MS = 1000 // FPS     # 16 мс, примерно 60 кадров в секунду

# Названия клавиш в tkinter (в нижнем регистре).
PAUSE_KEYS = {"space"}
GRAVITY_UP_KEYS = {"up"}
GRAVITY_DOWN_KEYS = {"down"}
MORE_ROCKETS_KEYS = {"right"}
FEWER_ROCKETS_KEYS = {"left"}


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

        self.window.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<Button-1>", self.on_click)

    def on_key_press(self, event):
        """Выполнить команду нажатой клавиши."""
        key = event.keysym.lower()
        if key in PAUSE_KEYS:
            self.model.toggle_pause()
        elif key in GRAVITY_UP_KEYS:
            self.model.change_gravity(1)
        elif key in GRAVITY_DOWN_KEYS:
            self.model.change_gravity(-1)
        elif key in MORE_ROCKETS_KEYS:
            self.model.change_launch_rate(1)
        elif key in FEWER_ROCKETS_KEYS:
            self.model.change_launch_rate(-1)

    def on_click(self, event):
        """Взорвать фейерверк случайного цвета там, где кликнули."""
        self.model.explode(event.x, event.y)

    def update(self):
        """Сдвинуть всё на кадр, перерисовать и запланировать новый кадр."""
        self.model.step()
        self.renderer.draw(self.model)
        self.window.after(FRAME_DELAY_MS, self.update)

    def run(self):
        """Запустить цикл анимации и главный цикл tkinter."""
        # Сразу забрать фокус, чтобы клавиши работали без клика по окну.
        self.window.focus_force()
        self.update()
        self.window.mainloop()
