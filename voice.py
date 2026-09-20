"""
Kisan Vaani - Voice Processing Module (Speech-to-Text & Text-to-Speech).
Uses SpeechRecognition (free, zero Gemini API quota consumption) with Gemini audio fallback.
"""

import io
import re
import warnings
from typing import Optional
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai

import agent

warnings.filterwarnings("ignore")


def is_devanagari(text: str) -> bool:
    """Check if the text contains Devanagari (Hindi) characters."""
    return bool(re.search(r"[\u0900-\u097F]", text))


def clean_text_for_speech(text: str) -> str:
    """Clean markdown artifacts, asterisks, bullet markers for natural voice synthesis."""
    # Remove bold, italics, headers
    cleaned = re.sub(r"[\*#_`~]", " ", text)
    # Remove brackets and bullets
    cleaned = re.sub(r"^\s*[-•]\s*", "", cleaned, flags=re.MULTILINE)
    # Replace multiple spaces/newlines
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def transcribe_audio_free(audio_bytes: bytes) -> Optional[str]:
    """
    Transcribe recorded WAV audio using Google Speech Recognition.
    Zero Gemini quota consumed. Free and fast for Hindi and English.
    """
    try:
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            # Adjust for ambient noise and read audio
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.record(source)

        # Try Hindi first (typical for rural farmers)
        try:
            hindi_text = r.recognize_google(audio, language="hi-IN")
            if hindi_text and hindi_text.strip():
                return hindi_text.strip()
        except sr.UnknownValueError:
            pass
        except Exception:
            pass

        # Try Indian English
        try:
            en_text = r.recognize_google(audio, language="en-IN")
            if en_text and en_text.strip():
                return en_text.strip()
        except sr.UnknownValueError:
            pass
        except Exception:
            pass

    except Exception as e:
        print(f"SpeechRecognition local error: {e}")

    return None


def transcribe_audio_gemini(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """
    Fallback transcription using Gemini multimodal audio model.
    """
    agent.configure_gemini()
    models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]

    prompt = (
        "You are an accurate multilingual audio transcriber for Indian farmers. "
        "Transcribe this spoken audio verbatim in the exact language spoken (Hindi or English). "
        "Do not translate. Return ONLY the transcribed text, with no explanations, quotes, or preamble."
    )

    last_err = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([
                {"mime_type": mime_type, "data": audio_bytes},
                prompt,
            ])
            if response.text:
                return response.text.strip()
        except Exception as e:
            last_err = e
            continue

    if last_err:
        raise last_err
    return ""


def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """
    Main transcription entry point:
    1. First uses SpeechRecognition (0 Gemini quota used)
    2. Falls back to Gemini multimodal if needed
    """
    # Try free local/web speech recognition first to save Gemini quota
    recognized = transcribe_audio_free(audio_bytes)
    if recognized:
        return recognized

    # Fallback to Gemini if needed
    return transcribe_audio_gemini(audio_bytes, mime_type=mime_type)


def generate_speech(text: str) -> Optional[bytes]:
    """
    Convert text response to speech audio bytes (MP3) using gTTS.
    Automatically switches between Hindi and Indian English.
    """
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return None

    # Detect language: Hindi if Devanagari characters present, else Indian English
    if is_devanagari(clean_text):
        lang = "hi"
        tld = "com"
    else:
        lang = "en"
        tld = "co.in"

    try:
        tts = gTTS(text=clean_text, lang=lang, tld=tld, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None
