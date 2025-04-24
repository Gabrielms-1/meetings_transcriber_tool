import whisper
import json
import os

MODEL_NAME = "tiny"
ASR_MODEL = whisper.load_model(MODEL_NAME, device="cpu")

def transcript_audio_to_text(audio_path: str, output_path: str):

    result = ASR_MODEL.transcribe(audio_path)

    conversation = []

    for segment in result["segments"]:
        conversation.append(segment["text"])

    exit()
    
    with open(output_path, 'w') as f:
        f.write("\n".join(conversation))

    return conversation


if __name__ == "__main__":
    transcript_audio_to_text("data/audios/2025-04-08 09-02-19_audio.mp3", "data/transcripts/testing_gemini.log")






