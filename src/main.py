from transcript_audio_to_text import transcript_audio_to_text
from video_to_audio import convert_mov_to_mp3
from utils import preprocess_audio
from inference_with_gemini import inference_with_gemini
import os


def main(input_path: str, output_path: str):
    audio_buffer = convert_mov_to_mp3(input_path)
    audio_buffer = preprocess_audio(audio_buffer)
    conversation = transcript_audio_to_text(audio_buffer)
    
    summary = inference_with_gemini(conversation)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(summary)


    summary

if __name__ == "__main__":
    input_path = '/Users/gabrielmendessouza/Movies/2025-04-07 11-57-48.mov'
    output_file_name = "2025-04-07 11-57-48"
    
    output_path = output_file_name + '_transcript.log'
    output_path = f"data/summaries/{output_path}"

    # PIPELINE - - - - - - - - - - 
    main(input_path, output_path)