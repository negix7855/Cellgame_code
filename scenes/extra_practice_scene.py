import pygame
import random
from objects.button import Button
from systems.load_distribution import load_distribution

class ExtraPracticeScene:

    def __init__(self, font, width, height, world_data, found_cells):
        
        self.wrold_data = world_data

        self.font = font

        self.width = width
        self.height = height

        self.found_cells = found_cells

        self.buttons = []

        self.current_index = 0
        self.current_cell = None

        self.answers = None

        self.message = ""
        self.message_timer = 0

        self.wait_next = False

        self.finished = False
        self.passed = False

        distribution = load_distribution(
            f"data/practice/world{world_data}.csv"
        )

        self.cell_names = [
            info["display_name"]
            for info in distribution
        ]

        self.question_number = 1
        self.total_question = len(self.cell_names)
        self.streak = 0
        self.correct_count = 0

        self.PASS_SCORE = int(self.total_question * 0.8)

        self.result_button = None

        self.question_cells = self.found_cells.copy()
        random.shuffle(self.question_cells)

        self.make_question()

    def make_question(self):

        self.answer_buttons = []

        self.current_cell = self.question_cells[self.current_index]
        self.correct = self.current_cell.display_name

        choices = []

        for name in self.cell_names:

            if name != self.correct:
                choices.append(name)

        wrong = random.sample(choices, 3)

        self.answers = wrong

        self.answers.append(self.correct)

        random.shuffle(self.answers)

        start_y = self.height // 2 - 140

        for i in range(4):

            button = Button(
                200,
                start_y + i*70,
                500,
                60,
                self.answers[i],
                self.font
            )

            self.answer_buttons.append(button)

    def update(self):

        if self.message_timer > 0:
            self.message_timer -= 1

            if self.message_timer == 0 and self.wait_next:

                self.wait_next = False
                self.question_number += 1
                self.current_index += 1

                if self.current_index >= self.total_question:
                    self.finished = True

                    if self.correct_count >= self.PASS_SCORE:
                        self.passed = True
                        self.result_button = Button(
                            self.width//2-150, self.height//2, 300, 70,
                            "次の世界へ！",
                            self.font
                        )

                    else:
                        self.result_button = Button(
                            self.width//2-150, self.height//2, 300, 70,
                            "もう一度探索へ",
                            self.font
                        )

                    return

                else:
                    self.make_question()


    def handle_event(self, event):

        if self.wait_next:
            return
        
        if self.finished:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.result_button.clicked(event.pos):

                        if self.passed:
                            return "next_world"
                        
                        else:
                            return "retry"

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                for button in self.answer_buttons:

                    if button.clicked(event.pos):

                        print(button.text)

                        if button.text == self.correct:
                            print("正解")
                            self.message = "正解！"
                            self.streak += 1
                            self.correct_count += 1

                        else:
                            print("不正解")
                            self.message = "不正解..."
                            self.streak = 0

                        self.message_timer = 90
                        self.wait_next = True
                        break

    def draw(self, screen):

        width, height = screen.get_size()

        if self.finished:

            screen.fill((255,255,255))

            text = self.font.render(
                f"{self.correct_count} / {self.total_question}問正解",
                True,
                (0,0,0)
            )

            screen.blit(text, text.get_rect(center=(self.width//2, 200)))

            if self.passed:

                result = self.font.render(
                    "合格！",
                    True,
                    (0, 150, 0)
                )

            else:

                result = self.font.render(
                    "不合格...",
                    True,
                    (200,0,0)
                )

            screen.blit(result, result.get_rect(center=(self.width//2, 300)))

            self.result_button.draw(screen)

            return

        screen.fill((255,255,255))

        if self.streak > 1:

            text = self.font.render(
                f"{self.streak}問連続正解",
                True,
                (0,0,0)
            )

            text_rect = text.get_rect(
                center=(width // 2, 200)
            )

            screen.blit(text, text_rect)

        text = self.font.render(
            f"{self.question_number}/{self.total_question} この細胞の名前は？",
            True,
            (0,0,0)
        )

        text_rect = text.get_rect(
            center=(width // 2, 250)
        )

        screen.blit(text, text_rect)

        image = pygame.transform.smoothscale(
            self.current_cell.source_image,
            (300, 300)
        )

        rect = image.get_rect(
            center=(
                width // 2,
                height // 2
            )
        )

        screen.blit(image, rect)

        for button in self.answer_buttons:
            button.draw(screen)

        if self.message_timer > 0:

            text = self.font.render(
                self.message,
                True,
                (0,0,0)
            )

            screen.blit(
                text,
                text.get_rect(center=(self.width // 2, 150))
            )
