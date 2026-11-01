import pygame

from objects.button import Button
from objects.image_keyboard import scale_rect
from systems.score import TIME_BONUS_PER_SECOND, total_score

# 背景画像（images/ranking/result_unsent.jpg / result_sent.jpg）に描かれたボタンの位置 (x, y, w, h)
# 送信前と送信後で位置は同じ
SUBMIT_BUTTON = (556, 747, 331, 97)
MENU_BUTTON = (1027, 750, 331, 97)

# 背景画像を使う時の文字の位置（「本番結果」の見出しは画像に描かれている）
TOTAL_Y = 235
CORRECT_Y = 290
BREAKDOWN_Y = 350
FIRST_ROW_Y = 425
ROW_HEIGHT = 62

# 当たり判定を赤枠で表示する（位置合わせの確認用）
DEBUG_HITBOX = False


# =========================
# 本番の結果画面
# =========================

class ProductionResultScene:

    def __init__(self, font, width, height, results, backgrounds=None):
        """backgrounds: {"unsent": 送信前の背景, "sent": 送信後の背景}（無ければ白い背景にボタンを描く）"""
        self.font = font
        self.results = results

        self.backgrounds = backgrounds
        self.scaled_backgrounds = {}

        self.correct_count = sum(1 for r in results if r["is_correct"])

        # 最終スコアと内訳（問題スコア / 全問正解ボーナス / 残り時間ボーナス）
        self.breakdown = total_score(results)
        self.total_score = self.breakdown["total"]

        # ランキングに送信したか（送信後は二重に送れないようにする）
        self.submitted = False

        self.submit_button = Button(width // 2 - 320, height - 180, 300, 80, "ランキングに送信", font)
        self.menu_button = Button(width // 2 + 20, height - 180, 300, 80, "選択画面に戻る", font)

        self.update_layout(width, height)

    def update_layout(self, width, height):
        if self.backgrounds is not None:
            self.submit_button.rect = scale_rect(SUBMIT_BUTTON, width, height)
            self.menu_button.rect = scale_rect(MENU_BUTTON, width, height)
        else:
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

        if self.backgrounds is not None:
            self.draw_on_background(screen, width, height)
            return

        screen.fill((255, 255, 255))

        self.draw_center(screen, "本番結果", 70)
        self.draw_center(screen, f"合計スコア: {self.total_score}点", 140, (200, 120, 0))
        self.draw_center(screen, f"{len(self.results)}問中 {self.correct_count}問正解", 200)
        self.draw_breakdown(screen, 270, (80, 80, 80))
        self.draw_rows(screen, 360, 70)

        # 送信済みのボタンは押せないので暗く表示する
        self.submit_button.draw(screen, (120, 120, 120) if self.submitted else (180, 180, 180))
        self.menu_button.draw(screen)

    def draw_on_background(self, screen, width, height):
        """ボタンが描かれた背景画像（送信前 / 送信後）に、結果の文字を書く"""
        key = "sent" if self.submitted else "unsent"

        if key not in self.scaled_backgrounds:
            image = self.backgrounds[key]

            if image.get_size() != (width, height):
                image = pygame.transform.smoothscale(image, (width, height))

            self.scaled_backgrounds[key] = image

        screen.blit(self.scaled_backgrounds[key], (0, 0))

        scale = height / 1080

        self.draw_center(screen, f"合計スコア: {self.total_score}点", TOTAL_Y * scale, (190, 100, 0))
        self.draw_center(screen, f"{len(self.results)}問中 {self.correct_count}問正解", CORRECT_Y * scale, (60, 35, 20))
        self.draw_breakdown(screen, BREAKDOWN_Y * scale, (90, 70, 50))
        self.draw_rows(screen, FIRST_ROW_Y * scale, ROW_HEIGHT * scale)

        if DEBUG_HITBOX:
            pygame.draw.rect(screen, (255, 0, 0), self.submit_button.rect, 3)
            pygame.draw.rect(screen, (255, 0, 0), self.menu_button.rect, 3)

    def draw_breakdown(self, screen, y, color):
        b = self.breakdown

        self.draw_center(
            screen,
            f"問題スコア {b['question_total']}点"
            f"  ＋  全問正解ボーナス {b['all_correct_bonus']}点"
            f"  ＋  残り時間ボーナス {b['time_bonus']}点"
            f"（{b['remaining_total']}秒 × {TIME_BONUS_PER_SECOND}）",
            y,
            color
        )

    def draw_rows(self, screen, first_y, row_height):
        """1問ごとの結果"""
        for i, r in enumerate(self.results):
            mark = "○" if r["is_correct"] else "×"
            color = (0, 130, 0) if r["is_correct"] else (200, 0, 0)

            player_answer = "時間切れ" if r["time_up"] else r["player_answer"]

            self.draw_center(
                screen,
                f"第{r['question_number']}問  {mark}  "
                f"正解: {r['correct_answer']}  /  あなたの回答: {player_answer}"
                f"  /  コイン {r['coin_score']}点 → {r['score']}点",
                first_y + i * row_height,
                color
            )

    def draw_center(self, screen, text, y, color=(0, 0, 0)):
        surface = self.font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
