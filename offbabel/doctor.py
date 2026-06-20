"""Preflight check. Run on ANY machine to see what is ready: python -m offbabel.doctor

Prints OK/MISS per dependency and a readiness summary per mode, so the teammate can verify
his Mac (or you, Windows) in seconds. Exit code is non-zero if a critical-path piece is missing.
"""
import importlib
import os
import platform
import sys

from . import config

# (label, import_name, critical_for)  critical_for: None means optional
CHECKS = [
    ("numpy", "numpy", "core"),
    ("opencv", "cv2", "sign"),
    ("mediapipe", "mediapipe", "sign"),
    ("scikit-learn", "sklearn", "sign"),
    ("pandas", "pandas", "sign"),
    ("joblib", "joblib", "sign"),
    ("faster-whisper", "faster_whisper", "speak"),
    ("sounddevice", "sounddevice", "speak"),
    ("piper-tts", "piper", "speak"),
    ("openai", "openai", "speak"),
    ("fastapi", "fastapi", "server"),
    ("uvicorn", "uvicorn", "server"),
    ("cognee (optional)", "cognee", None),
    ("reachy-mini (optional)", "reachy_mini", None),
]


def main():
    print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}\n")
    present = set()
    for label, mod, _crit in CHECKS:
        try:
            importlib.import_module(mod)
            present.add(mod)
            print(f"  OK   {label}")
        except Exception:  # noqa: BLE001
            print(f"  MISS {label}")

    print("\nAssets:")
    model_ok = os.path.exists(config.HAND_MODEL_PATH)
    print(f"  {'OK  ' if model_ok else 'MISS'} hand model  ({config.HAND_MODEL_PATH})")
    trained = os.path.exists(config.SIGN_MODEL_PATH)
    print(f"  {'OK  ' if trained else '--  '} trained sign classifier"
          f"  ({'present' if trained else 'run capture + train'})")

    def ready(mods):
        return all(m in present for m in mods)

    sign_ok = ready(["cv2", "mediapipe", "sklearn", "pandas", "joblib"]) and model_ok
    speak_ok = ready(["faster_whisper", "sounddevice", "piper", "openai"])
    server_ok = ready(["fastapi", "uvicorn"])

    print("\nReadiness:")
    print(f"  SERVER + UI : {'READY' if server_ok else 'install fastapi/uvicorn'}")
    print(f"  SIGN engine : {'READY' if sign_ok else 'install sign deps / model'}"
          f"{'' if trained else '  (then capture + train a classifier)'}")
    print(f"  SPEAK loop  : {'deps READY (wire models on Mac)' if speak_ok else 'install speak deps'}")
    print(f"  MEMORY      : READY (SQLite, always on)")

    critical = server_ok and sign_ok
    sys.exit(0 if critical else 1)


if __name__ == "__main__":
    main()
