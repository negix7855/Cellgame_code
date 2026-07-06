import pygame
import random
from objects.button import Button
from systems.load_distribution import load_distribution

class ExtraPracticeScene:

    def __init__(self, font, width, height, world_data, found_cells):
        
        self.wrold_data = world_data

        self.font = font

        self.found_cells = found_cells

        self.buttons = []

        self.current_cell = None

        self.answers = None

        distribution = load_distribution(
            f"data/practice/world{world_data}.csv"
        )

        self.cell_names = [
            info["display_name"]
            for info in distribution
        ]

        self.make_question()

        self.answer_rects = []

        start_y = 450

        for i in range(4):

            rect = pygame.Rect(
                200,
                start_y + i*70,
                500,
                55
            )

            self.answer_rects.append(rect)

    def make_question(self):

        self.current_cell = random.choice(
            self.found_cells
        )

        correct = self.current_cell.display_name

        choices = []

        for name in self.cell_names:

            if name != correct:
                choices.append(name)

        wrong = random.sample(choices, 3)

        self.answers = wrong

        self.answers.append(correct)

        random.shuffle(self.answers)

    def draw(self, screen):

        width, height = screen.get_size()

        screen.fill((255,255,255))

        image = self.current_cell.image

        rect = image.get_rect(
            center=(
                width//2,
                height//2
            )
        )

        for rect, answer in zip(
            self.answer_rects,
            self.answers
        ):
            
            pygame.draw.rect(
                screen,
                (240, 240, 240),
                rect,
                border_radius=10
            )

            text = self.font.render(
                answer,
                True,
                (0,0,0)
            )

            screen.blit(
                text,
                text.get_rect(center=rect.center)
            )

        screen.blit(image, rect)
