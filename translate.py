from pathlib import Path
import requests

url = "http://localhost:11434/api/generate"

source_text_dir = Path("text_parts")
translations_dir = Path("translations")
instructions_file = Path("translation_instructions.txt")


def ask_llm(prompt, model, temperature):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "thinking": False,
            "temperature": temperature
        }
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json()["response"]


def create_file_with_text(file_path, content):
    translations_dir.mkdir(exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        f.write(content)


def translate(model: str, temperature: float, generations: int = 1):
    instructions = instructions_file.read_text(encoding="utf-8")
    folder_name = ""

    for file in source_text_dir.glob("*.txt"):
        content = file.read_text(encoding="utf-8")

        folder_name = file.stem
        Path(translations_dir / folder_name).mkdir(parents=True, exist_ok=True)

        if generations > 1:
            answers = []
            for _ in range(generations):
                answer = ask_llm(instructions + content, model, temperature)
                answers.append(answer)
            for i, ans in enumerate(answers):
                new_filepath = translations_dir / folder_name / (file.stem + "_translation.txt")
                create_file_with_text(new_filepath.with_name(f"{new_filepath.stem}_{i}{new_filepath.suffix}"), ans)
        else:
            new_filepath = translations_dir / (file.stem + "_translation.txt")
            answer = ask_llm(instructions + content, model, temperature)
            create_file_with_text(new_filepath, answer)

        # print(f"Translated {file.name}")

    if generations > 1:
        return folder_name