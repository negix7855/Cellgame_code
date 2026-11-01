import pygame

from objects.button import Button


# =========================
# メッセージだけを表示する画面（準備中の機能など）
# =========================

class MessageScene:

    def __init__(self, font, width, height, message):
        self.font = font
        self.message = message

        self.back_button = Button(30, 30, 270, 70, "戻る", font)

    def handle_event(self, event):
        """「戻る」で "back" を返す"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.clicked(event.pos):
                return "back"

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        text = self.font.render(self.message, True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=(width // 2, height // 2)))

        self.back_button.draw(screen)
