import asyncio
import gc
import os
import random

import pygame

from objects.slide_viewer import SlideViewer
from scenes.book_scene import BookScene
from scenes.difficulty_menu_scene import DiffMenuScene
from scenes.extra_explore_scene import ExtraExploreScene
from scenes.extra_menu_scene import ExtraMenuScene
from scenes.extra_practice_scene import ExtraPracticeScene
from scenes.game_scene import GameScene
from scenes.home_scene import HomeScene
from scenes.loading_scene import LoadingScene
from scenes.message_scene import MessageScene
from scenes.password_scene import PasswordScene
from scenes.production_intro_scene import ProductionIntroScene
from scenes.production_result_scene import ProductionResultScene
from scenes.production_scene import EXAM_CASE_COUNT, ProductionScene
from scenes.ranking_scene import RankingScene
from scenes.ranking_submit_scene import RankingSubmitScene
from setting import STAGES
from systems.game_generator import generate_game
from systems.generate_extra_map import generate_extra_map
from systems.ranking_api import make_details
from systems.score import count_streak
from systems.resource import resource_path

# =========================
# 設定
# =========================

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

FPS = 60

BGM_VOLUME = 0.3

# パスワード画面でこの文字列を入力するとエクストラモードが始まる
EXTRA_PASSWORD = "NOTDONE"

# エクストラの練習問題の世界の名前（data/practice/world{n}.csv と対応）
EXTRA_WORLD_NAMES = {
    1: "ノーマルム",
    2: "インフェクタ",
    3: "コイロサイト諸島",
    4: "シンジオン砦",
    5: "スコーマ",
}

# エクストラの練習問題の最後の世界
LAST_PRACTICE_WORLD = len(EXTRA_WORLD_NAMES)

# 本番の出題数（症例は毎回ランダムに選ぶので重複することがある）
PRODUCTION_QUESTION_COUNT = 5

# エクストラモードの細胞画像の種類と枚数
EXTRA_CELL_KINDS = {
    "NILM_norm": 9,
    "NILM_abnorm": 9,
    "LSIL": 6,
    "HSIL": 8,
    "SCC": 9,
}

# 本番問題に登場するコインの金額（images/coins/coin_{金額}.png）
# 数と大きさは分布表（data/exam/case*.csv）の coin_{金額} の行で決める
COIN_VALUES = [10, 50, 100, 500]

# =========================
# シーン管理
# =========================

SCENE_HOME = 0
SCENE_DIFFMENU = 1
SCENE_GAME = 2
SCENE_BOOK = 3
SCENE_LOADING = 4
SCENE_PASSWORD = 5
SCENE_EXTRA_EXPLORE = 6
SCENE_EXTRA_PRACTICE = 7
SCENE_PRODUCTION = 8
SCENE_PRODUCTION_INTRO = 9
SCENE_PRODUCTION_RESULT = 10
SCENE_NORMAL_HELP = 11
SCENE_EXTRA_BOOK = 12
SCENE_EXTRA_MENU = 13
SCENE_RANKING_SUBMIT = 14
SCENE_RANKING = 15
SCENE_HOME_HELP = 16

# current_scene = SCENE_HOME
current_scene = SCENE_HOME

world_data = 1

# =========================
# 初期化
# =========================

pygame.mixer.pre_init(
    frequency=44100,
    size=-16,
    channels=2,
    buffer=2048
)

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Oruccha")

font = pygame.font.Font(resource_path("fonts/MPLUS1p-Bold.ttf"), 32)
font.set_bold(True)

clock = pygame.time.Clock()

# =========================
# 画像読み込み
# =========================

def load_image(path, alpha=True):
    image = pygame.image.load(resource_path(path))

    if alpha:
        return image.convert_alpha()

    return image.convert()


normal_images = [
    load_image(f"images/cells/normal_{i}.png")
    for i in range(1, 3)
]

abnormal_images = [
    load_image(f"images/cells/abnormal_{i}.png")
    for i in range(1, 7)
]

book_images = (
    [load_image(f"images/book/normal_{i}.jpg", alpha=False) for i in range(1, 3)] +
    [load_image(f"images/book/abnormal_{i}.jpg", alpha=False) for i in range(1, 7)]
)

