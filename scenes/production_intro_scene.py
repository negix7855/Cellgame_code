import pygame

from objects.button import Button


# =========================
# 本番前の案内画面
# （エクストラの選択画面で「本番問題」を選んだ時に表示する）
# =========================

class ProductionIntroScene:

    def __init__(self, font, width, height, total_questions):
        self.font = font
        self.total_questions = total_questions

        self.start_button = Button(width // 2 - 150, height // 2 + 150, 300, 80, "本番へ進む", font)
        self.back_button = Button(10, 10, 270, 70, "選択画面に戻る", font)

    def update_layout(self, width, height):
        self.start_button.rect = pygame.Rect(width // 2 - 150, height // 2 + 150, 300, 80)

    def handle_event(self, event):
        """「本番へ進む」で "start"、「選択画面に戻る」で "back" を返す"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.clicked(event.pos):
                return "start"

            if self.back_button.clicked(event.pos):
                return "back"

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        screen.fill((255, 255, 255))

        lines = [
            ("本番問題", (0, 0, 0)),
            ("画面に映し出された細胞の分布を観察して、", (0, 0, 0)),
            (f"症例を判定してください（全{self.total_questions}問）", (0, 0, 0)),
        ]

        y = height // 2 - 180

        for text, color in lines:
            surface = self.font.render(text, True, color)
            screen.blit(surface, surface.get_rect(center=(width // 2, y)))
            y += 80

        self.start_button.draw(screen)
        self.back_button.draw(screen)
