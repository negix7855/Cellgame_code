import random
import time

import pygame

from objects.button import Button
from scenes.world_scene import WorldScene
from systems.resource import resource_path

HINT_DURATION = 100

# この数の異常細胞をヒントなしで見つけるとエクストラのコードを表示する
EXTRA_CODE_CELL_COUNT = 5
EXTRA_CODE = "EXTRA CODE: CELL-9384"


# =========================
# ノーマルモードのゲーム画面
# =========================

class GameScene(WorldScene):

    MAX_ZOOM = 4.0

    RETRY_LABEL = "難易度選択へ"
    RETRY_RESULT = "menu"

    def __init__(self, font, width, abnormal_cell_count, cells, grid, world_width, world_height):
        super().__init__(font, width, cells, grid, world_width, world_height)

        self.abnormal_cell_count = abnormal_cell_count
        self.found_count = 0

        # ヒント
        self.hint_active = False
        self.hint_target = None
        self.hint_timer = 0
        self.total_hint = 0

        self.hint_button = Button(width - 220, 100, 200, 60, "ヒント", font)

        # クリア（ギブアップ）後に画面中央に出す、難易度選択へ戻るボタン
        self.back_to_menu_button = Button(width // 2 - 150, 270, 300, 70, "難易度選択へ戻る", font)

        self.correct_sound = pygame.mixer.Sound(resource_path("sounds/correct.ogg"))
        self.miss_sound = pygame.mixer.Sound(resource_path("sounds/miss.ogg"))

    def update_layout(self, width, height):
        self.layout_help_menu(width)

        # ヒントボタンはミニマップの真上
        self.hint_button.rect = pygame.Rect(
            self.minimap_x,
            self.minimap_y - 80,
            self.minimap_width,
            60
        )

        self.back_to_menu_button.rect = pygame.Rect(width // 2 - 150, 270, 300, 70)

    # =========================
    # イベント処理
    # =========================

    def handle_left_click(self, pos):
        if self.game_cleared and self.back_to_menu_button.clicked(pos):
            self.reset()
            return "menu"

        if self.hint_button.clicked(pos):
            self.use_hint()

        elif self.help_button.clicked(pos):
            self.help_menu_open = not self.help_menu_open
            return None

        if self.help_menu_open:
            handled, result = self.handle_help_menu_click(pos)

            if handled:
                return result

        return None

    def use_hint(self):
        if not self.game_cleared and not self.giveup_flg:
            self.total_hint += 1

        unfound = [
            c for c in self.cells
            if c.is_target and not c.found
        ]

        if unfound:
            self.hint_target = random.choice(unfound)
            self.hint_active = True
            self.hint_timer = HINT_DURATION

    def reset(self):
        self.found_count = 0

        super().reset()

    # =========================
    # 更新
    # =========================

    def update(self):
        if self.hint_timer > 0:
            self.hint_timer -= 1
        else:
            self.hint_active = False
            self.hint_target = None

        super().update()

    # =========================
    # 細胞判定
    # =========================

    def on_cell_clicked(self, cell):
        if cell.is_target and not cell.found:
            cell.found = True

            self.correct_sound.play()

            self.found_count += 1

            if (
                self.found_count == self.abnormal_cell_count
                and not self.game_cleared
            ):
                self.game_cleared = True
                self.clear_time = time.time() - self.start_time

            self.show_message("異常発見!")

        else:
            self.show_message("ざんねん...")

    # =========================
    # 描画
    # =========================

    def draw(self, screen):
        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        self.draw_world(screen, width, height)

        self.draw_status(screen)
        self.draw_message(screen, width)
        self.draw_result(screen, width)

        self.hint_button.draw(screen)
        self.draw_help_menu(screen)

        self.draw_minimap(screen, width, height)

    def draw_status(self, screen):
        found_text = self.font.render(
            f"発見数: {self.found_count} / {self.abnormal_cell_count}",
            True,
            (0, 0, 0)
        )
        screen.blit(found_text, (20, 20))

        super().draw_status(screen)

    def get_clear_text(self):
        return f"クリア！ ヒント利用回数: {self.total_hint}回"

    def draw_result(self, screen, width):
        super().draw_result(screen, width)

        if (
            self.game_cleared
            and not self.giveup_flg
            and self.abnormal_cell_count == EXTRA_CODE_CELL_COUNT
            and self.total_hint == 0
        ):
            code_text = self.font.render(EXTRA_CODE, True, (255, 0, 255))
            screen.blit(code_text, code_text.get_rect(center=(width // 2, 220)))

        if self.game_cleared:
            self.back_to_menu_button.draw(screen)

    def draw_minimap(self, screen, width, height):
        super().draw_minimap(screen, width, height)

        # ヒント対象の位置を円で示す
        if self.hint_active and self.hint_target:
            hx, hy = self.world_to_minimap(self.hint_target.x, self.hint_target.y)

            pygame.draw.circle(screen, (0, 255, 0), (int(hx), int(hy)), 18, 3)
