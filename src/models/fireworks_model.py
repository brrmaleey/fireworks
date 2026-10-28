"""Логика фейерверков: запуск ракет, взрывы и движение искр."""

import math
import random

from src.models.particles import Rocket, Spark

FPS = 60                 # кадров в секунду

# Цвета фейерверков: у каждого взрыва свой случайный цвет.
COLORS = ("#ff5a5f", "#ff9f40", "#ffd93d", "#6bcb77",
          "#4dd4ff", "#4d96ff", "#c77dff", "#ffffff")

ROCKET_GRAVITY = 0.15    # ракеты всегда тормозят одинаково
ROCKET_MIN_SPEED = 9     # скорость ракеты вверх при запуске, пикселей
ROCKET_MAX_SPEED = 12    # за кадр; от неё зависит высота взрыва

SPARKS_PER_EXPLOSION = 80
SPARK_MIN_SPEED = 1
SPARK_MAX_SPEED = 4
SPARK_MIN_LIFE = 40      # время жизни искры в кадрах
SPARK_MAX_LIFE = 80

START_GRAVITY = 0.05     # гравитация искр
START_LAUNCH_RATE = 2    # сколько ракет в секунду запускается в среднем


class FireworksModel:
    """Все ракеты и искры на экране и правила их движения."""

    def __init__(self, width, height):
        """Создать пустое небо размером width x height."""
        self.width = width
        self.height = height
        self.rockets = []
        self.sparks = []
        self.gravity = START_GRAVITY
        self.launch_rate = START_LAUNCH_RATE

    def launch(self):
        """Запустить ракету снизу экрана в случайном месте."""
        x = random.uniform(self.width * 0.1, self.width * 0.9)
        speed = random.uniform(ROCKET_MIN_SPEED, ROCKET_MAX_SPEED)
        drift = random.uniform(-1, 1)    # небольшой наклон в сторону
        self.rockets.append(Rocket(x, self.height, drift, -speed,
                                   random.choice(COLORS)))

    def explode(self, x, y, color=None):
        """Взорвать фейерверк в точке (x, y): разбросать искры кругом.

        Если цвет не задан, он выбирается случайно.
        """
        if color is None:
            color = random.choice(COLORS)
        for _ in range(SPARKS_PER_EXPLOSION):
            # Каждой искре — случайное направление (угол) и скорость.
            # cos и sin раскладывают скорость на горизонтальную
            # и вертикальную части, поэтому искры разлетаются кругом.
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(SPARK_MIN_SPEED, SPARK_MAX_SPEED)
            life = random.randint(SPARK_MIN_LIFE, SPARK_MAX_LIFE)
            self.sparks.append(Spark(x, y, math.cos(angle) * speed,
                                     math.sin(angle) * speed, color, life))

    def step(self):
        """Сдвинуть всё на один кадр."""
        # launch_rate ракет в секунду — это launch_rate / FPS за кадр,
        # поэтому каждый кадр запускаем ракету с такой вероятностью.
        if random.random() < self.launch_rate / FPS:
            self.launch()

        for rocket in self.rockets:
            rocket.move(ROCKET_GRAVITY)
            if rocket.is_at_top():
                self.explode(rocket.x, rocket.y, rocket.color)
        for spark in self.sparks:
            spark.move(self.gravity)

        # Взорвавшиеся ракеты и погасшие искры убираем из списков.
        self.rockets = [r for r in self.rockets if not r.is_at_top()]
        self.sparks = [s for s in self.sparks if s.is_alive()]
