import subprocess
import os

def convert_mov_to_wav(input_video_path: str, output_audio_path: str):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-vn',
        '-acodec', 'pcm_s16le', # Specify WAV codec
        '-ar', '44100',
        '-ac', '1', 
        output_audio_path
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":

    input_file = "path/to/your/video.mov"
    output_file = "path/to/your/output.wav"

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(input_file):
        convert_mov_to_wav(input_file, output_file)
        print(f"Conversion complete: {output_file}")
    else:
        print(f"Input file not found: {input_file}")