extra_cell_images = {
    f"{kind}_{i}": load_image(f"images/extra_prac_cells/{kind}_{i}.png")
    for kind, count in EXTRA_CELL_KINDS.items()
    for i in range(1, count + 1)
}

# 本番用の細胞画像
exam_cell_images = {
    f"{kind}_{i}": load_image(f"images/extra_cells/{kind}_{i}.png")
    for kind, count in EXTRA_CELL_KINDS.items()
    for i in range(1, count + 1)
}


def load_coin_image(value):
    image = load_image(f"images/coins/coin_{value}.png")

    # 画像の周りの透明な余白を切り落とす（余白ごと正方形に縮めると楕円になるため）
    return image.subsurface(image.get_bounding_rect()).copy()


# コインも細胞と同じ仕組みで配置するので、本番用の画像に加える
exam_cell_images.update({
    f"coin_{value}": load_coin_image(value)
    for value in COIN_VALUES
})

home_background = load_image("images/background/home.png")
diffmenu_background = load_image("images/background/diffmenu.jpg", alpha=False)

# ランキング画面の背景
ranking_background = load_image("images/background/ranking_board.jpg", alpha=False)

# キーボードが描かれた背景（パスコード入力 / ランキング登録のニックネーム入力）
password_background = load_image("images/background/password_keyboard.jpg", alpha=False)
ranking_keyboard_background = load_image("images/background/ranking_keyboard.jpg", alpha=False)

# エクストラの選択画面（ボタンは背景画像に描かれている）
extra_menu_backgrounds = {
    "closed": load_image("images/background/extra_menu.jpg", alpha=False),
    "open": load_image("images/background/extra_menu_book.jpg", alpha=False),
}
extra_menu_ranking_button = load_image("images/background/ranking_button.png")

# ノーマルモードの遊び方のスライド
# buttons はスライド画像（1920x1080）に描かれているボタンの位置
normal_help_slides = SlideViewer([
    {
        "image": load_image("images/help/help_1.jpg", alpha=False),
        "buttons": {"next": (1535, 985, 360, 80)},
    },
    {
        "image": load_image("images/help/help_2.jpg", alpha=False),
        "buttons": {"prev": (25, 965, 370, 90), "next": (1525, 965, 375, 90)},
    },
    {
        "image": load_image("images/help/help_3.jpg", alpha=False),
        "buttons": {"prev": (20, 985, 205, 85), "close": (1690, 985, 210, 85)},
    },
])

# =========================
# BGM
# =========================

HOME_BGM = resource_path("sounds/BGM/home_bgm.ogg")
DIFFMENU_BGM = resource_path("sounds/BGM/diffmenu_bgm.ogg")
GAME_BGM = resource_path("sounds/BGM/normalgame_bgm.ogg")

# 曲ごとの音量の倍率（BGM_VOLUME に掛ける）。元の音源の音の大きさの違いをそろえる
# normalgame_bgm は他の曲より約3.5dB小さいので 1.5倍にする
BGM_VOLUME_SCALES = {
    GAME_BGM: 1.5,
}

current_bgm = None


def play_bgm(path):
    """BGM を切り替える（同じ曲が流れていれば何もしない）"""
    global current_bgm

    if current_bgm == path:
        return

    current_bgm = path

    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(min(1.0, BGM_VOLUME * BGM_VOLUME_SCALES.get(path, 1.0)))
    pygame.mixer.music.play(-1)


def stop_bgm():
    """BGM を止める（次の play_bgm で同じ曲でも最初から流れるようにする）"""
    global current_bgm

    current_bgm = None

    pygame.mixer.music.stop()

# =========================
# シーン初期化
# =========================

home_scene = HomeScene(font, WIDTH, HEIGHT, home_background)
diff_menu_scene = DiffMenuScene(font, WIDTH, HEIGHT, diffmenu_background)
book_scene = BookScene(font, WIDTH, HEIGHT, book_images)


