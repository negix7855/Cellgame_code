import random

from objects.cell import Cell
from systems.grid import GRID_SIZE, add_to_grid, is_inside_world, is_overlapping
from systems.load_distribution import load_distribution

WORLD_WIDTH = 10000
WORLD_HEIGHT = 10000
CLUSTER_COUNT = 200
CLUSTER_SPREAD = 300
MAX_PLACE_ATTEMPTS = 500


# =========================
# マップ生成（エクストラモード）
# =========================

def generate_extra_map(world_data, cell_images, data_folder="practice", file_prefix="world"):
    """CSV の分布に従って細胞を配置するジェネレータ。

    data/{data_folder}/{file_prefix}{world_data}.csv を読み込む。
    進捗 (0.0〜1.0) を yield し、完了時に
    (cells, grid, GRID_SIZE, world_width, world_height, distribution) を返す。
    """
    cells = []
    grid = {}

    distribution = load_distribution(
        f"data/{data_folder}/{file_prefix}{world_data}.csv"
    )

    # -------------------------
    # クラスタ生成
    # -------------------------

    clusters = []

    for _ in range(CLUSTER_COUNT):
        cx = random.uniform(200, WORLD_WIDTH - 200)
        cy = random.uniform(200, WORLD_HEIGHT - 200)
        clusters.append((cx, cy))

    # -------------------------
    # 細胞配置
    # -------------------------

    def place_cell(info):
        radius = max(info["width"], info["height"]) / 2

        for _ in range(MAX_PLACE_ATTEMPTS):
            cluster = random.choice(clusters)

            x = cluster[0] + random.uniform(-CLUSTER_SPREAD, CLUSTER_SPREAD)
            y = cluster[1] + random.uniform(-CLUSTER_SPREAD, CLUSTER_SPREAD)

            if not is_inside_world(x, y, radius, WORLD_WIDTH, WORLD_HEIGHT):
                continue

            if is_overlapping(grid, x, y, radius):
                continue

            new_cell = Cell(
                x=x,
                y=y,
                image=cell_images[info["cell_name"]],
                width=info["width"],
                height=info["height"],
                cell_name=info["cell_name"],
                display_name=info["display_name"]
            )

            cells.append(new_cell)
            add_to_grid(grid, new_cell)
            return

    cells_to_generate = [
        info
        for info in distribution
        for _ in range(info["count"])
    ]

    random.shuffle(cells_to_generate)

    total = len(cells_to_generate)
    done = 0

    for info in cells_to_generate:
        place_cell(info)
        done += 1

        if done % 100 == 0:
            yield done / total

    yield 1.0

    return cells, grid, GRID_SIZE, WORLD_WIDTH, WORLD_HEIGHT, distribution
