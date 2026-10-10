import pygame

from objects.button import Button
from systems.resource import resource_path

WORLD_BUTTON_WIDTH = 300
WORLD_BUTTON_HEIGHT = 90
WORLD_BUTTON_GAP = 30

# 各段の縦位置（右上の図鑑メニューを開いても重ならない高さにする）
PRACTICE_LABEL_Y = 480
WORLD_BUTTON_Y = 530
PRODUCTION_LABEL_Y = 730
PRODUCTION_BUTTON_Y = 780

# 右上の図鑑メニュー（「コイロサイト諸島」が収まる幅）
BOOK_BUTTON_WIDTH = 300
BOOK_BUTTON_HEIGHT = 60
BOOK_BUTTON_GAP = 10


# =========================
# エクストラの選択画面
# （パスワード入力の後に、練習問題の世界か本番問題を選ぶ）
# =========================

class ExtraMenuScene:

    def __init__(self, font, width, height, world_names, book_worlds):
        """world_names: 世界の名前のリスト（WORLD 1 から順に）
        book_worlds: 図鑑がある世界の番号のリスト
        """
        self.font = font
        self.world_count = len(world_names)

        # 画面上部に出す一言（world5 クリア時など）
        self.notice = ""

        self.home_button = Button(30, 30, 270, 70, "ホームに戻る", font)

        self.world_buttons = [
            Button(0, 0, WORLD_BUTTON_WIDTH, WORLD_BUTTON_HEIGHT, name, font)
            for name in world_names
        ]

        self.production_button = Button(0, 0, 360, 100, "本番問題に挑戦", font)
        self.ranking_button = Button(0, 0, 360, 80, "ランキングを見る", font)

        # 図鑑メニュー（「図鑑」を押すと世界ごとのボタンが開く）
        self.book_menu_open = False
        self.book_button = Button(0, 0, BOOK_BUTTON_WIDTH, BOOK_BUTTON_HEIGHT, "図鑑", font)
        self.book_world_buttons = [
            (world, Button(0, 0, BOOK_BUTTON_WIDTH, BOOK_BUTTON_HEIGHT, world_names[world - 1], font))
            for world in book_worlds
        ]

        self.select_se = pygame.mixer.Sound(resource_path("sounds/select_diffmenu.ogg"))

        self.update_layout(width, height)

    def update_layout(self, width, height):
        # 練習問題の世界ボタンを横一列に並べる
        row_width = (
            WORLD_BUTTON_WIDTH * self.world_count
            + WORLD_BUTTON_GAP * (self.world_count - 1)
        )
        x = width // 2 - row_width // 2

        for button in self.world_buttons:
            button.rect = pygame.Rect(x, WORLD_BUTTON_Y, WORLD_BUTTON_WIDTH, WORLD_BUTTON_HEIGHT)
            x += WORLD_BUTTON_WIDTH + WORLD_BUTTON_GAP

        self.production_button.rect = pygame.Rect(width // 2 - 180, PRODUCTION_BUTTON_Y, 360, 100)
        self.ranking_button.rect = pygame.Rect(width // 2 - 180, PRODUCTION_BUTTON_Y + 130, 360, 80)

        # 図鑑ボタンは右上、世界ごとのボタンはその下に縦に並べる
        x = width - BOOK_BUTTON_WIDTH - 30
        y = 30

        self.book_button.rect = pygame.Rect(x, y, BOOK_BUTTON_WIDTH, BOOK_BUTTON_HEIGHT)

        for _, button in self.book_world_buttons:
            y += BOOK_BUTTON_HEIGHT + BOOK_BUTTON_GAP
            button.rect = pygame.Rect(x, y, BOOK_BUTTON_WIDTH, BOOK_BUTTON_HEIGHT)

    def handle_event(self, event):
        """選ばれた内容を辞書で返す（何も選ばれなければ None）"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if self.book_button.clicked(event.pos):
            self.select_se.play()
            self.book_menu_open = not self.book_menu_open
            return None

        # 図鑑メニューは他のボタンの上に重ねて表示するので先に判定する
        if self.book_menu_open:
            for world, button in self.book_world_buttons:
                if button.clicked(event.pos):
                    self.select_se.play()
                    return {"action": "book", "world": world}

        for i, button in enumerate(self.world_buttons, 1):
            if button.clicked(event.pos):
                self.select_se.play()
                return {"action": "practice", "world": i}

        if self.production_button.clicked(event.pos):
            self.select_se.play()
            return {"action": "production"}

        if self.ranking_button.clicked(event.pos):
            self.select_se.play()
            return {"action": "ranking"}

        if self.home_button.clicked(event.pos):
            self.select_se.play()
            return {"action": "home"}

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        self.update_layout(width, height)

        screen.fill((255, 255, 255))

        title = self.font.render("エクストラステージ", True, (0, 0, 0))
        screen.blit(title, title.get_rect(center=(width // 2, 150)))

        if self.notice:
            notice = self.font.render(self.notice, True, (0, 150, 0))
            screen.blit(notice, notice.get_rect(center=(width // 2, 230)))

        practice_label = self.font.render("練習問題（世界を選んで探索）", True, (0, 0, 0))
        screen.blit(practice_label, practice_label.get_rect(center=(width // 2, PRACTICE_LABEL_Y)))

        for button in self.world_buttons:
            button.draw(screen)

        production_label = self.font.render("本番問題（症例を判定）", True, (0, 0, 0))
        screen.blit(production_label, production_label.get_rect(center=(width // 2, PRODUCTION_LABEL_Y)))

        self.production_button.draw(screen)
        self.ranking_button.draw(screen)
        self.home_button.draw(screen)

        self.book_button.draw(screen)

        if self.book_menu_open:
            for _, button in self.book_world_buttons:
                button.draw(screen)
