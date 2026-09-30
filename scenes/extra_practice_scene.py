import random

import pygame

from objects.button import Button
from systems.load_distribution import load_distribution

CHOICE_COUNT = 4
PASS_RATE = 0.8
MESSAGE_DURATION = 90


# =========================
# エクストラモードの練習問題画面
# （探索で見つけた細胞の名前を4択で答える）
# =========================

class ExtraPracticeScene:

    def __init__(self, font, width, height, world_data, found_cells):
        self.font = font

        self.width = width
        self.height = height

        self.world_data = world_data

        distribution = load_distribution(f"data/practice/world{world_data}.csv")

        self.cell_names = [info["display_name"] for info in distribution]

        # 出題
        self.question_cells = found_cells.copy()
        random.shuffle(self.question_cells)

        self.current_index = 0
        self.question_number = 1
        self.total_question = len(self.cell_names)

        self.current_cell = None
        self.correct = None
        self.answers = None
        self.answer_buttons = []

        # 成績
        self.streak = 0
        self.correct_count = 0
        self.pass_score = int(self.total_question * PASS_RATE)

        self.finished = False
        self.passed = False
        self.result_button = None

        # 正解・不正解の表示
        self.message = ""
        self.message_timer = 0
        self.wait_next = False

        self.make_question()

    def make_question(self):
        self.current_cell = self.question_cells[self.current_index]
        self.correct = self.current_cell.display_name

        choices = [name for name in self.cell_names if name != self.correct]

        self.answers = random.sample(choices, CHOICE_COUNT - 1)
        self.answers.append(self.correct)
        random.shuffle(self.answers)

        start_y = self.height // 2 - 140

        self.answer_buttons = [
            Button(200, start_y + i * 70, 500, 60, answer, self.font)
            for i, answer in enumerate(self.answers)
        ]

    def finish(self):
        self.finished = True
        self.passed = self.correct_count >= self.pass_score

        label = "次の世界へ！" if self.passed else "もう一度探索へ"

        self.result_button = Button(
            self.width // 2 - 150, self.height // 2, 300, 70,
            label,
            self.font
        )

    # =========================
    # 更新
    # =========================

    def update(self):
        if self.message_timer <= 0:
            return

        self.message_timer -= 1

        # メッセージを表示し終えたら次の問題へ
        if self.message_timer == 0 and self.wait_next:
            self.wait_next = False
            self.question_number += 1
            self.current_index += 1

            if self.current_index >= self.total_question:
                self.finish()
            else:
                self.make_question()

    # =========================
    # イベント処理
    # =========================

    def handle_event(self, event):
        if self.wait_next:
            return None

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if self.finished:
            if self.result_button.clicked(event.pos):
                return "next_world" if self.passed else "retry"

        for button in self.answer_buttons:
            if button.clicked(event.pos):
                if button.text == self.correct:
                    self.message = "正解！"
                    self.streak += 1
                    self.correct_count += 1
                else:
                    self.message = "不正解..."
                    self.streak = 0

                self.message_timer = MESSAGE_DURATION
                self.wait_next = True
                break

        return None

    # =========================
    # 描画
    # =========================

    def draw(self, screen):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        if self.finished:
            self.draw_result(screen)
            return

        if self.streak > 1:
            text = self.font.render(f"{self.streak}問連続正解", True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(width // 2, 200)))

        text = self.font.render(
            f"{self.question_number}/{self.total_question} この細胞の名前は？",
            True,
            (0, 0, 0)
        )
        screen.blit(text, text.get_rect(center=(width // 2, 250)))

        image = pygame.transform.smoothscale(self.current_cell.source_image, (300, 300))
        screen.blit(image, image.get_rect(center=(width // 2, height // 2)))

        for button in self.answer_buttons:
            button.draw(screen)

        if self.message_timer > 0:
            text = self.font.render(self.message, True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(self.width // 2, 150)))

    def draw_result(self, screen):
        text = self.font.render(
            f"{self.correct_count} / {self.total_question}問正解",
            True,
            (0, 0, 0)
        )
        screen.blit(text, text.get_rect(center=(self.width // 2, 200)))

        if self.passed:
            result = self.font.render("合格！", True, (0, 150, 0))
        else:
            result = self.font.render("不合格...", True, (200, 0, 0))

        screen.blit(result, result.get_rect(center=(self.width // 2, 300)))

        self.result_button.draw(screen)
