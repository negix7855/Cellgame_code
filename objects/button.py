import pygame

# =========================
# ボタンクラス
# =========================
class Button:
    def __init__(self, x, y, w, h, text, font):

        self.rect = pygame.Rect(x, y, w, h)

        self.text = text

        self.font = font

    def draw(self, screen, color=(180, 180, 180)):
        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            (50, 50, 50),
            self.rect,
            3,
            border_radius=10
        )

        text_surface = self.font.render(
            self.text,
            True,
            (0, 0, 0)
        )

        text_rect = text_surface.get_rect(
            center=self.rect.center
        )

        screen.blit(text_surface, text_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)
