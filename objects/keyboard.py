import pygame

from objects.button import Button


# =========================
# 画面上のソフトウェアキーボード
# =========================

class Keyboard:

    KEY_ROWS = [
        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"],
        ["!", "?", "#", "@"]
    ]

    KEY_WIDTH = 70
    KEY_HEIGHT = 65
    KEY_GAP = 10

    def __init__(self, x, y, font):
        self.font = font
        self.key_buttons = []

        self.make_buttons(x, y)

    def make_buttons(self, x, y):
        """x を中心、y を上端としてキーを並べる"""
        current_y = y

        for row in self.KEY_ROWS:
            row_width = len(row) * self.KEY_WIDTH + (len(row) - 1) * self.KEY_GAP
            current_x = x - row_width // 2

            for key in row:
                self.key_buttons.append(
                    Button(current_x, current_y, self.KEY_WIDTH, self.KEY_HEIGHT, key, self.font)
                )
                current_x += self.KEY_WIDTH + self.KEY_GAP

            current_y += self.KEY_HEIGHT + self.KEY_GAP

        self.key_buttons.append(Button(x - 150, current_y, 140, 60, "<-", self.font))
        self.key_buttons.append(Button(x + 20, current_y, 140, 60, "OK", self.font))

    def handle_event(self, event):
        """押されたキーの文字列を返す（押されていなければ None）"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        for button in self.key_buttons:
            if button.clicked(event.pos):
                return button.text

        return None

    def draw(self, screen):
        for button in self.key_buttons:
            button.draw(screen)
