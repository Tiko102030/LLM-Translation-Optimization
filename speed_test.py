import requests
import time
import json
import statistics
from pathlib import Path

# -------------------------
# CONFIG
# -------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "yandex/YandexGPT-5-Lite-8B-instruct-GGUF:latest"
# "llama3.1:8b", "qwen3:8b", "yandex/YandexGPT-5-Lite-8B-instruct-GGUF:latest"

INPUT_FOLDER = "input"
INSTRUCTIONS_FILE = "translation_instructions.txt"

SOURCE_LANG = "Russian"
TARGET_LANG = "English"

# -------------------------
# LOAD INSTRUCTIONS
# -------------------------
def load_instructions(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found")
    return Path(path).read_text(encoding="utf-8").strip()

INSTRUCTIONS = load_instructions(INSTRUCTIONS_FILE)

# -------------------------
# LOAD INPUT TEXTS
# -------------------------
def load_input_texts(folder):
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(f"{folder} folder not found")

    texts = []
    for file in sorted(folder_path.glob("*.txt")):
        content = file.read_text(encoding="utf-8").strip()
        if content:
            texts.append({
                "filename": file.name,
                "text": content
            })
    return texts

INPUT_TEXTS = load_input_texts(INPUT_FOLDER)

# -------------------------
# TRANSLATION FUNCTION
# -------------------------
def translate_stream(text):
    prompt = f"""
{INSTRUCTIONS}

Translate the following text from {SOURCE_LANG} to {TARGET_LANG}:

{text}
""".strip()

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.1
        }
    }

    start_time = time.time()
    first_token_time = None
    full_output = ""

    with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
        if response.status_code != 200:
            raise Exception(f"Request failed: {response.text}")

        for line in response.iter_lines():
            if not line:
                continue

            chunk = json.loads(line.decode("utf-8"))

            if first_token_time is None:
                first_token_time = time.time()

            token = chunk.get("response", "")
            full_output += token

            if chunk.get("done", False):
                end_time = time.time()

                eval_count = chunk.get("eval_count", 0)
                eval_duration = chunk.get("eval_duration", 0) / 1e9

                prompt_eval_count = chunk.get("prompt_eval_count", 0)
                prompt_eval_duration = chunk.get("prompt_eval_duration", 0) / 1e9

                break

    ttft = (first_token_time - start_time) if first_token_time else None
    ttlt = end_time - start_time
    tokens_per_sec = eval_count / eval_duration if eval_duration > 0 else 0

    return {
        "output": full_output.strip(),
        "ttft": ttft,
        "ttlt": ttlt,
        "tokens_generated": eval_count,
        "tokens_per_sec": tokens_per_sec,
        "prompt_tokens": prompt_eval_count,
        "prompt_time": prompt_eval_duration
    }

# -------------------------
# MAIN LOOP
# -------------------------
results = []

for i, item in enumerate(INPUT_TEXTS):
    print(f"\n--- Processing {item['filename']} ({i+1}/{len(INPUT_TEXTS)}) ---")

    res = translate_stream(item["text"])

    result_entry = {
        "filename": item["filename"],
        "input": item["text"],
        **res
    }

    results.append(result_entry)

    print(f"Output: {res['output']}")
    print(f"TTFT: {res['ttft']:.3f}s")
    print(f"TTLT: {res['ttlt']:.3f}s")
    print(f"Tokens Generated: {res['tokens_generated']}")
    print(f"Tokens/sec: {res['tokens_per_sec']:.2f}")
    print(f"Prompt Tokens: {res['prompt_tokens']}")
    print(f"Prompt Time: {res['prompt_time']:.3f}s")

# -------------------------
# AGGREGATE STATS
# -------------------------
ttfts = [r["ttft"] for r in results if r["ttft"] is not None]
ttlts = [r["ttlt"] for r in results]
tps = [r["tokens_per_sec"] for r in results if r["tokens_per_sec"] > 0]

print("\n=========================")
print("AGGREGATE STATISTICS")
print("=========================")

if ttfts:
    print(f"TTFT Mean: {statistics.mean(ttfts):.3f}s")
    print(f"TTFT Min: {min(ttfts):.3f}s")
    print(f"TTFT Max: {max(ttfts):.3f}s")

print(f"TTLT Mean: {statistics.mean(ttlts):.3f}s")
print(f"TTLT Min: {min(ttlts):.3f}s")
print(f"TTLT Max: {max(ttlts):.3f}s")

if tps:
    print(f"Tokens/sec Mean: {statistics.mean(tps):.2f}")
    print(f"Tokens/sec Min: {min(tps):.2f}")
    print(f"Tokens/sec Max: {max(tps):.2f}")