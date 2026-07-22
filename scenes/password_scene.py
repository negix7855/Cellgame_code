import pygame
from objects.textbox import TextBox
from objects.button import Button
from objects.keyboard import Keyboard

class PasswordScene:

    def __init__(self, width, height, font):

        self.font = font
        self.input_test = ""

        self.width = width

        self.textbox = TextBox(
            width//2 - 200, height//2 - 60, 400, 60, font
        )

        self.home_button = Button(
            10,
            10,
            270,
            70,
            "ホームに戻る",
            font
        )

        self.keyboard = Keyboard(
            width // 2,
            height // 2 + 50,
            font
        )

    def handle_event(self, event):

        key = self.keyboard.handle_event(event)

        if key == "<-":

            self.textbox.text = self.textbox.text[:-1]

        elif key == "OK":

            return self.textbox.text

        elif key is not None:

            self.textbox.text += key


        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.home_button.clicked(event.pos):

                    return "home"

    def draw(self, screen):

        screen.fill((255,255,255))

        text = self.font.render(
            "エクストラステージのパスワードを入力してください",
            True,
            (0,0,0)
        )

        text_rect = text.get_rect(
            center=(self.width // 2, 250)
        )

        screen.blit(text, text_rect)

        self.textbox.draw(screen)
        self.keyboard.draw(screen)

        self.home_button.draw(screen)
