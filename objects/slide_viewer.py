import pygame

from systems.resource import resource_path

# スライド画像の基準サイズ（ボタンの位置はこのサイズの座標で指定する）
BASE_WIDTH = 1920
BASE_HEIGHT = 1080


# =========================
# スライド表示
# （画像に描かれている「戻る」「次へ進む」「閉じる」を当たり判定で押せるようにする）
# =========================

class SlideViewer:

    def __init__(self, slides):
        """slides: [{"image": Surface, "buttons": {"prev" | "next" | "close": (x, y, w, h)}}, ...]"""
        self.slides = slides
        self.current_page = 0
        self.scaled_cache = {}

        self.page_se = pygame.mixer.Sound(resource_path("sounds/page.ogg"))
        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_diffmenu.ogg"))

    def open(self):
        self.current_page = 0

    def get_button_rect(self, rect, width, height):
        """基準サイズの座標を、現在の画面サイズに合わせて変換する"""
        x, y, w, h = rect
        sx = width / BASE_WIDTH
        sy = height / BASE_HEIGHT

        return pygame.Rect(x * sx, y * sy, w * sx, h * sy)

    def handle_event(self, event, width, height):
        """閉じるボタンが押されたら "close" を返す"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        buttons = self.slides[self.current_page]["buttons"]

        for action, rect in buttons.items():
            if not self.get_button_rect(rect, width, height).collidepoint(event.pos):
                continue

            if action == "prev" and self.current_page > 0:
                self.page_se.play()
                self.current_page -= 1

            elif action == "next" and self.current_page < len(self.slides) - 1:
                self.page_se.play()
                self.current_page += 1

            elif action == "close":
                self.select_se.play()
                return "close"

            break

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        key = (self.current_page, width, height)

        # 拡大縮小した画像は使い回す
        if key not in self.scaled_cache:
            image = self.slides[self.current_page]["image"]
            self.scaled_cache[key] = pygame.transform.smoothscale(image, (width, height))

        screen.blit(self.scaled_cache[key], (0, 0))
