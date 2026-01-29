# _internal/Menu/Menu_Levels.py
import arcade
import math
import subprocess
import sys
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Меню уровней — Марио Стиль"

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.options = ["Уровень 1", "Уровень 2", "Уровень 3", "Уровень 4"]
        self.selected_option = 0
        self.frame_count = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        self.clear()
        self.frame_count += 1

        # Рисуем облака
        for i in range(5):
            x = 100 + i * 150
            y = 500 + math.sin(self.frame_count / 30 + i) * 10
            arcade.draw_circle_filled(x, y, 40, arcade.color.WHITE_SMOKE)
            arcade.draw_circle_filled(x + 50, y + 20, 50, arcade.color.LIGHT_GRAY)

        # Заголовок
        arcade.draw_text(
            "МЕНЮ УРОВНЕЙ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.RED,
            font_size=50,
            anchor_x="center"
        )

        # Кнопки уровней с анимацией подпрыгивания
        start_y = SCREEN_HEIGHT - 200
        for i, option in enumerate(self.options):
            scale = 1 + 0.05 * math.sin(self.frame_count / 10 + i)
            color = arcade.color.YELLOW if i == self.selected_option else arcade.color.WHITE
            arcade.draw_text(
                f"{i+1}. {option}",
                SCREEN_WIDTH // 2,
                start_y - i * 80,
                color,
                font_size=int(30 * scale),
                anchor_x="center"
            )

        # Подсказка
        arcade.draw_text(
            "↑↓ — выбрать уровень, Enter — запустить, ESC — выйти",
            SCREEN_WIDTH // 2,
            50,
            arcade.color.BLACK,
            font_size=20,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == arcade.key.DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == arcade.key.ENTER:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            level = self.selected_option + 1
            level_path = os.path.join(parent_dir, f"Level_{level}", f"Level_{level}.py")
            # Запускаем выбранный уровень
            subprocess.Popen([sys.executable, level_path])
            # Закрываем меню
            self.window.close()
        elif key == arcade.key.ESCAPE:
            self.window.close()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu = MenuView()
    window.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
