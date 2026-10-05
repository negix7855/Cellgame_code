import pygame

from objects.button import Button


# =========================
# 本番の結果画面
# =========================

class ProductionResultScene:

    def __init__(self, font, width, height, results):
        self.font = font
        self.results = results

        self.correct_count = sum(1 for r in results if r["is_correct"])
        self.total_score = sum(r["score"] for r in results)

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

        title = self.font.render("本番結果", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(width // 2, 100)))

        total = self.font.render(f"合計スコア: {self.total_score}点", True, (200, 120, 0))
        screen.blit(total, total.get_rect(center=(width // 2, 170)))

        score = self.font.render(
            f"{len(self.results)}問中 {self.correct_count}問正解",
            True,
            (0, 0, 0)
        )
        screen.blit(score, score.get_rect(center=(width // 2, 230)))

        # 1問ごとの結果
        y = 320

        for r in self.results:
            mark = "○" if r["is_correct"] else "×"
            color = (0, 150, 0) if r["is_correct"] else (200, 0, 0)

            player_answer = "時間切れ" if r["time_up"] else r["player_answer"]

            text = self.font.render(
                f"第{r['question_number']}問  {mark}  "
                f"正解: {r['correct_answer']}  /  あなたの回答: {player_answer}"
                f"  /  {r['score']}点",
                True,
                color
            )
            screen.blit(text, text.get_rect(center=(width // 2, y)))
            y += 70

        # 送信済みのボタンは押せないので暗く表示する
        self.submit_button.draw(screen, (120, 120, 120) if self.submitted else (180, 180, 180))
        self.menu_button.draw(screen)
