import pygame

from objects.button import Button
from systems.resource import resource_path

# 背景画像の基準サイズ（当たり判定はこのサイズの座標で指定する）
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# 背景画像に描かれているボタンの位置 (x, y, w, h)
# 図鑑メニューを開いた画像（extra_menu_book）はボタンの位置が少し違うので別に持つ
LAYOUTS = {
    "closed": {
        "home": (30, 32, 295, 80),
        "book": (1595, 35, 290, 72),
        "worlds": [
            (188, 522, 299, 93),
            (505, 522, 303, 93),
            (826, 522, 299, 93),
            (1143, 522, 289, 93),
            (1452, 522, 294, 93),
        ],
        "production": (765, 775, 400, 107),
        "book_worlds": [],
    },
    "open": {
        "home": (30, 35, 295, 80),
        "book": (1595, 38, 290, 70),
        "worlds": [
            (183, 532, 301, 93),
            (502, 532, 303, 93),
            (822, 532, 300, 93),
            (1140, 532, 290, 93),
            (1450, 532, 295, 93),
        ],
        "production": (757, 785, 408, 110),
        # 図鑑メニューの各世界（ノーマルム → スコーマ）
        "book_worlds": [
            (1595, 118, 290, 62),
            (1595, 190, 290, 62),
            (1595, 263, 290, 62),
            (1595, 335, 290, 63),
            (1595, 408, 290, 62),
        ],
    },
}

# 背景画像に描かれていないので、画像（rancking_button.png）を重ねて描くボタン
# 画像の縦横比（1000:275）のまま、「図鑑」ボタンの左に並べる
RANKING_BUTTON = (1290, 33, 284, 78)

# world5 クリア時などのお知らせを表示する高さ（タイトルと練習問題の見出しの間）
NOTICE_Y = 400

# 当たり判定を赤枠で表示する（位置合わせの確認用）
DEBUG_HITBOX = False


# =========================
# エクストラの選択画面
# （パスワード入力の後に、練習問題の世界か本番問題を選ぶ）
# ボタンは背景画像に描かれているので、透明な当たり判定だけを持つ
# =========================

class ExtraMenuScene:

    def __init__(self, font, width, height, backgrounds, book_worlds, ranking_button_image=None):
        """backgrounds: {"closed": 通常の背景, "open": 図鑑メニューを開いた背景}
        book_worlds: 図鑑がある世界の番号のリスト（図鑑が無い世界のボタンは押せない）
        ranking_button_image: 「ランキング」ボタンの画像（無ければコードでボタンを描く）
        """
        self.font = font
        self.backgrounds = backgrounds
        self.book_worlds = set(book_worlds)

        # 画面上部に出す一言（world5 クリア時など）
        self.notice = ""

        self.book_menu_open = False

        self.ranking_button = Button(*RANKING_BUTTON, "ランキングを見る", font)
        self.ranking_button_image = ranking_button_image
        self.scaled_ranking_button_image = None

        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_diffmenu.ogg"))

        # 画面サイズに合わせた背景（サイズが変わった時だけ作り直す）
        self.scaled_backgrounds = {}

        self.update_layout(width, height)

    def update_layout(self, width, height):
        self.scale_x = width / BASE_WIDTH
        self.scale_y = height / BASE_HEIGHT

        self.ranking_button.rect = self.to_screen(RANKING_BUTTON)

    def to_screen(self, rect):
        """基準サイズの座標を、現在の画面サイズに合わせて変換する"""
        x, y, w, h = rect

        return pygame.Rect(
            x * self.scale_x,
            y * self.scale_y,
            w * self.scale_x,
            h * self.scale_y
        )

    def current_layout(self):
        return LAYOUTS["open" if self.book_menu_open else "closed"]

    def hit(self, rect, pos):
        return self.to_screen(rect).collidepoint(pos)

    # =========================
    # イベント処理
    # =========================

    def handle_event(self, event):
        """選ばれた内容を辞書で返す（何も選ばれなければ None）"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        pos = event.pos
        layout = self.current_layout()

        if self.hit(layout["book"], pos):
            self.select_se.play()
            self.book_menu_open = not self.book_menu_open
            return None

        # 図鑑メニューは他のボタンの上に重なるので先に判定する
        for world, rect in enumerate(layout["book_worlds"], 1):
            if world in self.book_worlds and self.hit(rect, pos):
                self.select_se.play()
                return {"action": "book", "world": world}

        for world, rect in enumerate(layout["worlds"], 1):
            if self.hit(rect, pos):
                self.select_se.play()
                return {"action": "practice", "world": world}

        if self.hit(layout["production"], pos):
            self.select_se.play()
            return {"action": "production"}

        if self.ranking_button.clicked(pos):
            self.select_se.play()
            return {"action": "ranking"}

        if self.hit(layout["home"], pos):
            self.select_se.play()
            return {"action": "home"}

        return None

    # =========================
    # 描画
    # =========================

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        screen.blit(self.get_background(width, height), (0, 0))

        if self.notice:
            notice = self.font.render(self.notice, True, (0, 130, 0))
            screen.blit(notice, notice.get_rect(center=(width // 2, NOTICE_Y * self.scale_y)))

        self.draw_ranking_button(screen)

        if DEBUG_HITBOX:
            self.draw_hitboxes(screen)

    def draw_ranking_button(self, screen):
        if self.ranking_button_image is None:
            self.ranking_button.draw(screen)
            return

        rect = self.ranking_button.rect

        # ボタンの大きさに合わせた画像は使い回す
        if self.scaled_ranking_button_image is None or self.scaled_ranking_button_image.get_size() != rect.size:
            self.scaled_ranking_button_image = pygame.transform.smoothscale(self.ranking_button_image, rect.size)

        screen.blit(self.scaled_ranking_button_image, rect)

    def get_background(self, width, height):
        key = ("open" if self.book_menu_open else "closed", width, height)

        if key not in self.scaled_backgrounds:
            image = self.backgrounds[key[0]]

            if image.get_size() != (width, height):
                image = pygame.transform.smoothscale(image, (width, height))

            self.scaled_backgrounds[key] = image

        return self.scaled_backgrounds[key]

    def draw_hitboxes(self, screen):
        layout = self.current_layout()

        rects = [layout["home"], layout["book"], layout["production"], RANKING_BUTTON]
        rects += layout["worlds"] + layout["book_worlds"]

        for rect in rects:
            pygame.draw.rect(screen, (255, 0, 0), self.to_screen(rect), 3)