def load_numbered_images(folder, prefix):
    """{folder}/{prefix}_1.jpg から順に、存在する画像を読み込む"""
    images = []

    while True:
        path = f"{folder}/{prefix}_{len(images) + 1}.jpg"

        if not os.path.exists(resource_path(path)):
            return images

        images.append(load_image(path, alpha=False))


def load_extra_book_images(world):
    """images/extra_book/world{n}/book_1.jpg から順に、存在するページを読み込む"""
    return load_numbered_images(f"images/extra_book/world{world}", "book")


# エクストラの図鑑（世界ごと。画像が1枚もない世界は図鑑なし）
extra_book_scenes = {}

for world in range(1, LAST_PRACTICE_WORLD + 1):
    extra_book_images = load_extra_book_images(world)

    if extra_book_images:
        extra_book_scenes[world] = BookScene(font, WIDTH, HEIGHT, extra_book_images)

# ホーム画面のヘルプ（images/home_help/help_1.jpg から順に置いたページを表示する）
home_help_images = load_numbered_images("images/home_help", "help")

if home_help_images:
    home_help_scene = BookScene(font, WIDTH, HEIGHT, home_help_images)
else:
    home_help_scene = MessageScene(font, WIDTH, HEIGHT, "ヘルプは準備中です")

loading_scene = LoadingScene(font)
password_scene = PasswordScene(font, WIDTH, HEIGHT, EXTRA_PASSWORD, password_background)
extra_menu_scene = ExtraMenuScene(
    font,
    WIDTH,
    HEIGHT,
    extra_menu_backgrounds,
    sorted(extra_book_scenes),
    extra_menu_ranking_button
)
production_intro_scene = ProductionIntroScene(font, WIDTH, HEIGHT, PRODUCTION_QUESTION_COUNT)


def create_game_scene(generated, stage, width):
    cells, grid, _, world_width, world_height = generated

    return GameScene(
        font,
        width,
        STAGES[stage]["abnormal_cells"],
        cells,
        grid,
        world_width,
        world_height
    )


def create_extra_explore_scene(generated, width):
    cells, grid, _, world_width, world_height, distribution = generated

    return ExtraExploreScene(
        font,
        width,
        cells,
        grid,
        world_width,
        world_height,
        distribution
    )


def create_production_generator(case_number):
    return generate_extra_map(
        world_data=case_number,
        cell_images=exam_cell_images,
        data_folder="exam",
        file_prefix="case"
    )


def create_production_scene(generated, case_number, question_number, score_before, streak_before, width):
    cells, grid, _, world_width, world_height, distribution = generated

    return ProductionScene(
        font,
        width,
        cells,
        grid,
        world_width,
        world_height,
        distribution,
        case_number,
        question_number,
        PRODUCTION_QUESTION_COUNT,
        score_before,
        streak_before
    )

# =========================
# メインループ
# =========================

