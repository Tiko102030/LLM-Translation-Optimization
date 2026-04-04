import json
from pathlib import Path

# target_dir = Path("RU to EN/YandexGPT-5-Lite-8B-instruct-GGUF/Crime and Punishment/Chapter_2/temp_2.0/ratings")

target_dirs = [
    "Embedding_test/RU to EN/YandexGPT-5-Lite-8B-instruct-GGUF/RusLTC_RU_1_94_1/ratings",


]

KEY_MAP = {
    "meaning": "Meaning",
    "grammar": "Grammar",
    "fluency": "Fluency",
    "lexical choice": "Lexical Choice",
    "lexical_choice": "Lexical Choice",
    "completeness": "Completeness",
}

EXPECTED_KEYS = {
    "Meaning",  
    "Grammar",
    "Fluency",
    "Lexical Choice",
    "Completeness",
}
for target_dir in target_dirs:
    target_dir = Path(target_dir)
    for file in target_dir.glob("*.txt"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)


            rating_source = None

            for key in data.keys():
                if key.lower() in ["rating", "ratings"]:
                    rating_source = data[key]
                    break

            # If no wrapper found, assume top-level is rating
            if rating_source is None:
                rating_source = data

            if not isinstance(rating_source, dict):
                print(f"Skipped (invalid structure): {file.name}")
                continue


            fixed_rating = {}

            for key, value in rating_source.items():
                normalized_key = KEY_MAP.get(key.lower())
                if normalized_key:
                    fixed_rating[normalized_key] = value


            missing = EXPECTED_KEYS - set(fixed_rating.keys())
            if missing:
                print(f"Warning: {file.name} missing keys: {missing}")

            data_fixed = {"rating": fixed_rating}

            with open(file, "w", encoding="utf-8") as f:
                json.dump(data_fixed, f, indent=2, ensure_ascii=False)

            print(f"Fixed: {file.name}")

        except Exception as e:
            print(f"Error in {file.name}: {e}")