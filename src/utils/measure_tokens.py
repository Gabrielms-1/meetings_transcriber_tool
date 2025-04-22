import json
from transformers import AutoTokenizer

with open("data/transcripts/2025-04-08 09-02-19_transcript_backup.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dialogue = "\n".join(
    f"{list(u.keys())[0]}: {list(u.values())[0]}" for u in data
)

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct-AWQ")

encoding = tokenizer(dialogue, return_length=True, truncation=False)
total_tokens = len(encoding["input_ids"])
print(f"Tokens totais: {total_tokens}")
