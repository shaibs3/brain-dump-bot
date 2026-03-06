from pathlib import Path

from google.cloud import speech

from config import LANGUAGE_CODE


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Google Speech-to-Text.

    Args:
        audio_path: Path to the audio file (OGG/OPUS format from Telegram)

    Returns:
        Transcribed text, or empty string if transcription fails
    """
    client = speech.SpeechClient()

    audio_file = Path(audio_path)
    with open(audio_file, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)

    # Telegram voice notes are OGG with OPUS codec
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code=LANGUAGE_CODE,
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio)

    transcript_parts = []
    for result in response.results:
        if result.alternatives:
            transcript_parts.append(result.alternatives[0].transcript)

    return " ".join(transcript_parts)
