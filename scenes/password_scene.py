import pygame

from objects.button import Button
from objects.image_keyboard import PASSWORD_LAYOUT, ImageKeyboard, scale_rect
from systems.resource import resource_path

# 入力欄からはみ出さない文字数
MAX_LENGTH = 15

TEXT_COLOR = (60, 35, 20)
WARNING_COLOR = (200, 0, 0)

# 「不正なパスコードです」を表示する高さ（説明文と入力欄の間）
WARNING_Y = 350

# 警告の下地の色を取る場所（飾り線と重なって読みにくいので、羊皮紙の色の下地を敷く）
WARNING_PATCH_SAMPLE = (560, 345, 80, 10)

# 当たり判定を赤枠で表示する（位置合わせの確認用）
DEBUG_HITBOX = False


# =========================
# エクストラステージのパスワード入力画面
# （キーボード・説明文・入力欄は背景画像に描かれているので、当たり判定と入力文字だけを扱う）
# =========================

class PasswordScene:

    def __init__(self, font, width, height, password, background):
        self.font = font
        self.password = password
        self.background = background
        self.scaled_background = None

        self.text = ""

        self.message = ""
        self.warn_flg = False

        self.keyboard = ImageKeyboard(PASSWORD_LAYOUT["keys"], font, width, height)

        # 当たり判定だけのボタン（「ホームに戻る」は背景画像に描かれている）
        self.home_button = Button(0, 0, 0, 0, "ホームに戻る", font)

        self.warning_font = pygame.font.Font(resource_path("fonts/MPLUS1p-Bold.ttf"), 28)

        self.update_layout(width, height)

    def update_layout(self, width, height):
        self.keyboard.update_layout(width, height)
        self.home_button.rect = scale_rect(PASSWORD_LAYOUT["back"], width, height)
        self.text_area = scale_rect(PASSWORD_LAYOUT["text_area"], width, height)

    def handle_event(self, event):
        """OK で入力文字列を、ホームボタンで "home" を返す"""
        key = self.keyboard.handle_event(event)

        if key == "<-":
            self.text = self.text[:-1]

        elif key == "OK":
            if self.text == self.password:
                self.warn_flg = False
                return self.password
            else:
                self.message = "不正なパスコードです"
                self.warn_flg = True

        elif key is not None:
            if len(self.text) < MAX_LENGTH:
                self.text += key

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.home_button.clicked(event.pos):
                self.text = ""
                return "home"

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)
        self.draw_background(screen, width, height)

        # 入力した文字（背景の入力欄の内側に書く）
        text = self.font.render(self.text, True, TEXT_COLOR)
        screen.blit(text, text.get_rect(midleft=(self.text_area.x + 10, self.text_area.centery)))

        if self.warn_flg:
            warning = self.warning_font.render(self.message, True, WARNING_COLOR)
            rect = warning.get_rect(center=(width // 2, WARNING_Y * height / 1080))

            pygame.draw.rect(screen, self.warning_patch_color, rect.inflate(30, 6), border_radius=8)
            screen.blit(warning, rect)

        if DEBUG_HITBOX:
            self.keyboard.draw(screen, debug=True)
            pygame.draw.rect(screen, (255, 0, 0), self.home_button.rect, 2)
            pygame.draw.rect(screen, (0, 120, 255), self.text_area, 2)

    def draw_background(self, screen, width, height):
        if self.scaled_background is None or self.scaled_background.get_size() != (width, height):
            if self.background.get_size() == (width, height):
                self.scaled_background = self.background
            else:
                self.scaled_background = pygame.transform.smoothscale(self.background, (width, height))

            sample = scale_rect(WARNING_PATCH_SAMPLE, width, height)
            self.warning_patch_color = pygame.transform.average_color(self.scaled_background, sample)

        screen.blit(self.scaled_background, (0, 0))
