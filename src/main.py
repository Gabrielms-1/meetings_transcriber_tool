from transcript_audio_to_text import transcript_audio_to_text
from video_to_audio import convert_mov_to_mp3
from utils import preprocess_audio
import os


def main(input_path: str, output_file_name: str):
    audio_buffer = convert_mov_to_mp3(input_path)
    audio_buffer = preprocess_audio(audio_buffer)
    conversation = transcript_audio_to_text(audio_buffer, output_path)
    
    conversation

if __name__ == "__main__":
    input_path = '/Users/gabrielmendessouza/Movies/2025-04-07 11-57-48.mov'
    output_file_name = "2025-04-07 11-57-48"
    
    output_path = output_file_name + '_transcript.json'
    output_path = f"data/transcripts/{output_path}"

    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)


    # PIPELINE - - - - - - - - - - 
    main(input_path, output_file_name)