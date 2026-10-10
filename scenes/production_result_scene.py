import pygame

from objects.button import Button
from systems.score import TIME_BONUS_PER_SECOND, total_score


# =========================
# 本番の結果画面
# =========================

class ProductionResultScene:

    def __init__(self, font, width, height, results):
        self.font = font
        self.results = results

        self.correct_count = sum(1 for r in results if r["is_correct"])

        # 最終スコアと内訳（問題スコア / 全問正解ボーナス / 残り時間ボーナス）
        self.breakdown = total_score(results)
        self.total_score = self.breakdown["total"]

        # ランキングに送信したか（送信後は二重に送れないようにする）
        self.submitted = False

        self.submit_button = Button(width // 2 - 320, height - 180, 300, 80, "ランキングに送信", font)
        self.menu_button = Button(width // 2 + 20, height - 180, 300, 80, "選択画面に戻る", font)

    def update_layout(self, width, height):
        self.submit_button.rect = pygame.Rect(width // 2 - 320, height - 180, 300, 80)
        self.menu_button.rect = pygame.Rect(width // 2 + 20, height - 180, 300, 80)

    def mark_submitted(self):
        self.submitted = True
        self.submit_button.text = "送信済み"

    def handle_event(self, event):
        """「ランキングに送信」で "submit"、「選択画面に戻る」で "menu" を返す"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.submitted and self.submit_button.clicked(event.pos):
                return "submit"

            if self.menu_button.clicked(event.pos):
                return "menu"

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        screen.fill((255, 255, 255))

        b = self.breakdown

        self.draw_center(screen, "本番結果", 70)
        self.draw_center(screen, f"合計スコア: {self.total_score}点", 140, (200, 120, 0))
        self.draw_center(screen, f"{len(self.results)}問中 {self.correct_count}問正解", 200)

        # 内訳
        self.draw_center(
            screen,
            f"問題スコア {b['question_total']}点"
            f"  ＋  全問正解ボーナス {b['all_correct_bonus']}点"
            f"  ＋  残り時間ボーナス {b['time_bonus']}点"
            f"（{b['remaining_total']}秒 × {TIME_BONUS_PER_SECOND}）",
            270,
            (80, 80, 80)
        )

        # 1問ごとの結果
        y = 360

        for r in self.results:
            mark = "○" if r["is_correct"] else "×"
            color = (0, 150, 0) if r["is_correct"] else (200, 0, 0)

            player_answer = "時間切れ" if r["time_up"] else r["player_answer"]

            self.draw_center(
                screen,
                f"第{r['question_number']}問  {mark}  "
                f"正解: {r['correct_answer']}  /  あなたの回答: {player_answer}"
                f"  /  コイン {r['coin_score']}点 → {r['score']}点",
                y,
                color
            )
            y += 70

        # 送信済みのボタンは押せないので暗く表示する
        self.submit_button.draw(screen, (120, 120, 120) if self.submitted else (180, 180, 180))
        self.menu_button.draw(screen)

    def draw_center(self, screen, text, y, color=(0, 0, 0)):
        surface = self.font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
