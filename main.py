import os
import pygame
import asyncio
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene
from scenes.book_scene import BookScene
from scenes.home_scene import HomeScene
from scenes.loading_scene import LoadingScene
from scenes.difficluty_menu_scene import DiffMenuScene
from scenes.extra_explore_scene import ExtraExploreScene
from scenes.extra_practice_scene import ExtraPracticeScene
from setting import STAGES
from systems.game_generator import generate_game
from systems.generate_extra_map import generate_extra_map

def resource_path(relative_path):
    return os.path.join(os.path.abspath("."), relative_path)

pygame.mixer.pre_init(
    frequency=44100,
    size=-16,
    channels=2,
    buffer=2048
)

pygame.init()

# =========================
# # シーン管理
# =========================

SCENE_HOME = 0
SCENE_DIFFMENU = 1
SCENE_GAME = 2
SCENE_BOOK = 3
SCENE_LOADING = 4
SCENE_EXTRA_EXPLORE = 5
SCENE_EXTRA_PRACTICE = 6

current_scene = SCENE_HOME
book_return_scene = SCENE_DIFFMENU
NormOrExtra = SCENE_GAME

# =========================
# 設定
# =========================

WORLD_WIDTH  = 10000
WORLD_HEIGHT = 10000

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

NORMAL_CELL_COUNT = 1000
ABNORMAL_CELL_COUNT = 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Oruccha")

# font = pygame.font.Font(resource_path("fonts/NotoSansJP-VariableFont_wght.ttf"), 32)
font = pygame.font.Font(resource_path("fonts/MPLUS1p-Bold.ttf"), 32)
font.set_bold(True)

start_time = 0
clear_time = 0
game_cleared = False


touch_dragging = False
touch_start_pos = (0, 0)
last_touch_pos  = (0, 0)
touch_moved = False

active_touches = {}
pinch_distance = None

world_data = 1

# =========================
# 画像読み込み
# =========================

normal_images = [
    pygame.image.load(resource_path("images/cells/normal_1.png")).convert_alpha(),
    pygame.image.load(resource_path("images/cells/normal_2.png")).convert_alpha(),
]

abnormal_images = [
    pygame.image.load(resource_path("images/cells/abnormal_1.png")).convert_alpha(),
    pygame.image.load(resource_path("images/cells/abnormal_2.png")).convert_alpha(),
    pygame.image.load(resource_path("images/cells/abnormal_3.png")).convert_alpha(),
    pygame.image.load(resource_path("images/cells/abnormal_4.png")).convert_alpha(),
    pygame.image.load(resource_path("images/cells/abnormal_5.png")).convert_alpha(),
    pygame.image.load(resource_path("images/cells/abnormal_6.png")).convert_alpha(),
]

book_images = [
    pygame.image.load(resource_path("images/book/normal_1.jpg")).convert(),
    pygame.image.load(resource_path("images/book/normal_2.jpg")).convert(),
    pygame.image.load(resource_path("images/book/abnormal_1.jpg")).convert(),
    pygame.image.load(resource_path("images/book/abnormal_2.jpg")).convert(),
    pygame.image.load(resource_path("images/book/abnormal_3.jpg")).convert(),
    pygame.image.load(resource_path("images/book/abnormal_4.jpg")).convert(),
    pygame.image.load(resource_path("images/book/abnormal_5.jpg")).convert(),
    pygame.image.load(resource_path("images/book/abnormal_6.jpg")).convert(),
]

