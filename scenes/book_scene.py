import pygame

from objects.button import Button
from systems.resource import resource_path


# =========================
# 図鑑画面
# =========================

class BookScene:

    def __init__(self, font, width, height, images):
        self.font = font
        self.images = images

        self.current_page = 0

        self.back_button = Button(20, 20, 180, 60, "戻る", font)
        self.prev_button = Button(width // 2 - 140, height - 85, 80, 60, "前へ", font)
        self.next_button = Button(width // 2 + 60, height - 85, 80, 60, "次へ", font)

        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_diffmenu.ogg"))
        self.page_se = pygame.mixer.Sound(resource_path("sounds/page.ogg"))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.clicked(event.pos):
                self.select_se.play()
                return "menu"

            elif self.prev_button.clicked(event.pos):
                self.page_se.play()

                if self.current_page > 0:
                    self.current_page -= 1

            elif self.next_button.clicked(event.pos):
                self.page_se.play()

                if self.current_page < len(self.images) - 1:
                    self.current_page += 1

    def draw(self, screen):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        # 画像は高さに合わせて拡大縮小し、左右中央に置く
        image = self.images[self.current_page]

        new_h = height - 100
        scale = new_h / image.get_height()
        new_w = int(image.get_width() * scale)

        scaled_image = pygame.transform.smoothscale(image, (new_w, new_h))
        screen.blit(scaled_image, ((width - new_w) // 2, 0))

        page = self.font.render(
            f"{self.current_page + 1} / {len(self.images)}",
            True,
            (0, 0, 0)
        )
        screen.blit(page, page.get_rect(center=(width // 2, height - 50)))

        self.back_button.draw(screen)

        if self.current_page > 0:
            self.prev_button.draw(screen)

        if self.current_page < len(self.images) - 1:
            self.next_button.draw(screen)
