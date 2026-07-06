from systems.load_distribution import load_distribution
import random
import math
from objects.cell import Cell

def generate_extra_map(world_data, cell_images):

    cells = []

    distribution = load_distribution(
        f"data/practice/world{world_data}.csv"
    )

    GRID_SIZE = 80

    grid = {}

    def get_grid_pos(x, y):

        gx = int(x // GRID_SIZE)
        gy = int(y // GRID_SIZE)

        return gx, gy
    
    clusters = []
    
    WORLD_WIDTH  = 10000
    WORLD_HEIGHT = 10000
    CLUSTER_COUNT = 200

    for _ in range(CLUSTER_COUNT):

        cx = random.uniform(200, WORLD_WIDTH - 200)

        cy = random.uniform(200, WORLD_HEIGHT - 200)

        clusters.append((cx, cy))

    def place_cell(info):

        for _ in range(500):

            cluster = random.choice(clusters)

            spread = 300

            x = cluster[0] + random.uniform(-spread, spread)
            y = cluster[1] + random.uniform(-spread, spread)

            radius = max(int(info["width"]), int(info["height"])) / 2

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

            if (gx, gy) not in grid:
                grid[(gx, gy)] = []

            grid[(gx, gy)].append(new_cell)

            return
        
        print(len(cells))

    total = sum(info["count"] for info in distribution)

    done = 0

    cells_to_generate = []

    for info in distribution:
        for _ in range(info["count"]):
            cells_to_generate.append(info)

    random.shuffle(cells_to_generate)

    for info in cells_to_generate:
            place_cell(info)
            done += 1

            if done % 100 == 0:
                yield done / total

    yield 1.0

    print("before return")

    return cells, grid, GRID_SIZE, WORLD_WIDTH, WORLD_HEIGHT, distribution