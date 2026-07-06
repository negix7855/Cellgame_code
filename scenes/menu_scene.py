import pygame

from objects.button import Button

class MenuScene:

    def __init__(self, font, width, height):

        self.font = font

        self.normal_cell_count = 100
        self.abnormal_cell_count = 5

        self.normal_minus_button = Button(
            250, 300, 80, 80, "-", font
        )

        self.normal_plus_button = Button(
            550, 300, 80, 80, "+", font
        )

        self.abnormal_minus_button = Button(
            250, 420, 80, 80, "-", font
        )

        self.abnormal_plus_button = Button(
            550, 420, 80, 80, "+", font
        )

        self.start_button = Button(
            width // 2 - 100,
            height // 2 + 100,
            200,
            60,
            "開始",
            font
        )



    def update_layout(self, width, height):

        button_w = max(80, width // 12)
        button_h = max(60, height // 14)

        row_gap = height // 7

        center_x = width // 2

        self.normal_minus_button.rect = pygame.Rect(
            center_x + 80,
            height // 3,
            button_w,
            button_h
        )

        self.normal_plus_button.rect = pygame.Rect(
            center_x + 200,
            height // 3,
            button_w,
            button_h
        )

        self.abnormal_minus_button.rect = pygame.Rect(
            center_x + 80,
            height // 3 + row_gap,
            button_w,
            button_h
        )

        self.abnormal_plus_button.rect = pygame.Rect(
            center_x + 200,
            height // 3 + row_gap,
            button_w,
            button_h
        )

        self.start_button.rect = pygame.Rect(
            width // 2 - 120,
            height - 180,
            240,
            80
        )



    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                NORMAL_CELL_COUNT += 100

            elif event.key == pygame.K_DOWN:
                NORMAL_CELL_COUNT = max(
                    100,
                    NORMAL_CELL_COUNT - 100
                )

            elif event.key == pygame.K_RIGHT:
                ABNORMAL_CELL_COUNT += 1

            elif event.key == pygame.K_LEFT:
                ABNORMAL_CELL_COUNT = max(
                    1,
                    ABNORMAL_CELL_COUNT - 1
                )

        elif (
            event.type == pygame.MOUSEBUTTONDOWN and
            event.button == 1
        ):

            if self.normal_plus_button.clicked(event.pos):

                self.normal_cell_count += 100

            elif self.normal_minus_button.clicked(event.pos):

                self.normal_cell_count = max(
                    100,
                    self.normal_cell_count - 100
                )

            elif self.abnormal_plus_button.clicked(event.pos):

                self.abnormal_cell_count += 1

            elif self.abnormal_minus_button.clicked(event.pos):

                self.abnormal_cell_count = max(
                    1,
                    self.abnormal_cell_count - 1
                )

            elif self.start_button.clicked(event.pos):

                return {
                    "action": "start",
                    "normal_count": self.normal_cell_count,
                    "abnormal_count": self.abnormal_cell_count
                }
            
            return None

    def update(self):
        pass

    def draw(self, screen):

        width, height = screen.get_size()

        self.update_layout(width, height)

        screen.fill((255, 255, 255))

        title = self.font.render(
            "おるっちゃ",
            True,
            (0, 0, 0)
        )

        title_rect = title.get_rect(
            center=(width // 2, height // 6)
        )

        screen.blit(title, title_rect)

        label_y = height // 3

        label = self.font.render(
            "正常細胞数",
            True,
            (0, 0, 0)
        )

        value = self.font.render(
            str(self.normal_cell_count),
            True,
            (0, 0, 0)
        )

        label_rect = label.get_rect(
            center=(width // 2 - 220, label_y + 35)
        )

        value_rect = value.get_rect(
            center=(width // 2, label_y + 35)
        )

        screen.blit(label, label_rect)
        screen.blit(value, value_rect)

        row_gap = height // 7

        abnormal_y = height // 3 + row_gap

        ab_label = self.font.render(
            "異常細胞数",
            True,
            (0, 0, 0)
        )

        ab_value = self.font.render(
            str(self.abnormal_cell_count),
            True,
            (0, 0, 0)
        )

        ab_label_rect = ab_label.get_rect(
            center=(width // 2 - 220, abnormal_y + 35)
        )

        ab_value_rect = ab_value.get_rect(
            center=(width // 2, abnormal_y + 35)
        )

        screen.blit(ab_label, ab_label_rect)
        screen.blit(ab_value, ab_value_rect)

        self.normal_minus_button.draw(screen)
        self.normal_plus_button.draw(screen)

        self.abnormal_minus_button.draw(screen)
        self.abnormal_plus_button.draw(screen)

        self.start_button.draw(screen)
