import pygame

from objects.button import Button
from systems.resource import resource_path

# NORMAL / EXTRA ボタン
MODE_BUTTON_WIDTH = 240
MODE_BUTTON_HEIGHT = 60

# 両脇の正方形のボタン（ヘルプ / ランキング）。NORMAL と EXTRA の2段分の高さにする
SIDE_BUTTON_SIZE = 140
SIDE_BUTTON_GAP = 20
SIDE_BUTTON_FONT_SIZE = 26


# =========================
# ホーム画面
# =========================

class HomeScene:

    def __init__(self, font, width, height, background):
        self.font = font
        self.background = background

        self.normal_button = Button(0, 0, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT, "NORMAL", font)
        self.extra_button = Button(0, 0, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT, "EXTRA", font)

        # 「ランキング」が正方形に収まるよう、少し小さい文字にする
        side_font = pygame.font.Font(resource_path("fonts/MPLUS1p-Bold.ttf"), SIDE_BUTTON_FONT_SIZE)
        side_font.set_bold(True)

        self.help_button = Button(0, 0, SIDE_BUTTON_SIZE, SIDE_BUTTON_SIZE, "ヘルプ", side_font)
        self.ranking_button = Button(0, 0, SIDE_BUTTON_SIZE, SIDE_BUTTON_SIZE, "ランキング", side_font)

        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_home.ogg"))

        self.update_layout(width, height)

    def update_layout(self, width, height):
        self.normal_button.rect = pygame.Rect(width // 2 - 150, height - 260, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT)
        self.extra_button.rect = pygame.Rect(width // 2 - 150, height - 180, MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT)

        # NORMAL の上端から EXTRA の下端までの高さに合わせて、左右に並べる
        top = self.normal_button.rect.top

        self.help_button.rect = pygame.Rect(
            self.normal_button.rect.left - SIDE_BUTTON_GAP - SIDE_BUTTON_SIZE,
            top,
            SIDE_BUTTON_SIZE,
            SIDE_BUTTON_SIZE
        )
        self.ranking_button.rect = pygame.Rect(
            self.normal_button.rect.right + SIDE_BUTTON_GAP,
            top,
            SIDE_BUTTON_SIZE,
            SIDE_BUTTON_SIZE
        )

    def handle_event(self, event):
        """押されたボタンに応じて "normal" / "extra" / "help" / "ranking" を返す"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.normal_button.clicked(event.pos):
                self.select_se.play()
                return "normal"

            elif self.extra_button.clicked(event.pos):
                self.select_se.play()
                return "extra"

            elif self.help_button.clicked(event.pos):
                self.select_se.play()
                return "help"

            elif self.ranking_button.clicked(event.pos):
                self.select_se.play()
                return "ranking"

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        bg = pygame.transform.smoothscale(self.background, (width, height))
        screen.blit(bg, (0, 0))

        self.normal_button.draw(screen)
        self.extra_button.draw(screen)
        self.help_button.draw(screen)
        self.ranking_button.draw(screen)
