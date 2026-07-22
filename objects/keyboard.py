import pygame
from objects.button import Button

class Keyboard:

    def __init__(self, x, y, font):

        self.font = font

        self.key_buttons = []

        self.KEY_ROWS = [
            ["Q","W","E","R","T","Y","U","I","O","P"],
            ["A","S","D","F","G","H","J","K","L"],
            ["Z","X","C","V","B","N","M"]
        ]

        self.make_buttons(x, y)

    def make_buttons(self, x, y):

        key_w = 65
        key_h = 60
        gap = 8

        current_y = y

        for row in self.KEY_ROWS:

            row_width = len(row) * key_w + (len(row) - 1) * gap

            current_x = x - row_width // 2

            for key in row:

                self.key_buttons.append(
                    Button(current_x, current_y, key_w, key_h, key, self.font)
                )

                current_x += key_w + gap

            current_y += key_h + gap

        self.key_buttons.append(
            Button(
                x - 150,
                current_y,
                140,
                60,
                "<-",
                self.font
            )
        )

        self.key_buttons.append(
            Button(
                x + 20,
                current_y,
                140,
                60,
                "OK",
                self.font
            )
        )

    def handle_event(self, event):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        if event.button != 1:
            return None

        for button in self.key_buttons:

            if button.clicked(event.pos):

                return button.text
            
        return None

    def draw(self, screen):

        for button in self.key_buttons:
            button.draw(screen)

