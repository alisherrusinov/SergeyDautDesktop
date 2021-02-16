from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
TEMP_VOICE_DIR = os.path.join(BASE_DIR, 'media', 'temp_voice')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'media', 'templates')
MUSIC_DIR = os.path.join(BASE_DIR, 'media', 'music')
