import json
from pathlib import Path

target_dir = Path("EN to RU/YandexGPT-5-Lite-8B-instruct-GGUF/Crime and Punishment/Chapter 2/temp_2.0/ratings")

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


print("Meaning: ", round(get_average("Meaning"), 4))
print("Grammar: ", round(get_average("Grammar"), 4))
print("Fluency: ", round(get_average("Fluency"), 4))
print("Lexical Choice: ", round(get_average("Lexical Choice"), 4))
print("Completeness: ", round(get_average("Completeness"), 4))