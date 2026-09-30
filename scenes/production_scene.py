import pygame
import math
from objects.button import Button


class ProductionScene:

    def __init__(
            self,
            font,
            width,
            cells,
            grid,
            world_width,
            world_height,
            distribution,
            world_data
        ):
        self.font = font

        self.width = width

        self.cells = cells
        self.grid = grid
        self.grid_size = 80

        self.world_width = world_width
        self.world_height = world_height

        self.distribution = distribution

        self.world_data = world_data


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


        self.minimap_width = 220
        self.minimap_height = 220

        self.minimap_x = 0
        self.minimap_y = 0

        self.minimap_margin = 20

        self.answer_buttons = []

        self.answer_choices = [
            "NILM 正常",
            "NILM 感染症・炎症",
            "LSIL",
            "HSIL",
            "SCC"
        ]

        self.question_number = 1

        self.answered = False
        self.correct_answer = None
        self.answer_reslut = None

        start_y = 100

        for i, answer in enumerate(self.answer_choices):
            button = Button(
                self.width - 280,
                start_y + i * 70,
                250,
                60,
                answer,
                self.font
            )

        self.answer_buttons.append(button)


    def handle_event(self, event, width, height):

        # =========================
        # マウス操作
        # =========================

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                for button in self.answer_buttons:

                    if button.clicked(event.pos):

                        self.ansered = True

                        if button.text == self.correct_answer:

                            self.answer_result = "正解"

                        else:

                            self.answer_reslut = "不正解"

                        print(button.text)
                        print(self.answer_reslut)

                        break

            elif event.button == 3:

                self.dragging = True
                self.last_mouse_pos = event.pos

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

        # =========================
        # マウスホイール
        # =========================

        elif event.type == pygame.MOUSEWHEEL:

            if event.y > 0:

                self.zoom *= 1.1

            else:

                self.zoom /= 1.1

            self.zoom = max(
                0.1,
                min(self.zoom, 3.0)
            )

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

                        self.zoom = max(0.1, min(self.zoom, 3.0))

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


    def draw(self, screen):

        width, height = screen.get_size()

        # =========================
        # 背景
        # =========================

        screen.fill((255, 255, 255))

        # =========================
        # 細胞を描画
        # =========================

        for cell in self.cells:

            cell.draw(
                screen,
                self.camera_x,
                self.camera_y,
                width,
                height,
                self.zoom
            )

        # =========================
        # 回答ボタン
        # =========================

        for button in self.answer_buttons:

            button.draw(screen)

        # =========================
        # ミニマップ
        # =========================

        self.draw_minimap(
            screen,
            width,
            height
        )

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


    def draw_minimap(self, screen, width, height):

        self.minimap_x = (
            width
            - self.minimap_width
            - self.minimap_margin
        )

        self.minimap_y = (
            height
            - self.minimap_height
            - self.minimap_margin * 10
        )

        # =========================
        # 背景
        # =========================

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            (
                self.minimap_x,
                self.minimap_y,
                self.minimap_width,
                self.minimap_height
            ),
            border_radius=10
        )

        # =========================
        # 枠
        # =========================

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            (
                self.minimap_x,
                self.minimap_y,
                self.minimap_width,
                self.minimap_height
            ),
            2,
            border_radius=10
        )

        # =========================
        # 細胞
        # =========================

        for cell in self.cells:

            mx = (
                self.minimap_x
                + (cell.x / self.world_width)
                * self.minimap_width
            )

            my = (
                self.minimap_y
                + (cell.y / self.world_height)
                * self.minimap_height
            )

            pygame.draw.circle(
                screen,
                (180, 180, 180),
                (int(mx), int(my)),
                2
            )

        # =========================
        # カメラ範囲
        # =========================

        view_w = width / self.zoom
        view_h = height / self.zoom

        cam_x = (
            self.minimap_x
            + (self.camera_x / self.world_width)
            * self.minimap_width
        )

        cam_y = (
            self.minimap_y
            + (self.camera_y / self.world_height)
            * self.minimap_height
        )

        cam_w = (
            view_w / self.world_width
        ) * self.minimap_width

        cam_h = (
            view_h / self.world_height
        ) * self.minimap_height

        pygame.draw.rect(
            screen,
            (0, 255, 255),
            (cam_x, cam_y, cam_w, cam_h),
            2
        )


