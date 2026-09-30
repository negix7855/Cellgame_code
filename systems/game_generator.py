import random

from objects.cell import Cell
from systems.grid import GRID_SIZE, add_to_grid, is_inside_world, is_overlapping

CLUSTER_COUNT = 200
MAX_PLACE_ATTEMPTS = 500


# =========================
# ゲーム生成（ノーマルモード）
# =========================

def get_world_settings(normal_cell_count):
    """正常細胞数に応じたワールドの大きさとクラスタの広がりを返す"""
    if normal_cell_count < 1500:
        return 5000, 150

    elif normal_cell_count < 3500:
        return 10000, 300

    elif normal_cell_count < 10000:
        return 15000, 450

    else:
        return 20000, 1000


def generate_game(normal_cell_count, abnormal_cell_count, normal_images, abnormal_images):
    """細胞を配置するジェネレータ。

    進捗 (0.0〜1.0) を yield し、完了時に
    (cells, grid, GRID_SIZE, world_width, world_height) を返す。
    """
    cells = []
    grid = {}

    world_size, spread = get_world_settings(normal_cell_count)
    world_width = world_size
    world_height = world_size

    # -------------------------
    # クラスタ生成
    # -------------------------

    clusters = []

    for _ in range(CLUSTER_COUNT):
        cx = random.uniform(200, world_width - 200)
        cy = random.uniform(200, world_height - 200)
        clusters.append((cx, cy))

    # -------------------------
    # 細胞配置
    # -------------------------

    def place_cell(is_target):
        for _ in range(MAX_PLACE_ATTEMPTS):
            cluster = random.choice(clusters)

            x = cluster[0] + random.uniform(-spread, spread)
            y = cluster[1] + random.uniform(-spread, spread)

            radius = random.uniform(45, 55)

            if not is_inside_world(x, y, radius, world_width, world_height):
                continue

            if is_overlapping(grid, x, y, radius):
                continue

            images = abnormal_images if is_target else normal_images

            new_cell = Cell(
                x=x,
                y=y,
                image=random.choice(images),
                width=radius,
                height=radius,
                is_target=is_target
            )

            cells.append(new_cell)
            add_to_grid(grid, new_cell)
            return

    total = abnormal_cell_count + normal_cell_count
    done = 0

    # 異常細胞を先に配置
    for i in range(abnormal_cell_count):
        place_cell(True)
        done += 1

        if i % 5 == 0:
            yield done / total

    # 正常細胞
    for i in range(normal_cell_count):
        place_cell(False)
        done += 1

        if i % 100 == 0:
            yield done / total

    yield 1.0

    return cells, grid, GRID_SIZE, world_width, world_height
