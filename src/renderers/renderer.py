"""Отрисовка фейерверков на холсте tkinter."""

BACKGROUND = "#05070f"
TEXT_COLOR = "#9aa4b8"
ROCKET_COLOR = "#fff3c4"
ROCKET_RADIUS = 2
ROCKET_TAIL = 3          # длина хвоста ракеты: во сколько кадров её пути
SPARK_RADIUS = 2

HUD_FONT = ("Helvetica", 13)


def blend(color, background, amount):
    """Смешать два цвета вида "#rrggbb".

    amount = 1 даёт color, amount = 0 — background, между ними —
    промежуточный цвет. В tkinter нет прозрачности, поэтому угасание
    искры делаем так: чем меньше ей осталось жить, тем ближе её цвет
    к цвету фона, и искра будто растворяется в небе.
    """
    result = "#"
    # Цвет — три пары шестнадцатеричных цифр: красный, зелёный, синий.
    for start in (1, 3, 5):
        a = int(color[start:start + 2], 16)
        b = int(background[start:start + 2], 16)
        result += f"{round(b + (a - b) * amount):02x}"
    return result


class Renderer:
    """Рисует кадр: ракеты, искры и строку с информацией."""

    def __init__(self, canvas):
        """Запомнить холст, на котором будем рисовать."""
        self.canvas = canvas

    def draw(self, model):
        """Очистить холст и нарисовать текущий кадр."""
        self.canvas.delete("all")
        for rocket in model.rockets:
            self.draw_rocket(rocket)
        for spark in model.sparks:
            self.draw_spark(spark)
        self.draw_hud(model)

    def draw_rocket(self, rocket):
        """Нарисовать ракету: светлую точку и хвост её цвета."""
        # Хвост тянется туда, откуда ракета прилетела, то есть против
        # её скорости: на ROCKET_TAIL кадров назад.
        self.canvas.create_line(rocket.x - rocket.dx * ROCKET_TAIL,
                                rocket.y - rocket.dy * ROCKET_TAIL,
                                rocket.x, rocket.y,
                                fill=rocket.color, width=2)
        self.draw_dot(rocket.x, rocket.y, ROCKET_RADIUS, ROCKET_COLOR)

    def draw_spark(self, spark):
        """Нарисовать искру: чем меньше ей осталось жить, тем она тусклее."""
        color = blend(spark.color, BACKGROUND, spark.brightness)
        self.draw_dot(spark.x, spark.y, SPARK_RADIUS, color)

    def draw_dot(self, x, y, radius, color):
        """Нарисовать кружок радиуса radius с центром в (x, y)."""
        self.canvas.create_oval(x - radius, y - radius, x + radius,
                                y + radius, fill=color, outline="")

    def draw_hud(self, model):
        """Написать в углу, сколько сейчас искр."""
        self.canvas.create_text(15, 15, anchor="w", fill=TEXT_COLOR,
                                font=HUD_FONT,
                                text=f"Искр: {len(model.sparks)}")
