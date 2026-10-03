import math
import time

import pygame

from objects.button import Button
from systems.grid import GRID_SIZE, iter_neighbor_cells

# クリックの連打を無視する間隔（ミリ秒）
CLICK_INTERVAL_MS = 500

# この距離以上指が動いたらタップではなくドラッグとみなす
TAP_MOVE_THRESHOLD = 15


# =========================
# ワールド探索シーンの基底クラス
# （カメラ操作・タッチ操作・ミニマップ・共通UI）
# =========================

class WorldScene:

    MIN_ZOOM = 0.1
    MAX_ZOOM = 4.0

    # ヘルプメニューの「戻る」ボタンの表示名と、押した時に main に返す結果
    RETRY_LABEL = ""
    RETRY_RESULT = None

    def __init__(self, font, width, cells, grid, world_width, world_height):
        self.font = font

        self.cells = cells
        self.grid = grid
        self.grid_size = GRID_SIZE

        self.world_width = world_width
        self.world_height = world_height

        # カメラ
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 0.2

        # マウス操作
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.last_click_time = 0

        # 左クリックを押した位置（離した時に細胞を判定するため）
        self.mouse_press_pos = None

        # タッチ操作
        self.touch_dragging = False
        self.touch_start_pos = (0, 0)
        self.last_touch_pos = (0, 0)
        self.touch_moved = False

        self.active_touches = {}
        self.pinch_distance = None

        # ゲーム状態
        self.game_cleared = False
        self.giveup_flg = False

        self.start_time = time.time()
        self.clear_time = 0

        self.message = ""
        self.message_timer = 0

        # ミニマップ
        self.minimap_width = 220
        self.minimap_height = 220
        self.minimap_x = 0
        self.minimap_y = 0
        self.minimap_margin = 20
        self.minimap_bottom_margin = self.minimap_margin

        # ヘルプメニュー
        self.help_menu_open = False

        self.help_button = Button(width - 260, 20, 250, 60, "？", font)
        self.retry_button = Button(width - 260, 90, 250, 60, self.RETRY_LABEL, font)
        self.giveup_button = Button(width - 260, 160, 250, 60, "諦める", font)
        self.book_button = Button(width - 260, 230, 250, 60, "図鑑", font)

    def layout_help_menu(self, width):
        self.retry_button.rect = pygame.Rect(width - 260, 90, 250, 60)
        self.giveup_button.rect = pygame.Rect(width - 260, 160, 250, 60)

    # =========================
    # イベント処理
    # =========================

    def handle_event(self, event, width, height):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.dragging = True
                self.last_mouse_pos = event.pos

            elif event.button == 1:
                if getattr(event, "touch", False):
                    # スマホのタッチから作られたマウスイベント。
                    # 細胞の判定は指を離した時（FINGERUP）に行うので、ここではしない
                    self.mouse_press_pos = None
                else:
                    self.mouse_press_pos = event.pos

                return self.handle_left_click(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self.dragging = False

            elif event.button == 1:
                self.handle_left_release(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]

                self.camera_x -= dx / self.zoom
                self.camera_y -= dy / self.zoom

                self.last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.zoom *= 1.1
            else:
                self.zoom /= 1.1

            self.zoom = self.clamp_zoom(self.zoom)

        elif event.type == pygame.FINGERDOWN:
            self.handle_finger_down(event, width, height)

        elif event.type == pygame.FINGERMOTION:
            self.handle_finger_motion(event, width, height)

        elif event.type == pygame.FINGERUP:
            self.handle_finger_up(event, width, height)

    def handle_left_click(self, pos):
        """左クリックを押した時のボタン処理。シーンごとに実装する。

        細胞の判定はここではなく、離した時（handle_left_release）に行う。
        """
        raise NotImplementedError

    def handle_left_release(self, pos):
        """左クリックを離した時、ほとんど動いていなければ細胞を判定する"""
        if self.mouse_press_pos is None:
            return

        dx = pos[0] - self.mouse_press_pos[0]
        dy = pos[1] - self.mouse_press_pos[1]

        self.mouse_press_pos = None

        if math.sqrt(dx * dx + dy * dy) <= TAP_MOVE_THRESHOLD:
            self.check_cell_click(self.screen_to_world(pos))

    def handle_help_menu_click(self, pos):
        """ヘルプメニューのボタン処理。

        (処理したか, main に返す結果) を返す。
        """
        if self.book_button.clicked(pos):
            return True, "book"

        elif self.giveup_button.clicked(pos):
            if not self.game_cleared:
                self.give_up()

            return True, None

        elif self.retry_button.clicked(pos):
            self.reset()
            return True, self.RETRY_RESULT

        return False, None

    # -------------------------
    # タッチ操作
    # -------------------------

    def handle_finger_down(self, event, width, height):
        self.touch_moved = False

        self.touch_start_pos = (event.x * width, event.y * height)
        self.last_touch_pos = self.touch_start_pos

        self.active_touches[event.finger_id] = (event.x * width, event.y * height)

        if len(self.active_touches) == 2:
            self.pinch_distance = self.get_touch_distance()

        self.touch_dragging = True

    def handle_finger_motion(self, event, width, height):
        self.active_touches[event.finger_id] = (event.x * width, event.y * height)

        if len(self.active_touches) >= 2:
            # 2本指: ピンチズーム
            new_distance = self.get_touch_distance()
            self.touch_moved = True

            if self.pinch_distance and new_distance:
                zoom_ratio = new_distance / self.pinch_distance
                center = self.get_touch_center()

                if center:
                    self.zoom_at(center, self.zoom * zoom_ratio)

            self.pinch_distance = new_distance

        elif self.touch_dragging:
            # 1本指: ドラッグ移動
            current_pos = (event.x * width, event.y * height)

            dx = current_pos[0] - self.last_touch_pos[0]
            dy = current_pos[1] - self.last_touch_pos[1]

            self.camera_x -= dx / self.zoom
            self.camera_y -= dy / self.zoom

            move_dx = current_pos[0] - self.touch_start_pos[0]
            move_dy = current_pos[1] - self.touch_start_pos[1]

            if math.sqrt(move_dx * move_dx + move_dy * move_dy) > TAP_MOVE_THRESHOLD:
                self.touch_moved = True

            self.last_touch_pos = current_pos

    def handle_finger_up(self, event, width, height):
        # ほとんど動かさずに離したらタップとして扱う
        if not self.touch_moved:
            self.check_cell_click(self.screen_to_world((event.x * width, event.y * height)))

        self.touch_dragging = False

        if event.finger_id in self.active_touches:
            del self.active_touches[event.finger_id]

        if len(self.active_touches) < 2:
            self.pinch_distance = None

    def get_touch_distance(self):
        if len(self.active_touches) < 2:
            return None

        touches = list(self.active_touches.values())

        x1, y1 = touches[0]
        x2, y2 = touches[1]

        dx = x2 - x1
        dy = y2 - y1

        return math.sqrt(dx * dx + dy * dy)

    def get_touch_center(self):
        if len(self.active_touches) < 2:
            return None

        touches = list(self.active_touches.values())

        x1, y1 = touches[0]
        x2, y2 = touches[1]

        return (x1 + x2) / 2, (y1 + y2) / 2

    # =========================
    # カメラ
    # =========================

    def clamp_zoom(self, zoom):
        return max(self.MIN_ZOOM, min(zoom, self.MAX_ZOOM))

    def zoom_at(self, screen_pos, new_zoom):
        """画面上の screen_pos を固定したままズームする"""
        world_x, world_y = self.screen_to_world(screen_pos)

        self.zoom = self.clamp_zoom(new_zoom)

        self.camera_x = world_x - screen_pos[0] / self.zoom
        self.camera_y = world_y - screen_pos[1] / self.zoom

    def screen_to_world(self, pos):
        return (
            self.camera_x + pos[0] / self.zoom,
            self.camera_y + pos[1] / self.zoom
        )

    def reset_camera(self):
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 0.2

    # =========================
    # ゲーム状態
    # =========================

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

    def show_message(self, text):
        if text == "異常発見!":
            self.message = text
            self.message_timer = 120
            return

        if self.message_timer > 0:
            return

        self.message = text
        self.message_timer = 90

    def give_up(self):
        for cell in self.cells:
            if cell.is_target:
                cell.found = True

        self.clear_time = 0
        self.game_cleared = True
        self.giveup_flg = True

    def reset(self):
        self.game_cleared = False
        self.giveup_flg = False

        self.reset_camera()

    def get_elapsed_time(self):
        if self.game_cleared:
            return int(self.clear_time)

        return int(time.time() - self.start_time)

    # =========================
    # 細胞判定
    # =========================

    def check_cell_click(self, world_pos):
        now = pygame.time.get_ticks()

        if now - self.last_click_time < CLICK_INTERVAL_MS:
            return

        self.last_click_time = now

        if self.game_cleared or self.giveup_flg:
            return

        for cell in iter_neighbor_cells(self.grid, *world_pos):
            if cell.clicked(world_pos):
                self.on_cell_clicked(cell)
                break

    def on_cell_clicked(self, cell):
        """細胞がクリックされた時の処理。シーンごとに実装する"""
        raise NotImplementedError

    # =========================
    # 描画
    # =========================

    def draw_world(self, screen, width, height):
        """画面内のグリッドにある細胞だけを描画する"""
        view_right = self.camera_x + width / self.zoom
        view_bottom = self.camera_y + height / self.zoom

        grid_left = int(self.camera_x // self.grid_size)
        grid_right = int(view_right // self.grid_size)
        grid_top = int(self.camera_y // self.grid_size)
        grid_bottom = int(view_bottom // self.grid_size)

        for gx in range(grid_left, grid_right + 1):
            for gy in range(grid_top, grid_bottom + 1):
                for cell in self.grid.get((gx, gy), ()):
                    cell.draw(screen, self.camera_x, self.camera_y, width, height, self.zoom)

    def draw_status(self, screen):
        """画面左上の細胞数と経過時間"""
        cell_num = self.font.render(f"総細胞数: {len(self.cells)}", True, (0, 0, 0))
        screen.blit(cell_num, (20, 60))

        elapsed_time = self.get_elapsed_time()
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60

        timer_text = self.font.render(f"時間: {minutes:02}:{seconds:02}", True, (0, 0, 0))
        screen.blit(timer_text, (20, 100))

    def draw_message(self, screen, width):
        if self.message_timer > 0:
            text = self.font.render(self.message, True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(width // 2, 50)))

    def get_clear_text(self):
        return "クリア！"

    def draw_result(self, screen, width):
        """クリア / ギブアップ時の表示"""
        if self.game_cleared and not self.giveup_flg:
            clear_text = self.get_clear_text()

            c_text = self.font.render(clear_text, True, (0, 255, 0))
            c_outline = self.font.render(clear_text, True, (0, 0, 0))

            rect = c_text.get_rect(center=(width // 2, 100))

            # 縁取り
            for dx, dy in [
                (-2, 0), (2, 0),
                (0, -2), (0, 2),
                (-2, -2), (-2, 2),
                (2, -2), (2, 2)
            ]:
                screen.blit(c_outline, rect.move(dx, dy))

            screen.blit(c_text, rect)

            minutes = int(self.clear_time // 60)
            seconds = int(self.clear_time % 60)

            time_text = self.font.render(f"クリアタイム {minutes}分 {seconds}秒", True, (0, 0, 0))
            screen.blit(time_text, time_text.get_rect(center=(width // 2, 160)))

        elif self.giveup_flg:
            giveup_text = self.font.render("ギブアップ...", True, (255, 0, 0))
            screen.blit(giveup_text, giveup_text.get_rect(center=(width // 2, 100)))

    def draw_help_menu(self, screen):
        self.help_button.draw(screen)

        if self.help_menu_open:
            self.book_button.draw(screen)
            self.giveup_button.draw(screen)
            self.retry_button.draw(screen)

    def draw_minimap(self, screen, width, height):
        self.minimap_x = width - self.minimap_width - self.minimap_margin
        self.minimap_y = height - self.minimap_height - self.minimap_bottom_margin

        minimap_rect = (self.minimap_x, self.minimap_y, self.minimap_width, self.minimap_height)

        # 背景と枠
        pygame.draw.rect(screen, (30, 30, 30), minimap_rect, border_radius=10)
        pygame.draw.rect(screen, (220, 220, 220), minimap_rect, 2, border_radius=10)

        # 細胞（見つけた異常細胞は赤）
        for cell in self.cells:
            mx, my = self.world_to_minimap(cell.x, cell.y)

            if cell.is_target and cell.found:
                color = (255, 0, 0)
            else:
                color = (180, 180, 180)

            pygame.draw.circle(screen, color, (int(mx), int(my)), 2)

        # カメラ範囲
        cam_x, cam_y = self.world_to_minimap(self.camera_x, self.camera_y)

        cam_w = (width / self.zoom / self.world_width) * self.minimap_width
        cam_h = (height / self.zoom / self.world_height) * self.minimap_height

        pygame.draw.rect(screen, (0, 255, 255), (cam_x, cam_y, cam_w, cam_h), 2)

    def world_to_minimap(self, x, y):
        return (
            self.minimap_x + (x / self.world_width) * self.minimap_width,
            self.minimap_y + (y / self.world_height) * self.minimap_height
        )
