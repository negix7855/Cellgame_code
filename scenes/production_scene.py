import math
import time
from collections import Counter

import pygame

from objects.button import Button
from scenes.world_scene import WorldScene
from systems.grid import get_grid_pos
from systems.score import coin_value, format_multiplier, question_score, streak_multiplier

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

# 1問の制限時間（秒）。server/supabase_ranking.sql の time_limit と合わせること
TIME_LIMIT = 60

# 残り時間がこの秒数以下になったら赤で表示する
TIME_WARNING = 10

# コインを拾った時のメッセージを表示するフレーム数
COIN_MESSAGE_DURATION = 60


# =========================
# 本番（症例判定）画面
# （細胞の分布を観察して、症例を5択で答える。コインを拾うとスコアになる）
# =========================

class ProductionScene(WorldScene):

    MAX_ZOOM = 3.0

    # コインを次々拾えるよう、連打防止の間隔を短くする
    CLICK_INTERVAL_MS = 100

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
            score_before=0,
            streak_before=0
        ):
        """score_before: これまでの問題のスコアの合計
        streak_before: 直前まで何問連続で正解しているか
        """
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

        # 拾ったコイン
        self.coin_score = 0
        self.coin_counts = Counter()

        # スコア
        self.score_before = score_before
        self.streak_before = streak_before
        self.streak = 0
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
            "coin_score": self.coin_score,
            "coin_counts": dict(self.coin_counts),
            "streak": self.streak,
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

        self.remaining_seconds = self.get_remaining_seconds()

        self.player_answer = answer
        self.time_up = answer is None
        self.is_correct = answer == self.correct_answer

        # 正解なら連続正解を伸ばし、不正解・時間切れなら途切れる
        self.streak = self.streak_before + 1 if self.is_correct else 0

        self.score = question_score(self.coin_score, self.is_correct, self.time_up, self.streak)

        # 回答後は経過時間を止め、コインも拾えなくする
        self.clear_time = elapsed
        self.game_cleared = True
        self.answered = True

    def on_cell_clicked(self, cell):
        """コインなら拾う（細胞には反応しない）"""
        value = coin_value(cell.cell_name)

        if value is None:
            return

        self.coin_score += value
        self.coin_counts[value] += 1

        # 拾ったコインはマップから消す
        self.cells.remove(cell)
        self.grid[get_grid_pos(cell.x, cell.y)].remove(cell)

        self.message = f"+{value}点（{cell.display_name}）"
        self.message_timer = COIN_MESSAGE_DURATION

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

            # コインを拾った時のメッセージ
            if self.message_timer > 0:
                text = self.font.render(self.message, True, (200, 120, 0))
                screen.blit(text, text.get_rect(center=(width // 2, 100)))

        for button in self.answer_buttons:
            if button.text == self.player_answer:
                button.draw(screen, (100, 200, 255))
            else:
                button.draw(screen)

        self.draw_minimap(screen, width, height)

    def draw_status(self, screen):
        """画面左上の 問題番号 / 残り時間 / 獲得コイン / 合計スコア"""
        lines = [
            (f"第{self.question_number}問 / {self.total_questions}", (0, 0, 0)),
        ]

        remaining = self.get_remaining_seconds()
        lines.append((f"残り時間: {remaining}秒", (200, 0, 0) if remaining <= TIME_WARNING else (0, 0, 0)))

        lines.append((f"獲得コイン: {self.coin_score}点", (200, 120, 0)))

        total = self.score_before + (self.score if self.answered else 0)
        lines.append((f"合計スコア: {total}点", (0, 0, 0)))

        for i, (text, color) in enumerate(lines):
            screen.blit(self.font.render(text, True, color), (20, 20 + i * 40))

    def draw_answer_result(self, screen, width):
        if self.time_up:
            text = f"時間切れ！  正解は「{self.correct_answer}」  0点"
            color = (200, 0, 0)

        elif self.is_correct:
            multiplier = streak_multiplier(self.streak)

            if self.streak >= 2:
                bonus = f" × {format_multiplier(multiplier)}（{self.streak}問連続正解）"
            else:
                bonus = ""

            text = f"正解！  コイン {self.coin_score}点 × 2{bonus} = {self.score}点"
            color = (0, 150, 0)

        else:
            text = f"不正解...  正解は「{self.correct_answer}」  コイン {self.coin_score}点 × 0.5 = {self.score}点"
            color = (200, 0, 0)

        result = self.font.render(text, True, color)
        screen.blit(result, result.get_rect(center=(width // 2, 50)))

        self.next_button.draw(screen)
