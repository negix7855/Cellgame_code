# =========================
# 本番問題（スコアアタック）のスコア計算
#
# 1問のスコア
#   基礎スコア = その問題で拾ったコインの合計（10円 = 10点 ... 500円 = 500点）
#   正解       = 基礎スコア × 2 × 連続正解の倍率
#   不正解     = 基礎スコア × 0.5
#   時間切れ   = 0点
#
# 最終スコア = 各問題のスコアの合計
#            + 全問正解ボーナス（5000点）
#            + 残り時間の合計（秒） × 150点
#
# サーバー側（server/supabase_ranking.sql の submit_score）も同じ計算をしているので、
# ここを変えたら SQL も合わせて変えること
# =========================

ALL_CORRECT_BONUS = 5000
TIME_BONUS_PER_SECOND = 150

# 連続正解数 → 倍率（小数の誤差が出ないよう 10倍した整数で持つ。11 = 1.1倍）
STREAK_MULTIPLIERS = {
    1: 10,
    2: 11,
    3: 12,
    4: 13,
    5: 15,
}


def coin_value(cell_name):
    """"coin_100" → 100。コインでなければ None"""
    if not cell_name or not cell_name.startswith("coin_"):
        return None

    return int(cell_name.split("_", 1)[1])


def streak_multiplier(streak):
    """連続正解数に応じた倍率（10倍した整数）"""
    return STREAK_MULTIPLIERS.get(streak, max(STREAK_MULTIPLIERS.values()))


def format_multiplier(multiplier):
    """11 → "1.1" """
    return f"{multiplier // 10}.{multiplier % 10}"


def question_score(coin_score, is_correct, time_up, streak):
    """1問のスコア。streak はこの問題を含めた連続正解数（正解の時だけ使う）

    コインは10点単位なので、どの倍率でも割り切れて整数になる
    """
    if time_up:
        return 0

    if is_correct:
        return coin_score * 2 * streak_multiplier(streak) // 10

    return coin_score // 2


def count_streak(results):
    """直前まで何問連続で正解しているか"""
    streak = 0

    for r in reversed(results):
        if not r["is_correct"]:
            break
        streak += 1

    return streak


def total_score(results):
    """5問の結果から最終スコアと内訳を計算する"""
    question_total = sum(r["score"] for r in results)
    all_correct = bool(results) and all(r["is_correct"] for r in results)
    remaining_total = sum(r["remaining_seconds"] for r in results)

    all_correct_bonus = ALL_CORRECT_BONUS if all_correct else 0
    time_bonus = remaining_total * TIME_BONUS_PER_SECOND

    return {
        "question_total": question_total,
        "all_correct_bonus": all_correct_bonus,
        "remaining_total": remaining_total,
        "time_bonus": time_bonus,
        "total": question_total + all_correct_bonus + time_bonus,
    }
