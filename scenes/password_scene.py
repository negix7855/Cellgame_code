import pygame

from objects.button import Button
from objects.keyboard import Keyboard
from objects.textbox import TextBox


# =========================
# エクストラステージのパスワード入力画面
# =========================

class PasswordScene:

    def __init__(self, font, width, height, password):
        self.font = font
        self.width = width
        self.password = password

        self.message = ""
        self.warn_flg = False

        self.textbox = TextBox(width // 2 - 200, height // 2 - 200, 400, 60, font)
        self.keyboard = Keyboard(width // 2, height // 2 - 50, font)
        self.home_button = Button(30, 30, 270, 70, "ホームに戻る", font)

    def handle_event(self, event):
        """OK で入力文字列を、ホームボタンで "home" を返す"""
        key = self.keyboard.handle_event(event)

        if key == "<-":
            self.textbox.text = self.textbox.text[:-1]

        elif key == "OK":
            if self.textbox.text == self.password:
                self.warn_flg = False
                return self.password
            else:
                self.message = "不正なパスコードです"
                self.warn_flg = True

        elif key is not None:
            self.textbox.text += key

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.home_button.clicked(event.pos):
                self.textbox.clear()
                return "home"

    def draw(self, screen):
        screen.fill((255, 255, 255))

        text = self.font.render(
            "エクストラステージのパスワードを入力してください",
            True,
            (0, 0, 0)
        )
        screen.blit(text, text.get_rect(center=(self.width // 2, 250)))

        if self.warn_flg == True:

            warn_text = self.font.render(
                self.message,
                True,
                (255, 0, 0)
            )
            screen.blit(warn_text, warn_text.get_rect(center=(self.width // 2, 300)))

        self.textbox.draw(screen)
        self.keyboard.draw(screen)
        self.home_button.draw(screen)
