import json
from pathlib import Path
import math

target_dir = Path("Embedding_test/EN to RU/llama3.1_8b/RusLTC_EN_1_94/ratings")

def get_std(property):
    values = []

    for file in target_dir.glob("*.txt"):
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        if "rating" not in data:
            continue

        values.append(int(data["rating"][property]))

    if len(values) < 2:
        return None

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)  # sample std
    return math.sqrt(variance)


properties = ["Meaning", "Grammar", "Fluency", "Lexical Choice", "Completeness"]

for prop in properties:
    std = get_std(prop)
    if std is not None:
        print(round(std, 4))