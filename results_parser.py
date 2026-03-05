import json
from pathlib import Path

target_dir = Path("EN to RU/qwen3_8b/Crime and Punishment/Chapter_2/temp_1.2/ratings")

def get_average(property):
    """
    Parameters:
        property: a string marking the property that the average off will be found. Valid options: Meaning, Grammar, Fluency, Lexical Choice, Completeness.

    Returns:
        Average score as a string
    """
    average_score = 0
    counter = 0

    for file in target_dir.glob("*.txt"):
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        if "rating" not in data:
            print(f"Missing 'rating' in: {file.name}")
            print(data)
            print("------")
            continue

        average_score += int(data["rating"][property])
        counter += 1

    if counter > 0:
        return (average_score / counter)
    else:
        print("No valid files found.")


print("Meaning: ", get_average("Meaning"))
print("Grammar: ", get_average("Grammar"))
print("Fluency: ", get_average("Fluency"))
print("Lexical Choice: ", get_average("Lexical Choice"))
print("Completeness: ", get_average("Completeness"))