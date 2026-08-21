import speech_recognition as sr
import io


def speech_to_text(audio_bytes, language="en-IN"):
    """
    Convert recorded audio bytes into text.

    Parameters:
        audio_bytes: Audio data received from Streamlit
        language: Speech recognition language code

    Returns:
        Transcribed text or None
    """

    if not audio_bytes:
        return None

    recognizer = sr.Recognizer()

    audio_file = io.BytesIO(audio_bytes)

    try:

        with sr.AudioFile(audio_file) as source:

            audio = recognizer.record(source)

        text = recognizer.recognize_google(
            audio,
            language=language
        )

        return text

    except sr.UnknownValueError:

        return None

    except sr.RequestError as e:

        raise RuntimeError(
            f"Speech recognition service error: {e}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Audio processing error: {e}"
        )