extra_cell_images = {
    "NILM_norm_1": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_1.png")).convert_alpha(),
    "NILM_norm_2": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_2.png")).convert_alpha(),
    "NILM_norm_3": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_3.png")).convert_alpha(),
    "NILM_norm_4": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_4.png")).convert_alpha(),
    "NILM_norm_5": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_5.png")).convert_alpha(),
    "NILM_norm_6": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_6.png")).convert_alpha(),
    "NILM_norm_7": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_7.png")).convert_alpha(),
    "NILM_norm_8": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_8.png")).convert_alpha(),
    "NILM_norm_9": pygame.image.load(resource_path("images/extra_prac_cells/NILM_norm_9.png")).convert_alpha(),
    "NILM_abnorm_1": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_1.png")).convert_alpha(),
    "NILM_abnorm_2": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_2.png")).convert_alpha(),
    "NILM_abnorm_3": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_3.png")).convert_alpha(),
    "NILM_abnorm_4": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_4.png")).convert_alpha(),
    "NILM_abnorm_5": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_5.png")).convert_alpha(),
    "NILM_abnorm_6": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_6.png")).convert_alpha(),
    "NILM_abnorm_7": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_7.png")).convert_alpha(),
    "NILM_abnorm_8": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_8.png")).convert_alpha(),
    "NILM_abnorm_9": pygame.image.load(resource_path("images/extra_prac_cells/NILM_abnorm_9.png")).convert_alpha(),
    "LSIL_1": pygame.image.load(resource_path("images/extra_prac_cells/LSIL_1.png")).convert_alpha(),
    "LSIL_2": pygame.image.load(resource_path("images/extra_prac_cells/LSIL_2.png")).convert_alpha(),
    "LSIL_3": pygame.image.load(resource_path("images/extra_prac_cells/LSIL_3.png")).convert_alpha(),
    "LSIL_4": pygame.image.load(resource_path("images/extra_prac_cells/LSIL_4.png")).convert_alpha(),
    "LSIL_5": pygame.image.load(resource_path("images/extra_prac_cells/LSIL_5.png")).convert_alpha(),
    "LSIL_6": pygame.image.load(resource_path("images/extra_prac_cells/LSIL_6.png")).convert_alpha(),
    "HSIL_1": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_1.png")).convert_alpha(),
    "HSIL_2": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_2.png")).convert_alpha(),
    "HSIL_3": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_3.png")).convert_alpha(),
    "HSIL_4": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_4.png")).convert_alpha(),
    "HSIL_5": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_5.png")).convert_alpha(),
    "HSIL_6": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_6.png")).convert_alpha(),
    "HSIL_7": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_7.png")).convert_alpha(),
    "HSIL_8": pygame.image.load(resource_path("images/extra_prac_cells/HSIL_8.png")).convert_alpha(),
    "SCC_1": pygame.image.load(resource_path("images/extra_prac_cells/SCC_1.png")).convert_alpha(),
    "SCC_2": pygame.image.load(resource_path("images/extra_prac_cells/SCC_2.png")).convert_alpha(),
    "SCC_3": pygame.image.load(resource_path("images/extra_prac_cells/SCC_3.png")).convert_alpha(),
    "SCC_4": pygame.image.load(resource_path("images/extra_prac_cells/SCC_4.png")).convert_alpha(),
    "SCC_5": pygame.image.load(resource_path("images/extra_prac_cells/SCC_5.png")).convert_alpha(),
    "SCC_6": pygame.image.load(resource_path("images/extra_prac_cells/SCC_6.png")).convert_alpha(),
    "SCC_7": pygame.image.load(resource_path("images/extra_prac_cells/SCC_7.png")).convert_alpha(),
    "SCC_8": pygame.image.load(resource_path("images/extra_prac_cells/SCC_8.png")).convert_alpha(),
}

home_background = pygame.image.load(
    resource_path("images/background/home.png")
).convert_alpha()

diffmenu_background = pygame.image.load(
    resource_path("images/background/diffmenu.jpg")
).convert()

HOME_BGM = resource_path("sounds/BGM/home_bgm.ogg")
DIFFMENU_BGM = resource_path("sounds/BGM/diffmenu_bgm.ogg")
GAME_BGM = resource_path("sounds/BGM/normalgame_bgm.ogg")

current_bgm = None

# クロック準備
clock = pygame.time.Clock()

# シーン初期化
home_scene = HomeScene(
    font,
    WIDTH,
    HEIGHT,
    home_background
)

menu_scene = MenuScene(
    font,
    WIDTH,
    HEIGHT
)

game_scene = None

diff_menu_scene = DiffMenuScene(
    font,
    WIDTH,
    HEIGHT,
    diffmenu_background
)

book_scene = BookScene(
    font,
    WIDTH,
    HEIGHT,
    book_images
)

loading_scene = LoadingScene(
    font
)

extra_explore_scene = None

extra_practice_scene = None


def play_bgm(path):

    global current_bgm

    if current_bgm == path:
        return
    
    current_bgm = path

    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

