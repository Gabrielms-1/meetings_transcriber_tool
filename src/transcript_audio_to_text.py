import whisper
import time
import os
import soundfile as sf
import numpy as np
from io import BytesIO

MODEL_NAME = "tiny"
ASR_MODEL = whisper.load_model(MODEL_NAME, device="cpu")

def transcript_audio_to_text(audio_buffer: BytesIO):
    audio_buffer.seek(0)
    audio_np, _ = sf.read(audio_buffer, dtype='float32')
    audio_buffer.close()

    result = ASR_MODEL.transcribe(audio_np)

    conversation = []

    for segment in result["segments"]:
        conversation.append(segment["text"])

    return conversation


if __name__ == "__main__":
    for i, audio in enumerate(os.listdir("data/audios/processed")):
        audio_path = os.path.join("data/audios/processed", audio)
        audio_ext = os.path.splitext(audio)[1]
        start_time = time.time()
        transcript_audio_to_text(audio_path, os.path.join("data/transcripts", audio.split(".")[0] + ".log"))
        end_time = time.time()
        print(f"Time taken to transcribe {audio_ext}: {end_time - start_time} seconds")






