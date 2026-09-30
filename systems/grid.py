import math

# 細胞を空間分割して管理するグリッドの1マスの大きさ
GRID_SIZE = 80


def get_grid_pos(x, y):
    """ワールド座標が属するグリッドのマス座標を返す"""
    return int(x // GRID_SIZE), int(y // GRID_SIZE)


def iter_neighbor_cells(grid, x, y):
    """(x, y) を含むマスと周囲8マスにある細胞を順に返す"""
    gx, gy = get_grid_pos(x, y)

    for nx in range(gx - 1, gx + 2):
        for ny in range(gy - 1, gy + 2):
            yield from grid.get((nx, ny), ())


def is_overlapping(grid, x, y, radius):
    """周囲の細胞と大きく重なるかどうか"""
    for cell in iter_neighbor_cells(grid, x, y):
        dx = x - cell.x
        dy = y - cell.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < (radius + cell.radius) * 0.75:
            return True

    return False


def is_inside_world(x, y, radius, world_width, world_height):
    """細胞がワールドの外にはみ出さないかどうか"""
    return (
        x - radius >= 0 and
        x + radius <= world_width and
        y - radius >= 0 and
        y + radius <= world_height
    )


def add_to_grid(grid, cell):
    grid.setdefault(get_grid_pos(cell.x, cell.y), []).append(cell)
