import pygame

from systems.resource import resource_path

STAGE_COUNT = 10
STAGE_COLUMNS = 5


# =========================
# 難易度選択画面
# （ボタンの見た目は背景画像に描かれているので、当たり判定の矩形だけ持つ）
# =========================

class DiffMenuScene:

    def __init__(self, font, width, height, background):
        self.font = font
        self.background = background

        self.selected_stage = 1

        self.stage_rects = [pygame.Rect(0, 0, 180, 80) for _ in range(STAGE_COUNT)]
        self.start_rect = pygame.Rect(width // 2 - 100, height // 2 + 100, 285, 100)
        self.book_rect = pygame.Rect(width // 2 - 120, height - 280, 240, 80)
        self.help_rect = pygame.Rect(width // 2 - 415, height // 2 + 115, 130, 100)
        self.home_rect = pygame.Rect(20, 20, 240, 80)

        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_diffmenu.ogg"))
        self.start_se = pygame.mixer.Sound(resource_path("sounds/start.ogg"))
        self.help_se = pygame.mixer.Sound(resource_path("sounds/help.ogg"))

    def update_layout(self, width, height):
        # ステージボタン（5列 x 2行）
        button_w = 195
        button_h = 95

        gap_x = 27
        gap_y = 40

        start_x = width // 2 - (button_w * STAGE_COLUMNS + gap_x * (STAGE_COLUMNS - 1)) // 2 - 5
        start_y = height // 2 - 175

        for i, rect in enumerate(self.stage_rects):
            row = i // STAGE_COLUMNS
            col = i % STAGE_COLUMNS

            rect.topleft = (
                start_x + col * (button_w + gap_x),
                start_y + row * (button_h + gap_y)
            )
            rect.size = (button_w, button_h)

        self.start_rect.topleft = (width // 2 + 80, height // 2 + 115)
        self.start_rect.size = (285, 100)

        self.book_rect.topleft = (width // 2 - 255, height // 2 + 115)
        self.book_rect.size = (300, 100)

        self.help_rect.topleft = (width // 2 - 415, height // 2 + 115)
        self.help_rect.size = (130, 100)

        self.home_rect.topleft = (50, 40)
        self.home_rect.size = (270, 70)

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        for i, rect in enumerate(self.stage_rects):
            if rect.collidepoint(event.pos):
                self.selected_stage = i + 1
                self.select_se.play()
                return None

        if self.start_rect.collidepoint(event.pos):
            self.start_se.play()
            return {"action": "start", "stage": self.selected_stage}

        elif self.book_rect.collidepoint(event.pos):
            self.select_se.play()
            return {"action": "book"}

        elif self.help_rect.collidepoint(event.pos):
            self.help_se.play()
            return {"action": "help"}

        elif self.home_rect.collidepoint(event.pos):
            self.select_se.play()
            return {"action": "home"}

        return None

    def update(self):
        pass

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        bg = pygame.transform.smoothscale(self.background, (width, height))
        screen.blit(bg, (0, 0))

        # 選択中のステージを半透明の青で強調
        rect = self.stage_rects[self.selected_stage - 1]

        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (80, 180, 255, 120), overlay.get_rect(), border_radius=18)
        screen.blit(overlay, rect.topleft)
