from pathlib import Path
from ollama import Client

client = Client()

source_text_dir = Path("text_parts")
translations_dir = Path("translations")
ratings_dir = Path("ratings")
instructions_file = Path("rating_instructions.txt")


def ask_cloud_llm(prompt, model):
    messages = [
        {'role': 'user', 'content': prompt},
    ]

    response = client.chat(model, messages=messages, stream=False)
    return response['message']['content']


def create_file_with_text(file_path, content):
    ratings_dir.mkdir(exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        f.write(content)


def rate(model: str = "gpt-oss:120b-cloud"):
    ratings_dir.mkdir(exist_ok=True)
    instructions = instructions_file.read_text(encoding="utf-8")

    for translated_file_path in translations_dir.glob("*.txt"):
        if translated_file_path.is_file():
            translated_text = translated_file_path.read_text(encoding="utf-8")

            # Compute original file name by removing _translation* suffix
            stem = translated_file_path.stem
            if "_translation" in stem:
                original_stem = stem.split("_translation")[0]  # "0_translation_4_centermost" -> "0"
            else:
                original_stem = stem

            source_file_path = source_text_dir / (original_stem + ".txt")
            if source_file_path.exists():
                original_text = source_file_path.read_text(encoding="utf-8")
            else:
                original_text = "[Original text not found]"

            print("Asking the following: \n" + instructions
                + "\nHere is the original text:\n" + original_text
                + "\nHere is the translated text:\n" + translated_text)
            
            # Ask the LLM for a rating
            rating = ask_cloud_llm(
                instructions
                + "\nHere is the original text:\n" + original_text
                + "\nHere is the translated text:\n" + translated_text,
                model
            )

            # Save rating file
            new_filepath = ratings_dir / (stem + "_rating.txt")
            create_file_with_text(new_filepath, rating)

            print(f"Rated {translated_file_path.name}")