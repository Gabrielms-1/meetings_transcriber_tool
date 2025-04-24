import os
import json
from google import genai
from google.genai import types

def main():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    pre_prompt = """
        You are a helpful assistant that summarizes and organizes a conversation. \
        The conversation is separated by the turns of each participant, separated by Speaker letters (A, B, C, etc.). \
        Please generate a long text in markdown that synthesizes and organizes this conversation. \
        Explain decisions made, and then a paragraph with next steps.
    """

    
    config = types.GenerateContentConfig(
        max_output_tokens=500,
        temperature=0.5,
        system_instruction=pre_prompt,
    )

    with open("data/transcripts/2025-04-07 11-57-48_transcript.json", "r") as f:
        dialogue = json.loads(f.read())

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=json.dumps(dialogue, ensure_ascii=False, indent=2),
        config=config,
    )

    print(response.text)

if __name__ == "__main__":
    main()
