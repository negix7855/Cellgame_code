import pygame


# =========================
# テキスト入力欄
# =========================

class TextBox:

    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font

        self.text = ""
        self.active = False

    def clear(self):
        self.text = ""

    def handle_event(self, event):
        """Enter が押されたら入力中の文字列を返す"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN:
            if not self.active:
                return None

            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_RETURN:
                return self.text

            else:
                self.text += event.unicode

    def draw(self, screen):
        if self.active:
            color = (255, 255, 255)
            border = (50, 120, 255)
        else:
            color = (235, 235, 235)
            border = (100, 100, 100)

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border, self.rect, 3, border_radius=8)

        text_surface = self.font.render(self.text, True, (0, 0, 0))

        screen.blit(
            text_surface,
            (
                self.rect.x + 10,
                self.rect.centery - text_surface.get_height() // 2
            )
        )
