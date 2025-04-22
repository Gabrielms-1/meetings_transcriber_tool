import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_model():
    model_name = "Qwen/Qwen2.5-7B-Instruct-AWQ"
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

def load_dialogue(json_path: str) -> str:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    speaker_map = {
        "A": "Speaker 1",
        "B": "Speaker 2",
        "C": "Speaker 3",
        "D": "Speaker 4",
        "E": "Speaker 5",
    }

    lines = []
    for turn in data:
        for speaker, text in turn.items():
            if speaker in speaker_map:
                speaker = speaker_map[speaker]
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def generate_text(model, tokenizer, prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an assistant. Receive the dialogue below and generate a Markdown document with the sections:\n"
                       "## Summary\n"
                       "Brief synthesis of the central theme discussed.\n\n"
                       "## Abstract\n"
                       "Running text citing the respective speaker to structure the narrative.\n\n"
                       "## Key Points\n"
                       "List the key points in bullets.\n\n"
                       "Dialogue:\n"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=4096 # Increased max_new_tokens for potentially longer summaries
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response


def summarize_and_save(json_path: str, output_md: str):
    model, tokenizer = load_model()
    dialogue = load_dialogue(json_path)
    
    #dialogue = "Speaker A: Oi, tudo bem?\nSpeaker B: Tudo bem, e você?\nSpeaker A: Muito bem, obrigado!\nSpeaker B: De nada!"
    
    markdown = generate_text(
        model,
        tokenizer,
        dialogue
    )

    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"Markdown saved at: {output_md}")

if __name__ == "__main__":
    json_path = "data/transcripts/2025-04-08 09-02-19_transcript_backup.json"
    output_md = "data/summaries/2025-04-08 09-02-19_summary.md"

    summarize_and_save(json_path, output_md)