async def main():
    global current_scene
    global world_data

    game_scene = None
    extra_explore_scene = None
    extra_practice_scene = None
    production_scene = None
    production_result_scene = None
    ranking_submit_scene = None
    ranking_scene = None

    current_stage = None

    # 本番で出題する症例番号のリストと、回答済みの結果
    production_cases = []
    production_results = []

    # ロード中のジェネレータと、ロード完了後に移るシーン
    generator = None
    loading_target = SCENE_GAME

    # 図鑑から戻る先のシーン
    book_return_scene = SCENE_DIFFMENU

    # エクストラの図鑑で表示する世界と、閉じた時に戻るシーン
    extra_book_world = 1
    extra_book_return_scene = SCENE_EXTRA_EXPLORE

    # ノーマルモードの遊び方を一度見たかどうか（起動中のみ記憶する）
    normal_help_seen = False

    # ランキングに前回送信した時の入力（起動中のみ記憶する）
    last_nickname = ""
    last_prefecture = None

    # ランキング画面を閉じた時に戻るシーン
    ranking_return_scene = SCENE_EXTRA_MENU

    running = True

    play_bgm(HOME_BGM)

    while running:
        width, height = screen.get_size()

        clock.tick(FPS)

        # -------------------------
        # レイアウト更新
        # -------------------------

        if current_scene == SCENE_DIFFMENU:
            diff_menu_scene.update_layout(width, height)

        elif current_scene == SCENE_GAME:
            game_scene.update_layout(width, height)

        elif current_scene == SCENE_EXTRA_EXPLORE:
            extra_explore_scene.update_layout()

        elif current_scene == SCENE_PRODUCTION:
            production_scene.update_layout(width, height)

        # -------------------------
        # イベント処理
        # -------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_scene == SCENE_HOME:
                result = home_scene.handle_event(event)

                if result == "normal":
                    loading_target = SCENE_GAME

                    if normal_help_seen:
                        current_scene = SCENE_DIFFMENU
                        play_bgm(DIFFMENU_BGM)

                    else:
                        # 初回は遊び方を見せてから難易度選択へ
                        normal_help_slides.open()
                        current_scene = SCENE_NORMAL_HELP

                elif result == "help":
                    if isinstance(home_help_scene, BookScene):
                        home_help_scene.current_page = 0

                    current_scene = SCENE_HOME_HELP

                elif result == "ranking":
                    ranking_scene = RankingScene(font, width, height, background=ranking_background)
                    ranking_return_scene = SCENE_HOME
                    current_scene = SCENE_RANKING

                elif result == "extra":
                    current_scene = SCENE_PASSWORD

            elif current_scene == SCENE_DIFFMENU:
                result = diff_menu_scene.handle_event(event)
                action = result["action"] if result else None

                if action == "start":
                    stop_bgm()

                    current_stage = result["stage"]
                    config = STAGES[current_stage]

                    generator = generate_game(
                        config["normal_cells"],
                        config["abnormal_cells"],
                        normal_images,
                        abnormal_images
                    )

                    current_scene = SCENE_LOADING

                elif action == "book":
                    book_return_scene = SCENE_DIFFMENU
                    current_scene = SCENE_BOOK

                elif action == "help":
                    normal_help_slides.open()
                    current_scene = SCENE_NORMAL_HELP

                elif action == "home":
                    current_scene = SCENE_HOME
                    play_bgm(HOME_BGM)

            elif current_scene == SCENE_GAME:
                result = game_scene.handle_event(event, width, height)

                if result == "menu":
                    game_scene = None
                    gc.collect()

                    current_scene = SCENE_DIFFMENU
                    play_bgm(DIFFMENU_BGM)

                elif result == "book":
                    book_return_scene = SCENE_GAME
                    current_scene = SCENE_BOOK

            elif current_scene == SCENE_BOOK:
                result = book_scene.handle_event(event)

                if result == "menu":
                    current_scene = book_return_scene

                    if current_scene == SCENE_DIFFMENU:
                        play_bgm(DIFFMENU_BGM)

                    elif current_scene == SCENE_GAME:
                        play_bgm(GAME_BGM)

            elif current_scene == SCENE_EXTRA_BOOK:
                result = extra_book_scenes[extra_book_world].handle_event(event)

                if result == "menu":
                    current_scene = extra_book_return_scene

            elif current_scene == SCENE_PASSWORD:
                result = password_scene.handle_event(event)

                if result == EXTRA_PASSWORD:
                    extra_menu_scene.notice = ""
                    current_scene = SCENE_EXTRA_MENU

                elif result == "home":
                    current_scene = SCENE_HOME
                    play_bgm(HOME_BGM)

            elif current_scene == SCENE_EXTRA_MENU:
                result = extra_menu_scene.handle_event(event)
                action = result["action"] if result else None

                if action == "practice":
                    world_data = result["world"]

                    stop_bgm()

                    generator = generate_extra_map(
                        world_data=world_data,
                        cell_images=extra_cell_images
                    )

                    loading_target = SCENE_EXTRA_EXPLORE
                    current_scene = SCENE_LOADING

                elif action == "production":
                    current_scene = SCENE_PRODUCTION_INTRO

                elif action == "book":
                    extra_book_world = result["world"]
                    extra_book_return_scene = SCENE_EXTRA_MENU
                    current_scene = SCENE_EXTRA_BOOK

                elif action == "ranking":
                    ranking_scene = RankingScene(font, width, height, background=ranking_background)
                    ranking_return_scene = SCENE_EXTRA_MENU
                    current_scene = SCENE_RANKING

                elif action == "home":
                    current_scene = SCENE_HOME
                    play_bgm(HOME_BGM)

            elif current_scene == SCENE_EXTRA_EXPLORE:
                result = extra_explore_scene.handle_event(event, width, height)

                if result == "menu":
                    extra_explore_scene = None
                    gc.collect()

                    extra_menu_scene.notice = ""
                    current_scene = SCENE_EXTRA_MENU
                    play_bgm(HOME_BGM)

                elif result == "book":
                    # 図鑑がまだ用意されていない世界では何もしない
                    if world_data in extra_book_scenes:
                        extra_book_world = world_data
                        extra_book_return_scene = SCENE_EXTRA_EXPLORE
                        current_scene = SCENE_EXTRA_BOOK

                elif result == "practice":
                    current_scene = SCENE_EXTRA_PRACTICE

                    extra_practice_scene = ExtraPracticeScene(
                        font,
                        width,
                        height,
                        world_data,
                        extra_explore_scene.get_found_cells()
                    )

            elif current_scene == SCENE_EXTRA_PRACTICE:
                result = extra_practice_scene.handle_event(event)

                if result == "next_world" and world_data >= LAST_PRACTICE_WORLD:
                    # 最後の世界の練習問題をクリアしたら選択画面へ
                    extra_practice_scene = None
                    gc.collect()

                    extra_menu_scene.notice = "すべての練習問題をクリアしました！"
                    current_scene = SCENE_EXTRA_MENU
                    play_bgm(HOME_BGM)

                elif result in ("next_world", "retry"):
                    if result == "next_world":
                        world_data += 1

                    extra_practice_scene = None
                    gc.collect()

                    stop_bgm()

                    generator = generate_extra_map(
                        world_data=world_data,
                        cell_images=extra_cell_images
                    )

                    current_scene = SCENE_LOADING

            elif current_scene == SCENE_PRODUCTION_INTRO:
                result = production_intro_scene.handle_event(event)

                if result == "start":
                    production_cases = random.choices(
                        range(1, EXAM_CASE_COUNT + 1),
                        k=PRODUCTION_QUESTION_COUNT
                    )
                    production_results = []

                    generator = create_production_generator(production_cases[0])
                    loading_target = SCENE_PRODUCTION
                    current_scene = SCENE_LOADING

                elif result == "back":
                    current_scene = SCENE_EXTRA_MENU

            elif current_scene == SCENE_PRODUCTION:
                result = production_scene.handle_event(event, width, height)

                if result == "next":
                    production_results.append(production_scene.get_result())

                    production_scene = None
                    gc.collect()

                    if len(production_results) < len(production_cases):
                        generator = create_production_generator(
                            production_cases[len(production_results)]
                        )
                        current_scene = SCENE_LOADING

                    else:
                        production_result_scene = ProductionResultScene(
                            font,
                            width,
                            height,
                            production_results
                        )
                        current_scene = SCENE_PRODUCTION_RESULT

            elif current_scene == SCENE_PRODUCTION_RESULT:
                result = production_result_scene.handle_event(event)

                if result == "submit":
                    ranking_submit_scene = RankingSubmitScene(
                        font,
                        width,
                        height,
                        production_result_scene.total_score,
                        make_details(production_results),
                        last_nickname,
                        last_prefecture,
                        keyboard_background=ranking_keyboard_background
                    )
                    current_scene = SCENE_RANKING_SUBMIT

                elif result == "menu":
                    production_result_scene = None

                    extra_menu_scene.notice = ""
                    current_scene = SCENE_EXTRA_MENU
                    play_bgm(HOME_BGM)

            elif current_scene == SCENE_RANKING_SUBMIT:
                result = ranking_submit_scene.handle_event(event)

                if result in ("back", "ranking"):
                    if ranking_submit_scene.succeeded:
                        # 同じ結果は二度送れないようにし、入力は次回のために覚えておく
                        production_result_scene.mark_submitted()

                        last_nickname = ranking_submit_scene.textbox.text
                        last_prefecture = ranking_submit_scene.prefecture

                    if result == "ranking":
                        submitted = ranking_submit_scene.result

                        ranking_scene = RankingScene(
                            font,
                            width,
                            height,
                            highlight_id=submitted["id"],
                            highlight_rank=submitted["rank"],
                            background=ranking_background
                        )
                        ranking_return_scene = SCENE_PRODUCTION_RESULT
                        current_scene = SCENE_RANKING

                    else:
                        current_scene = SCENE_PRODUCTION_RESULT

                    ranking_submit_scene = None

            elif current_scene == SCENE_RANKING:
                result = ranking_scene.handle_event(event)

                if result == "back":
                    ranking_scene = None
                    current_scene = ranking_return_scene

            elif current_scene == SCENE_HOME_HELP:
                result = home_help_scene.handle_event(event)

                # 図鑑形式（BookScene）は "menu"、準備中の表示（MessageScene）は "back" を返す
                if result in ("menu", "back"):
                    current_scene = SCENE_HOME

            elif current_scene == SCENE_NORMAL_HELP:
                result = normal_help_slides.handle_event(event, width, height)

                if result == "close":
                    normal_help_seen = True

                    current_scene = SCENE_DIFFMENU
                    play_bgm(DIFFMENU_BGM)

        # -------------------------
        # 更新・描画
        # -------------------------

        if current_scene == SCENE_HOME:
            home_scene.draw(screen)

        elif current_scene == SCENE_DIFFMENU:
            diff_menu_scene.draw(screen)

        elif current_scene == SCENE_GAME:
            game_scene.update()
            game_scene.draw(screen)

        elif current_scene == SCENE_BOOK:
            book_scene.draw(screen)

        elif current_scene == SCENE_EXTRA_BOOK:
            extra_book_scenes[extra_book_world].draw(screen)

        elif current_scene == SCENE_LOADING:
            loading_scene.draw(screen)

            # 1フレームごとに生成を少しずつ進める
            try:
                progress = next(generator)
                loading_scene.set_progress(progress)

            except StopIteration as finished:
                if loading_target == SCENE_GAME:
                    game_scene = create_game_scene(finished.value, current_stage, width)
                    current_scene = SCENE_GAME

                elif loading_target == SCENE_EXTRA_EXPLORE:
                    extra_explore_scene = create_extra_explore_scene(finished.value, width)
                    current_scene = SCENE_EXTRA_EXPLORE

                elif loading_target == SCENE_PRODUCTION:
                    question_number = len(production_results) + 1

                    production_scene = create_production_scene(
                        finished.value,
                        production_cases[question_number - 1],
                        question_number,
                        sum(r["score"] for r in production_results),
                        count_streak(production_results),
                        width
                    )
                    current_scene = SCENE_PRODUCTION

                play_bgm(GAME_BGM)

        elif current_scene == SCENE_PASSWORD:
            password_scene.draw(screen)

        elif current_scene == SCENE_EXTRA_EXPLORE:
            extra_explore_scene.update()
            extra_explore_scene.draw(screen, extra_cell_images)

        elif current_scene == SCENE_EXTRA_PRACTICE:
            extra_practice_scene.update()
            extra_practice_scene.draw(screen)

        elif current_scene == SCENE_EXTRA_MENU:
            extra_menu_scene.draw(screen)

        elif current_scene == SCENE_PRODUCTION_INTRO:
            production_intro_scene.draw(screen)

        elif current_scene == SCENE_PRODUCTION:
            production_scene.update()
            production_scene.draw(screen)

        elif current_scene == SCENE_PRODUCTION_RESULT:
            production_result_scene.draw(screen)

        elif current_scene == SCENE_RANKING_SUBMIT:
            ranking_submit_scene.draw(screen)

        elif current_scene == SCENE_RANKING:
            ranking_scene.draw(screen)

        elif current_scene == SCENE_NORMAL_HELP:
            normal_help_slides.draw(screen)

        elif current_scene == SCENE_HOME_HELP:
            home_help_scene.draw(screen)

        pygame.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())
