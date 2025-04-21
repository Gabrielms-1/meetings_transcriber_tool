from moviepy import VideoFileClip
import os

def convert_mov_to_wav(input_path: str, output_path: str, sample_rate: int = 44100, codec: str = 'mp3', bitrate: str = '192k'):
    """
    Convert a .mov file to .wav using MoviePy.

    Args:
        input_path: path for the input video file.
        output_path: path for the output audio file.
        sample_rate: sampling rate in Hz (default: 44100).
        codec: codec for the output audio file (default: mp3).
        bitrate: bitrate for the output audio file (default: 192k).
    """
    clip = VideoFileClip(input_path)
    audio = clip.audio
    audio.write_audiofile(output_path, fps=sample_rate, codec=codec, bitrate=bitrate)
    clip.close()

if __name__ == "__main__":

    input_path = '/Users/gabrielmendessouza/Movies/2025-04-08 09-02-19.mov'
    output_name = input_path.split('/')[-1].split('.')[0] + '_audio.mp3'
    output_path = f"data/audios/{output_name}"

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(input_path):
        convert_mov_to_wav(input_path, output_path)
        print(f"Conversion complete: {output_path}")
    else:
        print(f"Input file not found: {input_path}")
