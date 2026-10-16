import asyncio

import pygame

from objects.button import Button
from systems import ranking_api
from systems.prefectures import prefecture_name

ROWS_PER_PAGE = 15

# 背景画像（ranking_board）の羊皮紙の内側（横 約78〜1845、縦 約75〜995）に収まるよう並べる
TITLE_Y = 125
PAGE_INFO_Y = 178
ROW_HEIGHT = 46
FIRST_ROW_Y = 235
BACK_BUTTON = (110, 95, 250, 65)

# 「前へ」「次へ」はページ表示（「1〜15位」）の左右に置く
# （羊皮紙の下には紙束や顕微鏡の飾りが描かれているため）
PAGE_BUTTON_WIDTH = 200
PAGE_BUTTON_HEIGHT = 56
PAGE_BUTTON_OFFSET = 300

# 表の列（表の左端からの位置）。順位とスコアは右ぞろえ、他は左ぞろえ
# スコアは最大6桁（119540点）
TABLE_WIDTH = 1300
COLUMN_RANK_RIGHT = 80
COLUMN_SCORE_RIGHT = 290
COLUMN_NICKNAME = 330
COLUMN_PREFECTURE = 840
COLUMN_DATE = 1000

HIGHLIGHT_COLOR = (255, 235, 160)


# =========================
# ランキング画面（上位30名を15名ずつ2ページで表示）
# =========================

class RankingScene:

    def __init__(self, font, width, height, highlight_id=None, highlight_rank=None, background=None):
        """highlight_id / highlight_rank: 送信直後に開いた時の、自分の登録
        background: 背景画像（無ければ白）
        """
        self.font = font
        self.background = background
        self.scaled_background = None

        self.highlight_id = highlight_id
        self.highlight_rank = highlight_rank

        self.rows = []
        self.loading = False
        self.error_message = ""
        self.task = None

        # 自分が16位以下なら最初から2ページ目を開く
        self.page = 0

        if highlight_rank is not None and highlight_rank > ROWS_PER_PAGE:
            self.page = (min(highlight_rank, ROWS_PER_PAGE * 2) - 1) // ROWS_PER_PAGE

        self.back_button = Button(*BACK_BUTTON, "戻る", font)
        button_y = PAGE_INFO_Y - PAGE_BUTTON_HEIGHT // 2

        self.prev_button = Button(
            width // 2 - PAGE_BUTTON_OFFSET - PAGE_BUTTON_WIDTH, button_y,
            PAGE_BUTTON_WIDTH, PAGE_BUTTON_HEIGHT, "前へ", font
        )
        self.next_button = Button(
            width // 2 + PAGE_BUTTON_OFFSET, button_y,
            PAGE_BUTTON_WIDTH, PAGE_BUTTON_HEIGHT, "次へ", font
        )
        self.reload_button = Button(width // 2 - 150, height // 2 + 60, 300, 80, "再読み込み", font)

        self.load()

    # =========================
    # 読み込み
    # =========================

    def load(self):
        self.loading = True
        self.error_message = ""
        self.task = asyncio.create_task(self.fetch())

    async def fetch(self):
        try:
            self.rows = await ranking_api.fetch_ranking() or []

        except Exception as e:
            if isinstance(e, ranking_api.RankingError):
                self.error_message = str(e)
            else:
                self.error_message = f"予期しないエラーが起きました（{e}）"

        self.loading = False

        # 読み込み結果のページ数に合わせる
        self.page = min(self.page, self.page_count() - 1)

    def page_count(self):
        return max(1, (len(self.rows) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)

    # =========================
    # イベント処理
    # =========================

    def handle_event(self, event):
        """「戻る」で "back" を返す"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        pos = event.pos

        if self.back_button.clicked(pos):
            return "back"

        if self.loading:
            return None

        if self.error_message:
            if self.reload_button.clicked(pos):
                self.load()

        elif self.page > 0 and self.prev_button.clicked(pos):
            self.page -= 1

        elif self.page < self.page_count() - 1 and self.next_button.clicked(pos):
            self.page += 1

        return None

    # =========================
    # 描画
    # =========================

    def draw(self, screen):
        width, height = screen.get_size()

        self.draw_background(screen, width, height)

        self.draw_center(screen, f"ランキング（上位{ROWS_PER_PAGE * 2}名）", TITLE_Y)
        self.back_button.draw(screen)

        if self.loading:
            dots = "." * (pygame.time.get_ticks() // 300 % 4)
            self.draw_center(screen, f"読み込み中{dots}", height // 2)
            return

        if self.error_message:
            self.draw_center(screen, "ランキングを読み込めませんでした", height // 2 - 80, (200, 0, 0))
            self.draw_center(screen, self.error_message, height // 2 - 10)
            self.reload_button.draw(screen)
            return

        if not self.rows:
            self.draw_center(screen, "まだ登録がありません", height // 2)
            return

        self.draw_page_info(screen)
        self.draw_table(screen, width)

        if self.page > 0:
            self.prev_button.draw(screen)

        if self.page < self.page_count() - 1:
            self.next_button.draw(screen)

    def draw_page_info(self, screen):
        first = self.page * ROWS_PER_PAGE + 1
        last = min(first + ROWS_PER_PAGE - 1, len(self.rows))

        info = f"{first}〜{last}位"

        # 表に載っていない順位なら、自分の順位を添える
        if self.highlight_rank is not None and self.highlight_rank > len(self.rows):
            info += f"　／　あなたの順位: {self.highlight_rank}位"

        self.draw_center(screen, info, PAGE_INFO_Y, (100, 80, 60))

    def draw_table(self, screen, width):
        left = width // 2 - TABLE_WIDTH // 2

        start = self.page * ROWS_PER_PAGE
        rows = self.rows[start:start + ROWS_PER_PAGE]

        for i, row in enumerate(rows):
            center_y = FIRST_ROW_Y + i * ROW_HEIGHT

            if row["id"] == self.highlight_id:
                pygame.draw.rect(
                    screen,
                    HIGHLIGHT_COLOR,
                    (left - 20, center_y - ROW_HEIGHT // 2, TABLE_WIDTH + 40, ROW_HEIGHT),
                    border_radius=8
                )

            self.draw_cell(screen, f"{row['rank']}位", left + COLUMN_RANK_RIGHT, center_y, right=True)
            self.draw_cell(screen, f"{row['score']}点", left + COLUMN_SCORE_RIGHT, center_y, right=True)
            self.draw_cell(screen, row["nickname"], left + COLUMN_NICKNAME, center_y)
            self.draw_cell(screen, prefecture_name(row["prefecture"]), left + COLUMN_PREFECTURE, center_y)
            self.draw_cell(screen, row["created_at"], left + COLUMN_DATE, center_y)

    def draw_background(self, screen, width, height):
        if self.background is None:
            screen.fill((255, 255, 255))
            return

        # 画面サイズに合わせた背景は使い回す
        if self.scaled_background is None or self.scaled_background.get_size() != (width, height):
            if self.background.get_size() == (width, height):
                self.scaled_background = self.background
            else:
                self.scaled_background = pygame.transform.smoothscale(self.background, (width, height))

        screen.blit(self.scaled_background, (0, 0))

    def draw_cell(self, screen, text, x, center_y, right=False):
        surface = self.font.render(str(text), True, (0, 0, 0))

        if right:
            rect = surface.get_rect(midright=(x, center_y))
        else:
            rect = surface.get_rect(midleft=(x, center_y))

        screen.blit(surface, rect)

    def draw_center(self, screen, text, y, color=(0, 0, 0)):
        surface = self.font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
