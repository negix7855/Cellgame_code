from collections import defaultdict

import pygame

from objects.button import Button
from scenes.world_scene import WorldScene

# 練習問題に進むのに必要な、各種類の発見数
REQUIRED_FOUND_COUNT = 3

BOOK_ICON_SIZE = 150
BOOK_ICON_GAP = 200


# =========================
# エクストラモードの探索画面
# =========================

class ExtraExploreScene(WorldScene):

    MAX_ZOOM = 3.0

    RETRY_LABEL = "タイトルへ"
    RETRY_RESULT = "home"

    def __init__(self, font, width, cells, grid, world_width, world_height, distribution):
        super().__init__(font, width, cells, grid, world_width, world_height)

        self.width = width

        # 下部の図鑑パネルと重ならないようにミニマップを上げる
        self.minimap_bottom_margin = self.minimap_margin * 10

        self.book_data = distribution
        self.book_panel_height = 200

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
        y = height - 200

        for info in self.book_data:
            image = cell_images[info["cell_name"]]
            count = self.found_cells.get(info["cell_name"], 0)

            icon = pygame.transform.smoothscale(image, (BOOK_ICON_SIZE, BOOK_ICON_SIZE))

            # 未発見の種類はグレーで薄く表示
            if info["cell_name"] not in self.found_cells:
                icon = pygame.transform.grayscale(icon)
                icon.set_alpha(120)

            screen.blit(icon, (x, y))

            text = self.font.render(f"{count}個発見", True, (0, 0, 0))
            screen.blit(text, (x, y + 155))

            x += BOOK_ICON_GAP
