import pygame

class LoadingScene:

    def __init__(self, font):
        self.font = font
        self.progress = 0.0

    def set_progressa(self, progress):
        self.progress = max(0.0, min(progress, 1.0))

    def draw(self, screen):

        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        text = self.font.render(
            f"NOW LOADING...{int(self.progress*100)}%",
            True,
            (0, 0, 0)
        )

        rect = text.get_rect(
            bottomright=(width - 100,
            height - 50)
        )

        screen.blit(text, rect)

        bar_w = 350
        bar_h = 30

        x = width - 450
        y = height - 40

        pygame.draw.rect(
            screen,
            (180, 180, 180),
            (x, y, bar_w, bar_h),
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            (80, 180, 255),
            (x, y, int(bar_w*self.progress), bar_h),
            border_radius=15
        )