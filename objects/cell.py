import pygame
import random
import math

# =========================
# 細胞クラス
# =========================

class Cell:

    def __init__(self, x, y, image, width, height, cell_name=None, display_name=None, is_target=False):

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.radius = max(width, height) / 2

        self.found = False

        angle = random.uniform(0, 360)

        # size = radius * 2

        scaled = pygame.transform.smoothscale(
            image,
            (width, height)
        )

        self.source_image = image

        self.image = pygame.transform.rotate(
            scaled,
            angle
        )

        self.rect = self.image.get_rect(center=(x, y))
        self.image_cache = {}

        self.is_target = is_target

        self.cell_name = cell_name

        self.display_name = display_name

        self.can_count = True

    def draw(self, screen, camera_x, camera_y, width, height, zoom):

        # ワールド座標から画面座標に変換
        draw_x = (self.x - camera_x) * zoom
        draw_y = (self.y - camera_y) * zoom

        # キャッシュ用キー
        zoom_key = round(zoom * 10) / 10

        # 拡大後サイズ
        scaled_size = max(
            1,
            int(self.radius * 2 * zoom_key)
        )

        # キャッシュになければ生成
        if zoom_key not in self.image_cache:

            scaled_image = pygame.transform.scale(
                self.image,
                (scaled_size, scaled_size)
            )

            self.image_cache[zoom_key] = scaled_image

            if len(self.image_cache) > 30:
                self.image_cache.clear()

        # キャッシュから取得
        scaled_image = self.image_cache[zoom_key]

        # 描画位置
        rect = scaled_image.get_rect(
            center=(draw_x, draw_y)
        )

        if self.found:
            pygame.draw.circle(
                screen,
                (255, 255, 0),
                (int(draw_x), int(draw_y)),
                int(self.radius * zoom + 8),
                4
            )

        # 画面外なら描画しない
        if (
            rect.right < 0 or
            rect.left > width or
            rect.bottom < 0 or
            rect.top > height
        ):
            return

        screen.blit(scaled_image, rect)


    def clicked(self, pos):

        dx = pos[0] - self.x
        dy = pos[1] - self.y

        dist = math.sqrt(dx * dx + dy * dy)

        return dist <= self.radius