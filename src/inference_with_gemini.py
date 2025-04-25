import os
import json
from google import genai
from google.genai import types

def inference_with_gemini(conversation: list):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    pre_prompt = """
        You are a helpful assistant that summarizes and organizes a conversation. \
        The conversation is separated by lines aiming to identify the speaker, but without a clear separator. \
        Please generate a long text in markdown that synthesizes and organizes this conversation. \
        Explain decisions made, and then a paragraph with next steps. \
        Write everything like a report.
    """

    config = types.GenerateContentConfig(
        max_output_tokens=900,
        temperature=0.5,
        system_instruction=pre_prompt,
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=json.dumps(conversation, ensure_ascii=False, indent=2),
        config=config,
    )

    print(f"Tokens used: {response.usage_metadata.total_token_count} - - input tokens: {response.usage_metadata.prompt_token_count} - - output tokens: {response.usage_metadata.candidates_token_count}")

    return response.text