async def main():

    global current_scene
    global NORMAL_CELL_COUNT
    global ABNORMAL_CELL_COUNT
    global cells
    global grid
    global GRID_SIZE
    global WORLD_WIDTH
    global WORLD_HEIGHT
    global WIDTH
    global HEIGHT
    global current_stage
    global world_data

    current_stage = None

    generator = None

    loading_started = False

    running = True

    cells = []
    grid = {}
    GRID_SIZE = 80

    play_bgm(HOME_BGM)

    # =========================
    # メインループ
    # =========================

    while running:

        WIDTH, HEIGHT = screen.get_size()

        clock.tick(60)

        # if current_scene == SCENE_MENU:
        if current_scene == SCENE_DIFFMENU:
            diff_menu_scene.update_layout(WIDTH, HEIGHT)

        elif current_scene == SCENE_GAME:
            game_scene.update_layout(WIDTH, HEIGHT)

        elif current_scene == SCENE_EXTRA_EXPLORE:
            extra_explore_scene.update_layout(WIDTH, HEIGHT)

        for event in pygame.event.get():
                
            if current_scene == SCENE_HOME:

                if event.type == pygame.QUIT:
                    running = False

                result = home_scene.handle_event(event)

                if result == "normal":
                    current_scene = SCENE_DIFFMENU
                    NormOrExtra = SCENE_GAME
                    play_bgm(DIFFMENU_BGM)

                elif result == "extra":

                    NormOrExtra = SCENE_EXTRA_EXPLORE

                    pygame.mixer.music.stop()

                    generator = generate_extra_map(
                        world_data=world_data,
                        cell_images=extra_cell_images
                    )

                    print(type(generator))

                    current_scene = SCENE_LOADING

            elif current_scene == SCENE_DIFFMENU:

                if event.type == pygame.QUIT:
                    running = False

                # result = menu_scene.handle_event(event)
                result = diff_menu_scene.handle_event(event)

                if result:

                    if result["action"] == "start":

                        pygame.mixer.music.stop()

                        current_stage = result["stage"]

                        config = STAGES[current_stage]

                        generator = generate_game(
                            config["normal_cells"],
                            config["abnormal_cells"],
                            normal_images,
                            abnormal_images
                        )

                        current_scene = SCENE_LOADING

                    elif result["action"] == "book":

                        book_return_scene = SCENE_DIFFMENU
                        current_scene = SCENE_BOOK

                    elif result["action"] == "home":

                        current_scene = SCENE_HOME
                        play_bgm(HOME_BGM)


            elif current_scene == SCENE_GAME:

                if event.type == pygame.QUIT:
                    running = False

                result = game_scene.handle_event(event, WIDTH, HEIGHT)

                if result == "menu":
                    game_scene=None
                    cells = None
                    grid = None

                    import gc
                    gc.collect()
                    current_scene = SCENE_DIFFMENU
                    play_bgm(DIFFMENU_BGM)

                elif result == "book":

                    book_return_scene = SCENE_GAME
                    current_scene = SCENE_BOOK

            elif current_scene == SCENE_BOOK:

                if event.type == pygame.QUIT:
                    running = False

                result = book_scene.handle_event(event)

                if result == "menu":
                    current_scene = book_return_scene

                    if current_scene == SCENE_DIFFMENU:
                        play_bgm(DIFFMENU_BGM)

                    elif current_scene == SCENE_GAME:
                        play_bgm(GAME_BGM)

            elif current_scene == SCENE_EXTRA_EXPLORE:

                if event.type == pygame.QUIT:
                    running = False

                result = extra_explore_scene.handle_event(event)

                if result == "home":
                    current_scene = SCENE_HOME
                    play_bgm(HOME_BGM)

                elif result == "practice":
                    current_scene = SCENE_EXTRA_PRACTICE
                    extra_practice_scene = ExtraPracticeScene(
                        font,
                        WIDTH,
                        HEIGHT,
                        world_data,
                        extra_explore_scene.get_found_cells()
                    )

            elif current_scene == SCENE_EXTRA_PRACTICE:

                if event.type == pygame.QUIT:
                    running = False

                result = extra_practice_scene.handle_event(event)

                if result == "next_world":
                    world_data += 1

                    pygame.mixer.music.stop()

                    generator = generate_extra_map(
                        world_data=world_data,
                        cell_images=extra_cell_images
                    )

                    print(type(generator))

                    current_scene = SCENE_LOADING

                elif result == "retry":
                    pygame.mixer.music.stop()

                    generator = generate_extra_map(
                        world_data=world_data,
                        cell_images=extra_cell_images
                    )

                    print(type(generator))

                    current_scene = SCENE_LOADING


        # -------------------------
        # 描画
        # -------------------------

        # ホーム画面
        if current_scene == SCENE_HOME:

            home_scene.draw(screen)

        # メニュー画面
        if current_scene == SCENE_DIFFMENU:

            diff_menu_scene.draw(screen)


        # ゲーム画面
        elif current_scene == SCENE_GAME:

            game_scene.update()

            game_scene.draw(screen)

        # 図鑑画面
        elif current_scene == SCENE_BOOK:

            book_scene.draw(screen)

        elif current_scene == SCENE_LOADING:

            loading_scene.draw(screen)

            try:
                progress = next(generator)
                loading_scene.set_progressa(progress)

            except StopIteration as result:

                if NormOrExtra == SCENE_GAME:

                    cells, grid, GRID_SIZE, WORLD_WIDTH, WORLD_HEIGHT = result.value

                    config = STAGES[current_stage]

                    game_scene = GameScene(
                        font,
                        WIDTH,
                        config["abnormal_cells"],
                        cells,
                        grid,
                        WORLD_WIDTH,
                        WORLD_HEIGHT
                    )

                    current_scene = SCENE_GAME
                    play_bgm(GAME_BGM)

                elif NormOrExtra == SCENE_EXTRA_EXPLORE:

                    cells, grid, GRID_SIZE, WORLD_WIDTH, WORLD_HEIGHT, distribution = result.value

                    extra_explore_scene = ExtraExploreScene(
                        font,
                        WIDTH,
                        cells,
                        grid,
                        WORLD_WIDTH,
                        WORLD_HEIGHT,
                        distribution
                    )

                    current_scene = SCENE_EXTRA_EXPLORE
                    play_bgm(GAME_BGM)

        elif current_scene == SCENE_EXTRA_EXPLORE:

            extra_explore_scene.update()

            extra_explore_scene.draw(screen, extra_cell_images)

        elif current_scene == SCENE_EXTRA_PRACTICE:

            extra_practice_scene.update()

            extra_practice_scene.draw(screen)


        pygame.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())