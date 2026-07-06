import pygame
import os
from objects.button import Button

def resource_path(relative_path):
    return os.path.join(os.path.abspath("."), relative_path)

class BookScene:

    def __init__(self, font, width, height, images):
        
        self.font = font
        self.images = images

        self.current_page = 0

        self.back_button = Button(
            20,
            20,
            180,
            60,
            "戻る",
            font
        )

        self.prev_button = Button(
            width // 2 - 140,
            height - 85,
            80,
            60,
            "前へ",
            font
        )

        self.next_button = Button(
            width // 2 + 60,
            height - 85,
            80,
            60,
            "次へ",
            font
        )

        self.select_se = pygame.mixer.Sound(
            resource_path("sounds/select_diffmenu.ogg")
        )

        self.page_se = pygame.mixer.Sound(
            resource_path("sounds/page.ogg")
        )

    def update_layout(self, width, height):
        self.back_button.rect = pygame.Rect(
            20,
            20,
            180,
            60
        )

        self.prev_button.rect = pygame.Rect(
            width // 2 - 140,
            height - 100,
            80,
            60
        )

        self.next_button.rect = pygame.Rect(
            width // 2 + 60,
            height - 100,
            80,
            60
        )

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

                if self.current_page < 7:
                    self.current_page += 1


    def draw(self, screen):

        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        image = self.images[self.current_page]

        img_w = image.get_width()
        img_h = image.get_height()

        new_h = height - 100
        scale = new_h / img_h
        new_w = int(img_w * scale)

        scaled_image = pygame.transform.smoothscale(
            image,
            (new_w, new_h)
        )

        screen.blit(scaled_image,((width - new_w) // 2, 0))

        page = self.font.render(
            f"{self.current_page+1} / {len(self.images)}",
            True,
            (0,0,0)
        )
        page_rect = page.get_rect(
            center=(width // 2, height - 50)
        )

        screen.blit(page, page_rect)

        self.back_button.draw(screen)

        if self.current_page > 0:
            self.prev_button.draw(screen)

        if self.current_page < len(self.images) - 1:
            self.next_button.draw(screen)



