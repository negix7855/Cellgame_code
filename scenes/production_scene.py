import time

import pygame

from objects.button import Button
from scenes.world_scene import WorldScene

# 本番で出題する症例数（data/exam/case1.csv 〜 case5.csv）
EXAM_CASE_COUNT = 5

# 症例番号と正解の対応
CASE_ANSWERS = {
    1: "NILM 正常",
    2: "NILM 感染症・炎症",
    3: "LSIL",
    4: "HSIL",
    5: "SCC",
}

ANSWER_CHOICES = list(CASE_ANSWERS.values())


# =========================
# 本番（症例判定）画面
# （細胞の分布を観察して、症例を5択で答える）
# =========================

class ProductionScene(WorldScene):

    MAX_ZOOM = 3.0

    def __init__(
            self,
            font,
            width,
            cells,
            grid,
            world_width,
            world_height,
            distribution,
            case_number,
            question_number,
            total_questions
        ):
        super().__init__(font, width, cells, grid, world_width, world_height)

        self.minimap_bottom_margin = self.minimap_margin * 10

        self.distribution = distribution

        self.case_number = case_number
        self.correct_answer = CASE_ANSWERS[case_number]

        self.question_number = question_number
        self.total_questions = total_questions

        # 回答
        self.answered = False
        self.player_answer = None
        self.is_correct = False

        self.answer_buttons = [
            Button(width - 340, 100 + i * 70, 320, 60, answer, font)
            for i, answer in enumerate(ANSWER_CHOICES)
        ]

        is_last = question_number >= total_questions
        next_label = "結果を見る" if is_last else "次の問題へ"

        self.next_button = Button(width // 2 - 150, 220, 300, 70, next_label, font)

    def update_layout(self, width, height):
        for i, button in enumerate(self.answer_buttons):
            button.rect = pygame.Rect(width - 340, 100 + i * 70, 320, 60)

        self.next_button.rect = pygame.Rect(width // 2 - 150, 220, 300, 70)

    def get_result(self):
        """この問題の結果（main で集計する）"""
        return {
            "question_number": self.question_number,
            "case_number": self.case_number,
            "correct_answer": self.correct_answer,
            "player_answer": self.player_answer,
            "is_correct": self.is_correct,
        }

    # =========================
    # イベント処理
    # =========================

    def handle_left_click(self, pos):
        if self.answered:
            if self.next_button.clicked(pos):
                return "next"

            return None

        for button in self.answer_buttons:
            if button.clicked(pos):
                self.answer(button.text)
                break

        return None

    def answer(self, text):
        self.answered = True
        self.player_answer = text
        self.is_correct = text == self.correct_answer

        # 回答後は経過時間を止める
        self.clear_time = time.time() - self.start_time
        self.game_cleared = True

    def on_cell_clicked(self, cell):
        # 本番では細胞のクリックに反応しない
        pass

    # =========================
    # 描画
    # =========================

    def draw(self, screen):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        self.draw_world(screen, width, height)

        self.draw_status(screen)

        question_text = self.font.render(
            f"第{self.question_number}問 / {self.total_questions}",
            True,
            (0, 0, 0)
        )
        screen.blit(question_text, (20, 20))

        if self.answered:
            self.draw_answer_result(screen, width)
        else:
            guide = self.font.render("細胞の分布から症例を判定してください", True, (0, 0, 0))
            screen.blit(guide, guide.get_rect(center=(width // 2, 50)))

        for button in self.answer_buttons:
            if button.text == self.player_answer:
                button.draw(screen, (100, 200, 255))
            else:
                button.draw(screen)

        self.draw_minimap(screen, width, height)

    def draw_answer_result(self, screen, width):
        if self.is_correct:
            result = self.font.render("正解！", True, (0, 150, 0))
        else:
            result = self.font.render(f"不正解...  正解は「{self.correct_answer}」", True, (200, 0, 0))

        screen.blit(result, result.get_rect(center=(width // 2, 50)))

        self.next_button.draw(screen)
