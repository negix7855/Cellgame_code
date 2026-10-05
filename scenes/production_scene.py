import math
import time

import pygame

from objects.button import Button
from scenes.world_scene import WorldScene

# 本番で出題する症例数（data/exam/case1.csv 〜 case5.csv）
EXAM_CASE_COUNT = 5

# 症例番号と正解の対応
CASE_ANSWERS = {
    1: "ノーマルム",
    2: "インフェクタ",
    3: "コイロサイト諸島",
    4: "シンジオン砦",
    5: "スコーマ",
}

ANSWER_CHOICES = list(CASE_ANSWERS.values())

# スコアアタック
# 回答した時の残り秒数が基礎スコア。正解なら CORRECT_MULTIPLIER 倍、不正解・時間切れは0点
TIME_LIMIT = 60
CORRECT_MULTIPLIER = 2

# 残り時間がこの秒数以下になったら赤で表示する
TIME_WARNING = 10


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
            total_questions,
            score_before=0
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
        self.time_up = False

        # スコア（score_before はこれまでの問題の合計）
        self.score_before = score_before
        self.remaining_seconds = TIME_LIMIT
        self.score = 0

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
            "time_up": self.time_up,
            "remaining_seconds": self.remaining_seconds,
            "score": self.score,
        }

    # =========================
    # 制限時間
    # =========================

    def get_remaining_seconds(self):
        """画面に表示する残り秒数（切り上げ。回答後は回答した時点の値）"""
        if self.answered:
            return self.remaining_seconds

        elapsed = time.time() - self.start_time

        return max(0, math.ceil(TIME_LIMIT - elapsed))

    def update(self):
        super().update()

        if not self.answered and self.get_remaining_seconds() <= 0:
            self.finish_question(None)

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
                self.finish_question(button.text)
                break

        return None

    def finish_question(self, answer):
        """回答（answer が None なら時間切れ）して、この問題のスコアを決める"""
        elapsed = min(time.time() - self.start_time, TIME_LIMIT)

        # 画面に表示されている残り秒数をそのまま基礎スコアにする
        self.remaining_seconds = self.get_remaining_seconds()

        self.player_answer = answer
        self.time_up = answer is None
        self.is_correct = answer == self.correct_answer

        if self.is_correct:
            self.score = self.remaining_seconds * CORRECT_MULTIPLIER
        else:
            self.score = 0

        # 回答後は経過時間を止める
        self.clear_time = elapsed
        self.game_cleared = True
        self.answered = True

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

    def draw_status(self, screen):
        """画面左上の 問題番号 / 残り時間 / 合計スコア"""
        question_text = self.font.render(
            f"第{self.question_number}問 / {self.total_questions}",
            True,
            (0, 0, 0)
        )
        screen.blit(question_text, (20, 20))

        remaining = self.get_remaining_seconds()

        color = (200, 0, 0) if remaining <= TIME_WARNING else (0, 0, 0)
        timer_text = self.font.render(f"残り時間: {remaining}秒", True, color)
        screen.blit(timer_text, (20, 60))

        total = self.score_before + (self.score if self.answered else 0)
        score_text = self.font.render(f"合計スコア: {total}点", True, (0, 0, 0))
        screen.blit(score_text, (20, 100))

    def draw_answer_result(self, screen, width):
        if self.time_up:
            result = self.font.render(f"時間切れ！  正解は「{self.correct_answer}」  0点", True, (200, 0, 0))

        elif self.is_correct:
            result = self.font.render(
                f"正解！  残り{self.remaining_seconds}秒 × {CORRECT_MULTIPLIER} = {self.score}点",
                True,
                (0, 150, 0)
            )

        else:
            result = self.font.render(f"不正解...  正解は「{self.correct_answer}」  0点", True, (200, 0, 0))

        screen.blit(result, result.get_rect(center=(width // 2, 50)))

        self.next_button.draw(screen)
