import csv


def load_distribution(path):
    """細胞の分布 CSV を読み込み、1行ごとの辞書のリストを返す"""
    distribution = []

    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            distribution.append({
                "cell_name": row["cell_name"],
                "count": int(row["count"]),
                "width": int(row["width"]),
                "height": int(row["height"]),
                "display_name": row["display_name"]
            })

    return distribution
