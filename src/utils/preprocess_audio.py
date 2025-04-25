from pydub import AudioSegment
import os
from io import BytesIO

def preprocess_audio(audio_buffer: BytesIO):

    audio = AudioSegment.from_file(audio_buffer, format="mp3")
    mono16 = audio.set_channels(1).set_frame_rate(16000)

    processed_audio_buffer = BytesIO()
    mono16.export(processed_audio_buffer, format="flac")

    processed_audio_buffer.seek(0)

    return processed_audio_buffer
