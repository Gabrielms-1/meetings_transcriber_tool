import assemblyai as aai
import json
import os

aai.settings.api_key = os.getenv("ASSEMBLYAI_KEY")

def transcript_audio_to_text(audio_path: str, output_path: str):
    config = aai.TranscriptionConfig(
        speaker_labels=True,
    )
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(audio_path, config=config)

    conversation = []

    for utterance in transcript.json_response['utterances']:
        conversation.append({
            utterance['speaker']: utterance['text']
        })

    with open(output_path, 'w') as f:
        json.dump(conversation, f, indent=4)

    return conversation