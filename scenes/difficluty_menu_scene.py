import pygame
import os

from objects.button import Button

def resource_path(relative_path):
    return os.path.join(os.path.abspath("."), relative_path)

class DiffMenuScene:

    def __init__(self, font, width, height, background):

        self.font = font

        self.background = background

        self.stage_rects = []

        # for i in range(10):
        #     button = Button(
        #         0,
        #         0,
        #         180, 80,
        #         f"LEVEL {i+1}",
        #         font
        #     )
        #     self.stage_buttons.append(button)

        for _ in range(10):
            self.stage_rects.append(
                pygame.Rect(0, 0, 180, 80)
            )

        self.selected_stage = 1

        # self.start_button = Button(
        #     width // 2 - 100,
        #     height // 2 + 100,
        #     200,
        #     80,
        #     "開始",
        #     font
        # )

        self.start_rect = pygame.Rect(
            width // 2 - 100,
            height // 2 + 100,
            285,
            100
        )

        # self.book_button = Button(
        #     width // 2 - 120,
        #     height - 280,
        #     240,
        #     80,
        #     "図鑑",
        #     font
        # )

        self.book_rect = pygame.Rect(
            width // 2 - 120,
            height - 280,
            240,
            80
        )

        # self.home_button = Button(
        #     20,
        #     20,
        #     240,
        #     80,
        #     "ホームに戻る",
        #     font
        # )

        self.home_rect = pygame.Rect(
            20,
            20,
            240,
            80
        )

        self.select_diffmenu = pygame.mixer.Sound(
            resource_path("sounds/select_diffmenu.ogg")
        )

        self.start = pygame.mixer.Sound(
            resource_path("sounds/start.ogg")
        )

        self.help = pygame.mixer.Sound(
            resource_path("sounds/help.ogg")
        )



    def update_layout(self, width, height):

        button_w = 195
        button_h = 95

        gap_x = 27
        gap_y = 40

        start_x = width // 2 - (button_w * 5 + gap_x * 4) // 2 - 5
        start_y = height // 2 - 175

        # for i, button in enumerate(self.stage_buttons):

        #     row = i // 5
        #     col = i % 5

        #     x = start_x + col * (button_w + gap_x)
        #     y = start_y + row * (button_h + gap_y)

        #     button.rect = pygame.Rect(
        #         x,
        #         y,
        #         button_w,
        #         button_h
        #     )

        for i in range(10):

            row = i // 5
            col = i % 5

            x = start_x + col * (button_w + gap_x)
            y = start_y + row * (button_h + gap_y)

            self.stage_rects[i].topleft = (x, y)
            self.stage_rects[i].size = (button_w, button_h)

        # self.start_button.rect = pygame.Rect(
        #     width // 2 + 80,
        #     height // 2 + 115,
        #     285,
        #     100
        # )

        self.start_rect.topleft = (
            width // 2 + 80,
            height // 2 + 115
        )
        self.start_rect.size = (
            285,
            100
        )

        # self.book_button.rect = pygame.Rect(
        #     width // 2 - 255,
        #     height // 2 + 115,
        #     300,
        #     100
        # )

        self.book_rect.topleft = (
            width // 2 - 255,
            height // 2 + 115
        )
        self.book_rect.size = (
            300,
            100
        )

        # self.home_button.rect = pygame.Rect(
        #     50,
        #     40,
        #     270,
        #     70
        # )

        self.home_rect.topleft = (
            50,
            40
        )
        self.home_rect.size = (
            270,
            70
        )



    def handle_event(self, event):

        if (
            event.type == pygame.MOUSEBUTTONDOWN and
            event.button == 1
        ):

            # for i, button in enumerate(self.stage_buttons):

            #     if button.clicked(event.pos):
            #         self.selected_stage = i + 1
            #         return None

            for i, rect in enumerate(self.stage_rects):

                if rect.collidepoint(event.pos):
                    self.selected_stage = i + 1
                    self.select_diffmenu.play()
                    return None

            # if self.start_button.clicked(event.pos):

            #     return {
            #         "action": "start",
            #         "stage": self.selected_stage
            #     }

            if self.start_rect.collidepoint(event.pos):

                self.start.play()

                return {
                    "action": "start",
                    "stage": self.selected_stage
                }

            # elif self.book_button.clicked(event.pos):

            #     return{
            #         "action": "book"
            #     }

            elif self.book_rect.collidepoint(event.pos):

                self.select_diffmenu.play()

                return {
                    "action": "book"
                }

            # elif self.home_button.clicked(event.pos):

            #     return {
            #         "action": "home"
            #     }

            elif self.home_rect.collidepoint(event.pos):

                self.select_diffmenu.play()

                return {
                    "action": "home"
                }

            return None

    def update(self):
        pass

    def draw(self, screen):

        width, height = screen.get_size()

        self.update_layout(width, height)

        bg = pygame.transform.smoothscale(
            self.background,
            (width, height)
        )
        screen.blit(bg, (0,0))

        # for i, button in enumerate(self.stage_buttons):

        #     if self.selected_stage == i + 1:
        #         color = (100, 200, 255)
        #     else:
        #         color = (220, 220, 220)

        #     button.draw(screen, color)

        for i, rect in enumerate(self.stage_rects):

            if self.selected_stage == i + 1:

                overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    overlay,
                    (80, 180, 255, 120),
                    overlay.get_rect(),
                    border_radius=18
                )
                screen.blit(overlay, rect.topleft)

        # self.start_button.draw(screen)
        # self.book_button.draw(screen)
        # self.home_button.draw(screen)
