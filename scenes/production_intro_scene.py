import pygame

from objects.button import Button
from objects.image_keyboard import scale_rect

# 背景画像（images/background/production_intro.jpg）に描かれたボタンの位置 (x, y, w, h)
BACK_BUTTON = (150, 175, 282, 95)       # 「選択画面に戻る」
START_BUTTON = (640, 840, 640, 140)     # 「本番へ進む」

# 当たり判定を赤枠で表示する（位置合わせの確認用）
DEBUG_HITBOX = False


# =========================
# 本番前の案内画面
# （エクストラの選択画面で「本番問題」を選んだ時に表示する）
# 説明文とボタンは背景画像に描かれているので、透明な当たり判定だけを持つ
# =========================

class ProductionIntroScene:

    def __init__(self, font, width, height, total_questions, background=None):
        """background: 説明文とボタンが描かれた背景（無ければ白い背景に文字とボタンを描く）"""
        self.font = font
        self.total_questions = total_questions

        self.background = background
        self.scaled_background = None

        self.start_button = Button(width // 2 - 150, height // 2 + 150, 300, 80, "本番へ進む", font)
        self.back_button = Button(10, 10, 270, 70, "選択画面に戻る", font)

        self.update_layout(width, height)

    def update_layout(self, width, height):
        if self.background is not None:
            self.start_button.rect = scale_rect(START_BUTTON, width, height)
            self.back_button.rect = scale_rect(BACK_BUTTON, width, height)
        else:
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

        if self.background is not None:
            if self.scaled_background is None or self.scaled_background.get_size() != (width, height):
                if self.background.get_size() == (width, height):
                    self.scaled_background = self.background
                else:
                    self.scaled_background = pygame.transform.smoothscale(self.background, (width, height))

            screen.blit(self.scaled_background, (0, 0))

            if DEBUG_HITBOX:
                pygame.draw.rect(screen, (255, 0, 0), self.start_button.rect, 3)
                pygame.draw.rect(screen, (255, 0, 0), self.back_button.rect, 3)

            return

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
