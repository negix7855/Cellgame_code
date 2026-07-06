import pygame
import math
import time
import os
from collections import defaultdict
from objects.button import Button

def resource_path(relative_path):
    return os.path.join(os.path.abspath("."), relative_path)

class ExtraExploreScene:

    def __init__(self, font, width, cells, grid, world_width, world_height, distribution):

        self.font = font


        self.camera_x = 0
        self.camera_y = 0

        self.zoom = 0.2

        self.dragging = False
        self.last_mouse_pos = (0, 0)

        self.touch_dragging = False
        self.touch_start_pos = (0, 0)
        self.last_touch_pos = (0, 0)
        self.touch_moved = False

        self.active_touches = {}
        self.pinch_distance = None

        self.game_cleared = False
        self.giveup_flg = False

        self.message = ""
        self.message_timer = 0

        self.grid = grid
        self.grid_size = 80

        self.cells = cells

        self.start_time = time.time()
        self.clear_time = 0

        self.world_width = world_width
        self.world_height = world_height

        self.minimap_width  = 220
        self.minimap_height = 220

        self.minimap_x = 0
        self.minimap_y = 0

        self.minimap_margin = 20

        self.last_click_time = 0

        self.confirm_giveup = False

        self.book_data = distribution

        self.found_cells = defaultdict(int)

        self.target_cells = []

        self.book_panel_height = 200

        self.can_go_practice = False


        self.retry_button = Button(
            width - 260,
            90,
            250,
            60,
            "タイトルへ",
            font
        )

        self.help_button = Button(
            width - 260,
            20,
            250,
            60,
            "？",
            font
        )

        self.help_menu_open = False

        self.book_button = Button(
            width - 260,
            230,
            250,
            60,
            "図鑑",
            font
        )

        self.giveup_button = Button(
            width - 220,
            340,
            250,
            60,
            "諦める",
            font
        )

        self.practice_button = Button(
            width // 2 - 125,
            80,
            250,
            60,
            "練習問題へGO!",
            font
        )

    def update_layout(self, width, height):

        self.retry_button.rect = pygame.Rect(
            width - 260,
            90,
            250,
            60,
        )

        self.giveup_button.rect = pygame.Rect(
            width - 260,
            160,
            250,
            60,
        )

        self.practice_button.rect = pygame.Rect(
            width // 2 - 125,
            80,
            250,
            60
        )

    def handle_event(self, event, width, height):

        if event.type == pygame.MOUSEBUTTONDOWN:

            pos = event.pos

            if event.button == 3:
                self.dragging = True
                self.last_mouse_pos = event.pos

            elif event.button == 1:

                # if self.retry_button.clicked(event.pos):

                #     self.found_count = 0

                #     self.game_cleared = False
                #     self.giveup_flg = False

                #     self.camera_x = 0
                #     self.camera_y = 0
                #     self.zoom = 0.2

                #     return "menu"

                if self.help_button.clicked(event.pos):
                    self.help_menu_open = not self.help_menu_open
                    return

                # elif self.giveup_button.clicked(event.pos):

                #     if not self.game_cleared:

                #         if not self.confirm_giveup:

                #             self.confirm_giveup = True
                #             self.show_message("もう一度押すとギブアップ")

                #         else:

                #             for cell in self.cells:
                #                 if cell.is_target:
                #                     cell.found = True

                #             self.clear_time = 0
                #             self.game_cleared = True
                #             self.giveup_flg = True

                #             self.confirm_giveup = False

                #     return

                world_x = self.camera_x + pos[0] / self.zoom
                world_y = self.camera_y + pos[1] / self.zoom

                self.check_cell_click((world_x, world_y))

                if self.help_menu_open:

                        if self.book_button.clicked(event.pos):
                            return "book"
                        
                        elif self.giveup_button.clicked(event.pos):

                            if not self.game_cleared:
                                    
                                for cell in self.cells:
                                    if cell.is_target:
                                        cell.found = True

                                self.clear_time = 0
                                self.game_cleared = True
                                self.giveup_flg = True
                                self.confirm_giveup = False

                            return
                        
                        elif self.retry_button.clicked(event.pos):

                            # self.found_count = 0

                            self.game_cleared = False
                            self.giveup_flg = False

                            self.camera_x = 0
                            self.camera_y = 0
                            self.zoom = 0.2

                            return "home"

                if self.can_go_practice:

                    if self.practice_button.clicked(event.pos):
                        return "practice"

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 3:
                self.dragging = False

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

            self.zoom = max(0.1, min(self.zoom, 2.0))

        elif event.type == pygame.FINGERDOWN:

            self.touch_moved = False

            self.touch_start_pos = (
                event.x * width,
                event.y * height
            )

            self.last_touch_pos = self.touch_start_pos

            self.active_touches[event.finger_id] = (
                event.x * width,
                event.y * height
            )

            if len(self.active_touches) == 2:

                self.pinch_distance = self.get_touch_distance()

            self.touch_dragging = True

        elif event.type == pygame.FINGERMOTION:

            self.active_touches[event.finger_id] = (
                event.x * width,
                event.y * height
            )

            if len(self.active_touches) >= 2:

                new_distance = self.get_touch_distance()
                self.touch_moved = True

                if self.pinch_distance and new_distance:

                    zoom_ratio = new_distance / self.pinch_distance

                    old_zoom = self.zoom

                    center = self.get_touch_center()

                    if center:

                        center_x, center_y = center

                        world_x = self.camera_x + center_x / old_zoom
                        world_y = self.camera_y + center_y / old_zoom

                        self.zoom *= zoom_ratio

                        self.zoom = max(0.1, min(self.zoom, 1.5))

                        self.camera_x = world_x - center_x / self.zoom
                        self.camera_y = world_y - center_y / self.zoom

                self.pinch_distance = new_distance

            elif self.touch_dragging:

                current_pos =(
                    event.x * width,
                    event.y * height
                )

                dx = current_pos[0] - self.last_touch_pos[0]
                dy = current_pos[1] - self.last_touch_pos[1]

                self.camera_x -= dx / self.zoom
                self.camera_y -= dy / self.zoom

                move_dx = (
                    current_pos[0] - self.touch_start_pos[0]
                )

                move_dy = (
                    current_pos[1] - self.touch_start_pos[1]
                )

                move_dist = math.sqrt(
                    move_dx * move_dx +
                    move_dy * move_dy
                )

                if move_dist > 15:
                    self.touch_moved = True

                self.last_touch_pos = current_pos

        elif event.type == pygame.FINGERUP:

            if not self.touch_moved:

                screen_x = event.x * width
                screen_y = event.y * height

                world_x = self.camera_x + screen_x / self.zoom
                world_y = self.camera_y + screen_y / self.zoom

                self.check_cell_click((world_x, world_y))

            self.touch_dragging = False

            if event.finger_id in self.active_touches:
                del self.active_touches[event.finger_id]

            if len(self.active_touches) < 2:
                self.pinch_distance = None



    def update(self):

        if self.message_timer > 0:

            self.message_timer -= 1

    def draw(self, screen, cell_images):

        width, height = screen.get_size()

        screen.fill((255, 255, 255))

        view_left = self.camera_x
        view_top = self.camera_y

        view_right = self.camera_x + width / self.zoom
        view_bottom = self.camera_y + height / self.zoom

        grid_left = int(view_left // self.grid_size)
        grid_right = int(view_right // self.grid_size)

        grid_top = int(view_top // self.grid_size)
        grid_bottom = int(view_bottom // self.grid_size)


        for gx in range(grid_left, grid_right + 1):
            for gy in range(grid_top, grid_bottom + 1):

                if (gx, gy) not in self.grid:
                    continue

                for cell in self.grid[(gx, gy)]:

                    cell.draw(
                        screen,
                        self.camera_x,
                        self.camera_y,
                        width,
                        height,
                        self.zoom
                    )
        cell_num = self.font.render(
            f"総細胞数: {len(self.cells)}",
            True,
            (0, 0, 0)
        )
        screen.blit(cell_num, (20, 60))

        if self.game_cleared:
            elapsed_time = int(self.clear_time)
        else:
            elapsed_time = int(time.time() - self.start_time)

        minutes = elapsed_time // 60
        seconds = elapsed_time % 60

        timer_text = self.font.render(
            f"時間: {minutes:02}:{seconds:02}",
            True,
            (0, 0, 0)
        )

        screen.blit(timer_text, (20, 100))

        # メッセージ
        if self.message_timer > 0:

            text = self.font.render(
                self.message,
                True,
                (0, 0, 0)
            )

            rect = text.get_rect(center=(width // 2, 50))

            screen.blit(text, rect)

        if self.game_cleared and not self.giveup_flg:
            clear_text = f"クリア！"

            c_text = self.font.render(
                clear_text,
                True,
                (0, 255, 0)
                )
            
            c_outline = self.font.render(
                clear_text,
                True,
                (0, 0, 0)
            )

            rect = c_text.get_rect(center=(width // 2, 100))

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

            time_text = self.font.render(
                f"クリアタイム {minutes}分 {seconds}秒",
                True,
                (0, 0, 0)
            )

            screen.blit(
                time_text,
                time_text.get_rect(center=(width // 2, 160))
            )


        elif self.giveup_flg:
            giveup_text = self.font.render("ギブアップ...", True, (255, 0, 0))
            screen.blit(giveup_text, giveup_text.get_rect(center=(width // 2, 100)))

        self.help_button.draw(screen)

        if self.help_menu_open:
            self.book_button.draw(screen)
            self.giveup_button.draw(screen)
            self.retry_button.draw(screen)

        if self.can_go_practice:
            self.practice_button.draw(screen)

        self.draw_minimap(screen, width, height)

        self.draw_book_panel(screen)

        x = 30
        y = height - 200

        for info in self.book_data:

            image = cell_images[info["cell_name"]]

            count = self.found_cells.get(info["cell_name"], 0)

            icon = pygame.transform.smoothscale(image, (150, 150))

            if info["cell_name"] not in self.found_cells:

                icon = pygame.transform.grayscale(icon)
                icon.set_alpha(120)

            screen.blit(icon, (x, y))

            text = self.font.render(f"{count}個発見", True, (0,0,0))
            screen.blit(text, (x, y + 155))

            x += 200

        completed = True

        for info in self.book_data:

            if self.found_cells.get(info["cell_name"], 0) < 1:
                completed = False
                break

        self.can_go_practice = completed


    # =========================
    # メッセージ表示
    # =========================

    def show_message(self, text):

        if text == "異常発見!":
            self.message = text
            self.message_timer = 120
            return

        if self.message_timer > 0:
            return
        self.message = text
        self.message_timer = 90

    # =========================
    # 細胞判定
    # =========================

    def check_cell_click(self, world_pos):

        now = pygame.time.get_ticks()
        self.confirm_giveup = False

        if now - self.last_click_time < 500:
            return
    
        self.last_click_time = now

        if self.game_cleared or self.giveup_flg:
            return

        world_x, world_y = world_pos

        gx = int(world_x // self.grid_size)
        gy = int(world_y // self.grid_size)

        clicked_any = False

        for nx in range(gx - 1, gx + 2):
            for ny in range(gy - 1, gy + 2):

                if (nx, ny) not in self.grid:
                    continue

                for cell in self.grid[(nx, ny)]:

                    if cell.clicked(world_pos):

                        clicked_any = True

                        if not cell.found:

                            cell.found = True

                            # self.correct_sound.play()

                            if cell.can_count:

                                self.found_cells[cell.cell_name] += 1

                                cell.can_count = False

                            # self.found_count += 1

                            # if not self.game_cleared:

                            #     self.game_cleared = True

                            #     self.clear_time = (
                            #         time.time() - self.start_time
                            #     )

                            count = self.found_cells[cell.cell_name]

                            self.message = f"{cell.display_name} 発見！ {count}個目"
                            self.message_timer = 120

                        # else:
                        #     # self.miss_sound.play()

                        #     # self.show_message("ざんねん...")

                        break

                if clicked_any:
                    break

            if clicked_any:
                break

    # =========================
    # ピンチズーム用関数
    # =========================
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

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        return center_x, center_y

    # =========================
    # ミニマップ描画関数
    # =========================
    def draw_minimap(self, screen, width, height):

        self.minimap_x = width - self.minimap_width - self.minimap_margin
        self.minimap_y = height - self.minimap_height - self.minimap_margin * 10

        # 背景
        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (self.minimap_x, self.minimap_y,
            self.minimap_width, self.minimap_height),
            border_radius=10
        )

        # 枠
        pygame.draw.rect(
            screen,
            (220, 220, 220),
            (self.minimap_x, self.minimap_y,
            self.minimap_width, self.minimap_height),
            2,
            border_radius=10
        )

        # 細胞描画
        for cell in self.cells:

            mx = self.minimap_x + (cell.x / self.world_width) * self.minimap_width
            my = self.minimap_y + (cell.y / self.world_height) * self.minimap_height

            if cell.is_target:

                if cell.found:
                    color = (255, 0, 0)
                else:
                    color = (180, 180, 180)

            else:
                color = (180, 180, 180)

            pygame.draw.circle(
                screen,
                color,
                (int(mx), int(my)),
                2
            )

        # カメラ範囲
        view_w = width / self.zoom
        view_h = height / self.zoom

        cam_x = self.minimap_x + (self.camera_x / self.world_width) * self.minimap_width
        cam_y = self.minimap_y + (self.camera_y / self.world_height) * self.minimap_height

        cam_w = (view_w / self.world_width) * self.minimap_width
        cam_h = (view_h / self.world_height) * self.minimap_height

        pygame.draw.rect(
            screen,
            (0, 255, 255),
            (cam_x, cam_y, cam_w, cam_h),
            2
        )

    def draw_book_panel(self, screen):

        width, height = screen.get_size()

        panel_rect = pygame.Rect(
            0,
            height - self.book_panel_height,
            width,
            self.book_panel_height
        )

        pygame.draw.rect(screen, (40,40,40), panel_rect)

    def get_found_cells(self):

        result = []
        added = set()

        for cell in self.cells:

            if cell.found and cell.cell_name not in added:

                result.append(cell)
                added.add(cell.cell_name)

        return result