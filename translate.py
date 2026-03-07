from pathlib import Path
import requests
import json

url = "http://localhost:11434/api/generate"
source_text_dir = Path("text_parts")
translations_dir = Path("translations")
instructions_file = Path("translation_instructions.txt")    

def ask_llm(prompt, temperature=2.0):
    payload = {
        "model": "llama3.1:8b",
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

instructions = instructions_file.read_text(encoding="utf-8") 

for file in source_text_dir.glob("*.txt"):
    content = file.read_text(encoding='utf-8')
    answer = ask_llm(instructions + content)
    
    new_filepath = translations_dir / (file.stem + "_translation.txt")

    create_file_with_text(new_filepath, answer)
    print(answer)
