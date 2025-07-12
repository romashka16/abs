from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).parent.resolve()

# Папки с видео, аудио и результатами
BASE_FOLDER    = r"C:\Videos"
TOP_FOLDER = os.path.join(BASE_FOLDER, "top_clips")
STACKED_FOLDER   = os.path.join(BASE_FOLDER, "stacked_videos")
AUDIO_FOLDER     = os.path.join(BASE_FOLDER, "audio_wavs")
SUBTITLED_FOLDER = os.path.join(BASE_FOLDER, "subtitled_videos")
SEGMENTS_ROOT    = os.path.join(BASE_FOLDER, "segments")
BOTTOM_FOLDER = os.path.join(BASE_FOLDER, "bottom_clips")

# MFA данные
MFA_CORPUS_TXTS = PROJECT_ROOT / "mfa_data" / "corpus" / "txts"
MFA_CORPUS_WAVS = PROJECT_ROOT / "mfa_data" / "corpus" / "wavs"
MFA_OUTPUT = PROJECT_ROOT / "mfa_data" / "output"

# Русские словари и модели MFA
RUSSIAN_DICT = PROJECT_ROOT / "russian" / "russian_cv.dict"
RUSSIAN_MFA_DICT = PROJECT_ROOT / "russian" / "russian_mfa.dict"
RUSSIAN_MFA_MODEL_DIR = PROJECT_ROOT / "russian" / "russian_mfa"
