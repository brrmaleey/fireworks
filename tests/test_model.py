"""Тесты для частиц, логики фейерверков и смешивания цветов."""

import random
import unittest

from src.models.fireworks_model import (COLORS, GRAVITY_STEP, MAX_GRAVITY,
                                        MAX_LAUNCH_RATE, SPARK_MAX_LIFE,
                                        SPARKS_PER_EXPLOSION, START_GRAVITY,
                                        FireworksModel)
from src.models.particles import FADE_FRAMES, Particle, Rocket, Spark
from src.renderers.renderer import blend

WIDTH = 800
HEIGHT = 600


def quiet_model():
    """Создать модель, в которой ракеты сами не взлетают."""
    model = FireworksModel(WIDTH, HEIGHT)
    model.launch_rate = 0
    return model


class TestParticles(unittest.TestCase):
    """Проверки классов Particle, Rocket и Spark."""

    def test_move_without_gravity(self):
        """Без гравитации частица летит по прямой с постоянной скоростью."""
        particle = Particle(0, 0, 2, 3, "#ffffff")
        particle.move(0)
        particle.move(0)
        self.assertEqual((particle.x, particle.y), (4, 6))

    def test_gravity_pulls_down(self):
        """Гравитация каждый кадр прибавляет скорости вниз."""
        particle = Particle(0, 0, 0, 0, "#ffffff")
        particle.move(1)     # скорость 1, сдвиг на 1
        particle.move(1)     # скорость 2, сдвиг ещё на 2
        self.assertEqual(particle.dy, 2)
        self.assertEqual(particle.y, 3)

    def test_rocket_explodes_at_top(self):
        """Ракета на вершине, когда перестала подниматься."""
        rocket = Rocket(0, 100, 0, -1, "#ffffff")
        self.assertFalse(rocket.is_at_top())
        rocket.move(0.5)
        self.assertFalse(rocket.is_at_top())
        rocket.move(0.5)
        self.assertTrue(rocket.is_at_top())

    def test_spark_life(self):
        """Искра живёт ровно столько кадров, сколько ей задано."""
        spark = Spark(0, 0, 1, 0, "#ffffff", life=3)
        spark.move(0)
        spark.move(0)
        self.assertTrue(spark.is_alive())
        spark.move(0)
        self.assertFalse(spark.is_alive())

    def test_spark_slows_down(self):
        """Сопротивление воздуха уменьшает скорость искры."""
        spark = Spark(0, 0, 4, 0, "#ffffff", life=10)
        spark.move(0)
        self.assertLess(spark.dx, 4)

    def test_spark_brightness(self):
        """Искра горит в полную силу и гаснет только в конце жизни."""
        spark = Spark(0, 0, 0, 0, "#ffffff", life=FADE_FRAMES * 2)
        self.assertEqual(spark.brightness, 1)
        spark.life = FADE_FRAMES // 2
        self.assertAlmostEqual(spark.brightness, 0.5)
        spark.life = 0
        self.assertEqual(spark.brightness, 0)


class TestFireworksModel(unittest.TestCase):
    """Проверки класса FireworksModel."""

    def test_launch(self):
        """Ракета стартует от нижнего края экрана и летит вверх."""
        model = quiet_model()
        model.launch()
        rocket = model.rockets[0]
        self.assertEqual(rocket.y, HEIGHT)
        self.assertLess(rocket.dy, 0)
        self.assertIn(rocket.color, COLORS)

    def test_explode(self):
        """Взрыв даёт нужное число искр одного цвета в точке взрыва."""
        model = quiet_model()
        model.explode(100, 200, "#ff5a5f")
        self.assertEqual(len(model.sparks), SPARKS_PER_EXPLOSION)
        for spark in model.sparks:
            self.assertEqual((spark.x, spark.y), (100, 200))
            self.assertEqual(spark.color, "#ff5a5f")

    def test_sparks_fly_in_all_directions(self):
        """Искры разлетаются во все стороны, а не в одну."""
        random.seed(0)
        model = quiet_model()
        model.explode(400, 300)
        self.assertTrue(any(spark.dx > 0 for spark in model.sparks))
        self.assertTrue(any(spark.dx < 0 for spark in model.sparks))
        self.assertTrue(any(spark.dy > 0 for spark in model.sparks))
        self.assertTrue(any(spark.dy < 0 for spark in model.sparks))

    def test_rocket_turns_into_sparks(self):
        """Долетевшая до вершины ракета исчезает и превращается в искры."""
        model = quiet_model()
        model.launch()
        for _ in range(200):
            model.step()
            if not model.rockets:
                break
        self.assertEqual(model.rockets, [])
        self.assertEqual(len(model.sparks), SPARKS_PER_EXPLOSION)

    def test_sparks_disappear(self):
        """Когда время жизни кончается, искры убираются из списка."""
        model = quiet_model()
        model.explode(400, 300)
        for _ in range(SPARK_MAX_LIFE):
            model.step()
        self.assertEqual(model.sparks, [])

    def test_automatic_launches(self):
        """Ракеты взлетают сами, если частота больше нуля."""
        random.seed(1)
        model = FireworksModel(WIDTH, HEIGHT)
        model.launch_rate = MAX_LAUNCH_RATE
        for _ in range(60):
            model.step()
        self.assertTrue(model.rockets or model.sparks)

        model = quiet_model()
        for _ in range(600):
            model.step()
        self.assertEqual(model.rockets, [])

    def test_pause(self):
        """На паузе искры стоят на месте."""
        model = quiet_model()
        model.explode(400, 300)
        model.toggle_pause()
        before = [(spark.x, spark.y) for spark in model.sparks]
        model.step()
        self.assertEqual([(spark.x, spark.y) for spark in model.sparks],
                         before)
        model.toggle_pause()
        model.step()
        self.assertNotEqual([(spark.x, spark.y) for spark in model.sparks],
                            before)

    def test_gravity_limits(self):
        """Гравитация меняется шагами и не выходит за пределы."""
        model = quiet_model()
        model.change_gravity(1)
        self.assertAlmostEqual(model.gravity, START_GRAVITY + GRAVITY_STEP)
        for _ in range(20):
            model.change_gravity(1)
        self.assertEqual(model.gravity, MAX_GRAVITY)
        for _ in range(20):
            model.change_gravity(-1)
        self.assertEqual(model.gravity, 0)

    def test_launch_rate_limits(self):
        """Частота запуска не меньше 0 и не больше максимума."""
        model = quiet_model()
        model.change_launch_rate(-1)
        self.assertEqual(model.launch_rate, 0)
        for _ in range(20):
            model.change_launch_rate(1)
        self.assertEqual(model.launch_rate, MAX_LAUNCH_RATE)


class TestBlend(unittest.TestCase):
    """Проверки смешивания цветов для угасания искр."""

    def test_blend(self):
        """1 — исходный цвет, 0 — цвет фона, 0.5 — ровно посередине."""
        self.assertEqual(blend("#ff8000", "#000000", 1), "#ff8000")
        self.assertEqual(blend("#ff8000", "#000000", 0), "#000000")
        self.assertEqual(blend("#ffffff", "#000000", 0.5), "#808080")


if __name__ == "__main__":
    unittest.main()
