from moviepy import VideoFileClip
import os
import tempfile

def convert_mov_to_mp3(input_path: str, sample_rate: int = 44100, codec: str = 'mp3', bitrate: str = '192k'):
    """
    Convert a .mov file to .mp3 using MoviePy.

    Args:
        input_path: path for the input video file.
        output_path: path for the output audio file.
        sample_rate: sampling rate in Hz (default: 44100).
        codec: codec for the output audio file (default: mp3).
        bitrate: bitrate for the output audio file (default: 192k).
    """
    
    clip = VideoFileClip(input_path)
    audio = clip.audio

    with tempfile.NamedTemporaryFile(suffix=f".{codec}", delete=False) as temp_f:
        temp_file_path = temp_f.name
    
    audio.write_audiofile(temp_file_path, fps=sample_rate, codec=codec, bitrate=bitrate)
    clip.close()
    audio.close()
    
    return temp_file_path

if __name__ == "__main__":

    input_path = '/Users/gabrielmendessouza/Movies/2025-04-08 09-02-19.mov'
    output_name = input_path.split('/')[-1].split('.')[0] + '_audio.mp3'
    output_path = f"data/audios/{output_name}"

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(input_path):
        convert_mov_to_mp3(input_path, output_path)
    else:
        print(f"Input file not found: {input_path}")
