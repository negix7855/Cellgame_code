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

        self.home_button = Button(width // 2 - 150, height - 180, 300, 80, "ホームへ戻る", font)

    def update_layout(self, width, height):
        self.home_button.rect = pygame.Rect(width // 2 - 150, height - 180, 300, 80)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.home_button.clicked(event.pos):
                return "home"

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        screen.fill((255, 255, 255))

        title = self.font.render("本番結果", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(width // 2, 100)))

        score = self.font.render(
            f"{len(self.results)}問中 {self.correct_count}問正解",
            True,
            (0, 0, 0)
        )
        screen.blit(score, score.get_rect(center=(width // 2, 180)))

        # 1問ごとの結果
        y = 280

        for r in self.results:
            mark = "○" if r["is_correct"] else "×"
            color = (0, 150, 0) if r["is_correct"] else (200, 0, 0)

            text = self.font.render(
                f"第{r['question_number']}問  {mark}  "
                f"正解: {r['correct_answer']}  /  あなたの回答: {r['player_answer']}",
                True,
                color
            )
            screen.blit(text, text.get_rect(center=(width // 2, y)))
            y += 70

        self.home_button.draw(screen)
