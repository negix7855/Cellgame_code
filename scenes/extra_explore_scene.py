from collections import defaultdict

import pygame

from objects.button import Button
from scenes.world_scene import WorldScene
from systems.resource import resource_path

# 練習問題に進むのに必要な、各種類の発見数
REQUIRED_FOUND_COUNT = 3

BOOK_ICON_SIZE = 150
BOOK_ICON_GAP = 200

# 下部パネル（上から 名前 / 画像 / 発見数 の段を並べる）
BOOK_NAME_HEIGHT = 50
BOOK_COUNT_HEIGHT = 60
BOOK_PANEL_HEIGHT = BOOK_NAME_HEIGHT + BOOK_ICON_SIZE + BOOK_COUNT_HEIGHT

BOOK_NAME_FONT_SIZE = 26


# =========================
# エクストラモードの探索画面
# =========================

class ExtraExploreScene(WorldScene):

    MAX_ZOOM = 3.0

    RETRY_LABEL = "選択画面へ"
    RETRY_RESULT = "menu"

    def __init__(self, font, width, cells, grid, world_width, world_height, distribution):
        super().__init__(font, width, cells, grid, world_width, world_height)

        self.width = width

        self.book_data = distribution
        self.book_panel_height = BOOK_PANEL_HEIGHT

        # 下部の図鑑パネルと重ならないようにミニマップを上げる
        self.minimap_bottom_margin = self.book_panel_height

        # パネルに表示する細胞名の文字
        self.name_font = pygame.font.Font(resource_path("fonts/MPLUS1p-Bold.ttf"), BOOK_NAME_FONT_SIZE)
        self.name_font.set_bold(True)

        # 種類ごとの発見数
        self.found_cells = defaultdict(int)

        self.can_go_practice = False

        self.practice_button = Button(width // 2 - 125, 80, 250, 60, "練習問題へGO!", font)

    def update_layout(self):
        self.layout_help_menu(self.width)

        self.practice_button.rect = pygame.Rect(self.width // 2 - 125, 80, 250, 60)

    # =========================
    # イベント処理
    # =========================

    def handle_left_click(self, pos):
        if self.help_button.clicked(pos):
            self.help_menu_open = not self.help_menu_open
            return None

        if self.help_menu_open:
            handled, result = self.handle_help_menu_click(pos)

            if handled:
                return result

        if self.can_go_practice and self.practice_button.clicked(pos):
            return "practice"

        return None

    # =========================
    # 細胞判定
    # =========================

    def on_cell_clicked(self, cell):
        if cell.found:
            return

        cell.found = True

        if cell.can_count:
            self.found_cells[cell.cell_name] += 1
            cell.can_count = False

        count = self.found_cells[cell.cell_name]

        self.message = f"{cell.display_name} 発見！ {count}個目"
        self.message_timer = 120

    def get_found_cells(self):
        """見つけた細胞を種類ごとに1つずつ返す"""
        result = []
        added = set()

        for cell in self.cells:
            if cell.found and cell.cell_name not in added:
                result.append(cell)
                added.add(cell.cell_name)

        return result

    # =========================
    # 描画
    # =========================

    def draw(self, screen, cell_images):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        self.draw_world(screen, width, height)

        self.draw_status(screen)
        self.draw_message(screen, width)
        self.draw_result(screen, width)

        self.draw_help_menu(screen)

        if self.can_go_practice:
            self.practice_button.draw(screen)

        self.draw_minimap(screen, width, height)

        self.draw_book_panel(screen, cell_images)

        self.can_go_practice = all(
            self.found_cells.get(info["cell_name"], 0) >= REQUIRED_FOUND_COUNT
            for info in self.book_data
        )

    def draw_book_panel(self, screen, cell_images):
        """画面下部に、種類ごとの発見状況を表示する"""
        width, height = screen.get_size()

        panel_rect = pygame.Rect(
            0,
            height - self.book_panel_height,
            width,
            self.book_panel_height
        )

        pygame.draw.rect(screen, (40, 40, 40), panel_rect)

        x = 30
        name_y = panel_rect.top
        y = name_y + BOOK_NAME_HEIGHT

        for info in self.book_data:
            image = cell_images[info["cell_name"]]
            count = self.found_cells.get(info["cell_name"], 0)
            found = info["cell_name"] in self.found_cells

            # 細胞の名前（画像の真上に中央ぞろえ。未発見はグレー）
            name_color = (255, 255, 255) if found else (150, 150, 150)
            name = self.render_fit(info["display_name"], name_color, BOOK_ICON_GAP - 10)
            screen.blit(name, name.get_rect(center=(x + BOOK_ICON_SIZE // 2, name_y + BOOK_NAME_HEIGHT // 2)))

            icon = pygame.transform.smoothscale(image, (BOOK_ICON_SIZE, BOOK_ICON_SIZE))

            # 未発見の種類はグレーで薄く表示
            if not found:
                icon = pygame.transform.grayscale(icon)
                icon.set_alpha(120)

            screen.blit(icon, (x, y))

            # 発見数（画像の真下の段に中央ぞろえ）
            text = self.font.render(f"{count}個発見", True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=(x + BOOK_ICON_SIZE // 2, y + BOOK_ICON_SIZE + BOOK_COUNT_HEIGHT // 2)))

            x += BOOK_ICON_GAP

    def render_fit(self, text, color, max_width):
        """文字を描画し、max_width より長ければ収まるように縮める"""
        surface = self.name_font.render(text, True, color)

        if surface.get_width() > max_width:
            scale = max_width / surface.get_width()
            surface = pygame.transform.smoothscale(
                surface,
                (max_width, max(1, int(surface.get_height() * scale)))
            )

        return surface
