from pathlib import Path
import shutil
from tqdm import tqdm
from datetime import datetime
import text_parser
import translate
import check_translations

# -------------------------
# Configuration
# -------------------------
input_language = "EN"
input_texts = ["RusLTC_EN_1_94.txt"]
# text_source = "Wikipedia/Neural Networks" 
#  0.1, 0.3, 0.5, 0.6, 0.7, 0.9, 1.1, 1.2, 1.5, 2.0
# "yandex/YandexGPT-5-Lite-8B-instruct-GGUF:latest"
models = ["yandex/YandexGPT-5-Lite-8B-instruct-GGUF:latest"] # Done: llama3.1:8b, qwen3:8b, 
temps = [0.1, 0.3, 0.5, 0.6, 0.7, 0.9, 1.1, 1.2, 1.5, 2.0]

log_file = Path("pipeline_progress.log")
completed_work = []

# -------------------------
# Helper function for logging
# -------------------------
def log(msg: str):
    timestamped = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(timestamped)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(timestamped + "\n")

# Clear previous log
with log_file.open("w", encoding="utf-8") as f:
    f.write("Pipeline started at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

# Compute total runs
total_runs = len(input_texts) * len(models) * len(temps)

# -------------------------
# Main pipeline
# -------------------------
with tqdm(total=total_runs, desc="Total pipeline progress", position=0) as pbar_total:
    for input_text in input_texts:
        text_source = input_text.replace(".txt", "")
        # Parse once per text
        log(f"Parsing {input_text} into text_parts...")
        text_parser.parse(input_text)

        for model in models:
            for temp in temps:
                # Clean working folders before each run
                for folder in ["translations", "ratings"]:
                    path = Path(folder)
                    if path.exists():
                        shutil.rmtree(path)

                # -------------------------
                # Nested progress bar for this run
                # -------------------------
                with tqdm(total=2, desc=f"Run {input_text} | {model} | temp {temp}", position=1, leave=False) as pbar_run:

                    # Step 1: Translate
                    log(f"Translating with model {model} at temp {temp}...")
                    translate.translate(model=model, temperature=temp)
                    pbar_run.update(1)

                    # Step 2: Rate translations
                    log("Rating translations...")
                    check_translations.rate()
                    pbar_run.update(1)

                # -------------------------
                # Organize outputs
                # -------------------------
                if input_language == "RU":
                    if model == "qwen3:8b":
                        model_dir = "qwen3_8b"
                    elif model == "llama3.1:8b":
                        model_dir = "llama3.1_8b"
                    elif model == "yandex/YandexGPT-5-Lite-8B-instruct-GGUF:latest":
                        model_dir = "YandexGPT-5-Lite-8B-instruct-GGUF"
                    else:
                        raise ValueError("Incorrect model assigned")

                    base_path = Path(f"RU to EN/{model_dir}/{text_source}/temp_{temp}")
                    base_path.mkdir(parents=True, exist_ok=True)

                    dest_translations = base_path / "translations"
                    dest_ratings = base_path / "ratings"
                    dest_text_parts = base_path / "text_parts"

                    if dest_translations.exists():
                        shutil.rmtree(dest_translations)
                    if dest_ratings.exists():
                        shutil.rmtree(dest_ratings)
                    if dest_text_parts.exists():
                        shutil.rmtree(dest_text_parts)

                    shutil.move("translations", dest_translations)
                    shutil.move("ratings", dest_ratings)
                    shutil.copytree("text_parts", dest_text_parts)


                if input_language == "EN":
                    if model == "qwen3:8b":
                        model_dir = "qwen3_8b"
                    elif model == "llama3.1:8b":
                        model_dir = "llama3.1_8b"
                    elif model == "yandex/YandexGPT-5-Lite-8B-instruct-GGUF:latest":
                        model_dir = "YandexGPT-5-Lite-8B-instruct-GGUF"
                    else:
                        raise ValueError("Incorrect model assigned")

                    base_path = Path(f"EN to RU/{model_dir}/{text_source}/temp_{temp}")
                    base_path.mkdir(parents=True, exist_ok=True)

                    dest_translations = base_path / "translations"
                    dest_ratings = base_path / "ratings"
                    dest_text_parts = base_path / "text_parts"

                    if dest_translations.exists():
                        shutil.rmtree(dest_translations)
                    if dest_ratings.exists():
                        shutil.rmtree(dest_ratings)
                    if dest_text_parts.exists():
                        shutil.rmtree(dest_text_parts)

                    shutil.move("translations", dest_translations)
                    shutil.move("ratings", dest_ratings)
                    shutil.copytree("text_parts", dest_text_parts)

                # -------------------------
                # Update total progress
                # -------------------------
                pbar_total.update(1)

                # Record completed work
                completed_work.append(f"{text_source} | {model} | temp {temp} completed")
                log(f"Completed run: {text_source} | {model} | temp {temp}")


# -------------------------
# Final summary
# -------------------------
log("\nAll runs completed! Summary of completed work:")
for entry in completed_work:
    print(entry)

with log_file.open("a", encoding="utf-8") as f:
    f.write("Pipeline finished at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")