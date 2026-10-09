import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "CivicClarity"
API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL = "gemini-flash-latest"

OFFICIAL_CHANNEL_TEXT = "your city's official grievance portal, mobile app or helpline"

MAX_HISTORY_TURNS = 6
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.3