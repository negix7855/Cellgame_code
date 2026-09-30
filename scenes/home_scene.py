import pygame

from objects.button import Button
from systems.resource import resource_path


# =========================
# ホーム画面
# =========================

class HomeScene:

    def __init__(self, font, width, height, background):
        self.font = font
        self.background = background

        self.normal_button = Button(width // 2 - 120, height - 300, 240, 60, "NORMAL", font)
        self.extra_button = Button(width // 2 - 120, height - 180, 240, 60, "EXTRA", font)

        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_home.ogg"))

    def update_layout(self, width, height):
        self.normal_button.rect = pygame.Rect(width // 2 - 150, height - 260, 240, 60)
        self.extra_button.rect = pygame.Rect(width // 2 - 150, height - 180, 240, 60)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.normal_button.clicked(event.pos):
                self.select_se.play()
                return "normal"

            elif self.extra_button.clicked(event.pos):
                self.select_se.play()
                return "extra"

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        bg = pygame.transform.smoothscale(self.background, (width, height))
        screen.blit(bg, (0, 0))

        self.normal_button.draw(screen)
        self.extra_button.draw(screen)
