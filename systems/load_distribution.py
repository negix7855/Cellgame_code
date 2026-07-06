import csv

def load_distribution(path):

    cells = []

    with open(path, encoding="utf-8-sig") as f:

        reader = csv.DictReader(f)

        for row in reader:

            cells.append({
                "cell_name": row["cell_name"],
                "count": int(row["count"]),
                "width": int(row["width"]),
                "height": int(row["height"]),
                "display_name": row["display_name"]
            })

    return cells