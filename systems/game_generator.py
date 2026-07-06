import random
import math
from objects.cell import Cell
import asyncio

# =========================
# ゲーム生成
# =========================

def generate_game(
        normal_cell_count,
        abnormal_cell_count,
        normal_images,
        abnormal_images
):

    cells = []

    GRID_SIZE = 80

    grid = {}

    def get_grid_pos(x, y):

        gx = int(x // GRID_SIZE)
        gy = int(y // GRID_SIZE)

        return gx, gy
    # -------------------------
    # クラスタ生成
    # -------------------------

    #center_x = WORLD_WIDTH // 2
    #center_y = WORLD_HEIGHT // 2

    clusters = []

    if normal_cell_count < 1500:
        WORLD_WIDTH  = 5000
        WORLD_HEIGHT = 5000
        CLUSTER_COUNT = 200

    elif normal_cell_count < 3500:
        WORLD_WIDTH  = 10000
        WORLD_HEIGHT = 10000
        CLUSTER_COUNT = 200

    elif normal_cell_count < 10000:
        WORLD_WIDTH  = 15000
        WORLD_HEIGHT = 15000
        CLUSTER_COUNT = 300

    else:
        WORLD_WIDTH  = 20000
        WORLD_HEIGHT = 20000
        CLUSTER_COUNT = 350

    CLUSTER_COUNT = 200
    #GLOBAL_SPREAD = 1800

    for _ in range(CLUSTER_COUNT):

        cx = random.uniform(200, WORLD_WIDTH - 200)

        cy = random.uniform(200, WORLD_HEIGHT - 200)

        clusters.append((cx, cy))

    # -------------------------
    # 細胞配置関数
    # -------------------------

    def place_cell(is_target):

        for _ in range(500):

            cluster = random.choice(clusters)

            if normal_cell_count < 1500:
                spread = 150

            elif normal_cell_count < 3500:
                spread = 300

            elif normal_cell_count < 10000:
                spread = 450

            else:
                spread = 1000

            x = cluster[0] + random.uniform(-spread, spread)
            y = cluster[1] + random.uniform(-spread, spread)

            radius = random.uniform(45, 55)

            # 画面外防止
            if (
                x - radius < 0 or
                x + radius > WORLD_WIDTH or
                y - radius < 0 or
                y + radius > WORLD_HEIGHT
            ):
                continue

            overlap = False

            gx, gy = get_grid_pos(x, y)

            overlap = False

            # 周囲9マスだけ調べる
            for nx in range(gx - 1, gx + 2):
                for ny in range(gy - 1, gy + 2):

                    if (nx, ny) not in grid:
                        continue

                    for cell in grid[(nx, ny)]:

                        dx = x - cell.x
                        dy = y - cell.y

                        dist = math.sqrt(dx * dx + dy * dy)

                        if dist < (radius + cell.radius) * 0.75:

                            overlap = True
                            break

                    if overlap:
                        break

                if overlap:
                    break

            if overlap:
                continue

            if is_target:
                image = random.choice(abnormal_images)
            else:
                image = random.choice(normal_images)

            new_cell = Cell(
                x=x,
                y=y,
                image=image,
                width=radius,
                height=radius,
                is_target=is_target
            )

            cells.append(new_cell)

            if (gx, gy) not in grid:
                grid[(gx, gy)] = []

            grid[(gx, gy)].append(new_cell)

            return
        
        print(len(cells))

    total = abnormal_cell_count + normal_cell_count
    done = 0

    # 間違い画像を先に配置
    for i in range(abnormal_cell_count):
        place_cell(True)
        done += 1

        if i % 5 == 0:
            yield done / total

    # 通常細胞
    for i in range(normal_cell_count):
        place_cell(False)
        done += 1

        if i % 100 == 0:
            yield done / total

    yield 1.0

    return cells, grid, GRID_SIZE, WORLD_WIDTH, WORLD_HEIGHT