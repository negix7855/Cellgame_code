import asyncio

import pygame

from objects.button import Button
from objects.keyboard import Keyboard
from objects.textbox import TextBox
from systems import ranking_api
from systems.prefectures import REGIONS, prefecture_name

NICKNAME_MAX_LENGTH = 15

# 画面の段階
STEP_NICKNAME = 0
STEP_REGION = 1
STEP_PREFECTURE = 2
STEP_CONFIRM = 3
STEP_SENDING = 4
STEP_DONE = 5
STEP_FAILED = 6

# ランキングに表示される人数（これ以内なら「ランクイン」）
RANKING_SIZE = 30

CHOICE_WIDTH = 360
CHOICE_HEIGHT = 90
CHOICE_GAP = 30

SELECTED_COLOR = (100, 200, 255)


# =========================
# ランキングへの送信画面
# （ニックネーム → 地方 → 都道府県 → 確認 → 送信 の順に進む）
# =========================

class RankingSubmitScene:

    def __init__(self, font, width, height, score, details, nickname="", prefecture=None):
        """nickname / prefecture: 前回送信した時の入力（起動中だけ引き継ぐ）"""
        self.font = font
        self.width = width
        self.height = height

        self.score = score
        self.details = details

        self.step = STEP_NICKNAME

        # 入力内容
        self.prefecture = prefecture
        self.region_index = self.find_region(prefecture)

        # 送信結果
        self.succeeded = False
        self.result = None
        self.error_message = ""
        self.task = None

        self.nickname_error = ""

        self.textbox = TextBox(width // 2 - 250, 220, 500, 60, font)
        self.textbox.text = nickname
        self.keyboard = Keyboard(width // 2, 340, font)

        self.back_button = Button(10, 10, 270, 70, "戻る", font)

        self.region_buttons = self.make_choice_buttons(
            [name for name, _ in REGIONS],
            columns=4,
            top=320
        )
        self.prefecture_buttons = []

        self.send_button = Button(width // 2 - 150, 680, 300, 80, "送信する", font)

        # 送信後の2つのボタン（成功時と失敗時で役割が変わる）
        self.left_button = Button(width // 2 - 320, 620, 300, 80, "", font)
        self.right_button = Button(width // 2 + 20, 620, 300, 80, "", font)

    @staticmethod
    def find_region(prefecture):
        for i, (_, codes) in enumerate(REGIONS):
            if prefecture in codes:
                return i

        return None

    def make_choice_buttons(self, labels, columns, top):
        """選択肢のボタンを、画面中央に columns 列で並べる"""
        row_width = CHOICE_WIDTH * columns + CHOICE_GAP * (columns - 1)
        left = self.width // 2 - row_width // 2

        buttons = []

        for i, label in enumerate(labels):
            row = i // columns
            col = i % columns

            buttons.append(Button(
                left + col * (CHOICE_WIDTH + CHOICE_GAP),
                top + row * (CHOICE_HEIGHT + CHOICE_GAP),
                CHOICE_WIDTH,
                CHOICE_HEIGHT,
                label,
                self.font
            ))

        return buttons

    # =========================
    # 段階の切り替え
    # =========================

    def go_to_prefecture(self, region_index):
        self.region_index = region_index
        codes = REGIONS[region_index][1]

        # 都道府県が1つだけの地方（北海道）は、選ぶ段階を飛ばす
        if len(codes) == 1:
            self.prefecture = codes[0]
            self.step = STEP_CONFIRM
            return

        self.prefecture_buttons = self.make_choice_buttons(
            [prefecture_name(code) for code in codes],
            columns=3,
            top=300
        )
        self.step = STEP_PREFECTURE

    def go_back(self):
        """「戻る」ボタン。最初の段階なら "back"（結果画面へ）を返す"""
        if self.step == STEP_NICKNAME:
            return "back"

        if self.step == STEP_REGION:
            self.step = STEP_NICKNAME

        elif self.step == STEP_PREFECTURE:
            self.step = STEP_REGION

        elif self.step == STEP_CONFIRM:
            codes = REGIONS[self.region_index][1]
            self.step = STEP_REGION if len(codes) == 1 else STEP_PREFECTURE

        return None

    # =========================
    # 送信
    # =========================

    def start_sending(self):
        self.step = STEP_SENDING
        self.error_message = ""
        self.task = asyncio.create_task(self.send())

    async def send(self):
        try:
            self.result = await ranking_api.submit_score(
                self.textbox.text,
                self.prefecture,
                self.details
            )
            self.succeeded = True
            self.step = STEP_DONE

            self.left_button.text = "ランキングを見る"
            self.right_button.text = "結果画面に戻る"

        except Exception as e:
            if isinstance(e, ranking_api.RankingError):
                self.error_message = str(e)
            else:
                self.error_message = f"予期しないエラーが起きました（{e}）"

            self.step = STEP_FAILED

            self.left_button.text = "もう一度送信"
            self.right_button.text = "やめる"

    # =========================
    # イベント処理
    # =========================

    def handle_event(self, event):
        """戻り値: "back"（結果画面へ） / "ranking"（ランキング画面へ） / None"""
        if self.step == STEP_NICKNAME:
            key = self.keyboard.handle_event(event)

            if key is not None:
                self.input_key(key)
                return None

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        pos = event.pos

        if self.step in (STEP_NICKNAME, STEP_REGION, STEP_PREFECTURE, STEP_CONFIRM):
            if self.back_button.clicked(pos):
                return self.go_back()

        if self.step == STEP_REGION:
            for i, button in enumerate(self.region_buttons):
                if button.clicked(pos):
                    self.go_to_prefecture(i)
                    break

        elif self.step == STEP_PREFECTURE:
            codes = REGIONS[self.region_index][1]

            for code, button in zip(codes, self.prefecture_buttons):
                if button.clicked(pos):
                    self.prefecture = code
                    self.step = STEP_CONFIRM
                    break

        elif self.step == STEP_CONFIRM:
            if self.send_button.clicked(pos):
                self.start_sending()

        elif self.step == STEP_DONE:
            if self.left_button.clicked(pos):
                return "ranking"

            if self.right_button.clicked(pos):
                return "back"

        elif self.step == STEP_FAILED:
            if self.left_button.clicked(pos):
                self.start_sending()

            elif self.right_button.clicked(pos):
                return "back"

        return None

    def input_key(self, key):
        self.nickname_error = ""

        if key == "<-":
            self.textbox.text = self.textbox.text[:-1]

        elif key == "OK":
            if not self.textbox.text:
                self.nickname_error = "ニックネームを入力してください"
            else:
                self.step = STEP_REGION

        elif len(self.textbox.text) >= NICKNAME_MAX_LENGTH:
            self.nickname_error = f"ニックネームは{NICKNAME_MAX_LENGTH}文字までです"

        else:
            self.textbox.text += key

    # =========================
    # 描画
    # =========================

    def draw(self, screen):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        self.draw_center(screen, "ランキングに送信", 70)

        if self.step == STEP_NICKNAME:
            self.draw_nickname_step(screen, width)

        elif self.step == STEP_REGION:
            self.draw_center(screen, "地方を選んでください", 200)

            for i, button in enumerate(self.region_buttons):
                button.draw(screen, SELECTED_COLOR if i == self.region_index else (180, 180, 180))

        elif self.step == STEP_PREFECTURE:
            region_name, codes = REGIONS[self.region_index]
            self.draw_center(screen, f"都道府県を選んでください（{region_name}）", 200)

            for code, button in zip(codes, self.prefecture_buttons):
                button.draw(screen, SELECTED_COLOR if code == self.prefecture else (180, 180, 180))

        elif self.step == STEP_CONFIRM:
            self.draw_center(screen, "この内容で送信しますか？", 200)
            self.draw_center(screen, f"ニックネーム: {self.textbox.text}", 330)
            self.draw_center(screen, f"都道府県: {prefecture_name(self.prefecture)}", 400)
            self.draw_center(screen, f"スコア: {self.score}点", 470)
            self.send_button.draw(screen)

        elif self.step == STEP_SENDING:
            dots = "." * (pygame.time.get_ticks() // 300 % 4)
            self.draw_center(screen, f"送信中{dots}", height // 2)

        elif self.step == STEP_DONE:
            rank = self.result["rank"]

            if rank <= RANKING_SIZE:
                message = f"{rank}位にランクインしました！"
            else:
                message = f"あなたの順位は{rank}位です（上位{RANKING_SIZE}位まで表示されます）"

            self.draw_center(screen, "送信しました", 300, (0, 150, 0))
            self.draw_center(screen, message, 400, (200, 120, 0))
            self.draw_center(screen, f"スコア: {self.result['score']}点", 480)

            self.left_button.draw(screen)
            self.right_button.draw(screen)

        elif self.step == STEP_FAILED:
            self.draw_center(screen, "送信できませんでした", 350, (200, 0, 0))
            self.draw_center(screen, self.error_message, 430)

            self.left_button.draw(screen)
            self.right_button.draw(screen)

        if self.step in (STEP_NICKNAME, STEP_REGION, STEP_PREFECTURE, STEP_CONFIRM):
            self.back_button.draw(screen)

    def draw_nickname_step(self, screen, width):
        self.draw_center(
            screen,
            "ニックネームはランキングに公開されます。本名は入力しないでください",
            160,
            (200, 0, 0)
        )

        self.textbox.draw(screen)

        counter = self.font.render(
            f"{len(self.textbox.text)} / {NICKNAME_MAX_LENGTH}",
            True,
            (100, 100, 100)
        )
        screen.blit(counter, (self.textbox.rect.right + 20, self.textbox.rect.y + 8))

        if self.nickname_error:
            self.draw_center(screen, self.nickname_error, 310, (200, 0, 0))

        self.keyboard.draw(screen)

    def draw_center(self, screen, text, y, color=(0, 0, 0)):
        surface = self.font.render(text, True, color)
        screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y)))
