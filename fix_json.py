import json
from pathlib import Path

# target_dir = Path("ratings")
target_dir = Path("EN to RU/YandexGPT-5-Lite-8B-instruct-GGUF/Crime and Punishment/Chapter 2/temp_2.0/ratings")

# Canonical key mapping
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

for file in target_dir.glob("*.txt"):
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ---------------------------------------------------
        # Step 1: Detect rating block (case-insensitive)
        # ---------------------------------------------------
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

        # ---------------------------------------------------
        # Step 2: Normalize metric keys
        # ---------------------------------------------------
        fixed_rating = {}

        for key, value in rating_source.items():
            normalized_key = KEY_MAP.get(key.lower())
            if normalized_key:
                fixed_rating[normalized_key] = value

        # ---------------------------------------------------
        # Step 3: Validate required metrics exist
        # ---------------------------------------------------
        missing = EXPECTED_KEYS - set(fixed_rating.keys())
        if missing:
            print(f"Warning: {file.name} missing keys: {missing}")

        # ---------------------------------------------------
        # Step 4: Overwrite with canonical structure
        # ---------------------------------------------------
        data_fixed = {"rating": fixed_rating}

        with open(file, "w", encoding="utf-8") as f:
            json.dump(data_fixed, f, indent=2, ensure_ascii=False)

        print(f"Fixed: {file.name}")

    except Exception as e:
        print(f"Error in {file.name}: {e}")