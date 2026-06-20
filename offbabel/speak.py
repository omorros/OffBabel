"""Speak mode (Person A / Mac): mic -> faster-whisper -> Exo LLM -> Piper TTS -> speakers.

This is a scaffold. The structure and the tutor prompt are done. The TODOs need the cached
models on the Mac (see PRD 3 + 11). Wire it into the server like this:

    # in server.py handle(), replace the speak_text stub body with:
    from . import speak
    data = speak.tutor_turn(text, lang)
    await hub.send({"type": "transcript", "role": "user", "text": text})
    await emote("speaking")
    await hub.send({"type": "transcript", "role": "tutor", "text": data["reply"]})
    if data.get("correction"):
        await hub.send({"type": "correction", **data["correction"]})
        memory.log_miss("word", lang, data["correction"]["wrong"][:40])
    speak.speak_tts(data["reply"], lang)

Push-to-talk audio path: capture mic with sounddevice while the PTT button is held, then
transcribe() the buffer and feed the text through tutor_turn() exactly like the text fallback.
"""
import json

from . import config

LANG_NAMES = {"es": "Spanish", "en": "English", "cs": "Czech"}

TUTOR_PROMPT = (
    "You are a friendly, patient {language} conversation tutor. Reply ONLY in {language}, "
    "1-2 short sentences, and keep the conversation going with a simple question. If the "
    "learner's last message has a grammar or word-choice mistake, briefly correct it. "
    'Return JSON: {{"reply": "...", "correction": {{"wrong": "...", "right": "...", '
    '"note": "..."}} | null}}. Keep vocabulary simple (A2-B1).'
)


def get_llm():
    """OpenAI client pointed at Exo (localhost:52415). Falls back to Ollama via env (PRD 9)."""
    from openai import OpenAI
    return OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def tutor_turn(user_text, language):
    """Run one tutor turn. Returns {"reply": str, "correction": {...} | None}."""
    client = get_llm()
    sys = TUTOR_PROMPT.format(language=LANG_NAMES.get(language, "Spanish"))
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": user_text},
        ],
        temperature=0.4,
    )
    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except Exception:  # noqa: BLE001
        # small models sometimes wrap JSON in prose; degrade to plain reply
        data = {"reply": raw, "correction": None}
    return data


def transcribe(audio, language):
    """TODO (Mac): faster-whisper 'small' int8. Load the model ONCE at startup, not per call.

    from faster_whisper import WhisperModel
    _MODEL = WhisperModel(config.WHISPER_SIZE, device="cpu", compute_type="int8")
    segments, _ = _MODEL.transcribe(audio, language=language)
    return " ".join(s.text for s in segments).strip()
    """
    raise NotImplementedError("wire faster-whisper on the Mac")


def speak_tts(text, language):
    """TODO (Mac): Piper with the LOCAL voice path for `language` (never a bare name).

    voice = config.PIPER_VOICES[language]   # e.g. .../cs_CZ-jirka-medium.onnx
    subprocess: piper -m {voice} -f out.wav  then play out.wav on the speakers.
    """
    raise NotImplementedError("wire Piper on the Mac with local voice paths")
