"""
Smart Writer Stack - Configuration
Edit to customize. Add API keys to .env file (never commit keys to GitHub!).
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Google Gemini Pro API Key - get free at: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini model: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Free local models (auto-downloaded on first run)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"        # ~90MB - for hallucination scoring
AI_DETECTOR_MODEL = "roberta-base-openai-detector"  # ~500MB - for AI detection

# Research settings
RESEARCH_MAX_RESULTS = 5
RESEARCH_MAX_CONTENT_LENGTH = 5000

# Quality thresholds (0-1 scale)
HALLUCINATION_THRESHOLD = 0.30  # Sentences below this are flagged
PLAGIARISM_THRESHOLD = 0.45     # Paragraphs above this are flagged

# Output settings
OUTPUT_DIR = "outputs"
SAVE_JSON = True
SAVE_MARKDOWN = True
SAVE_DOCX = True

if not GEMINI_API_KEY:
      print("WARNING: GEMINI_API_KEY not set. Add it to your .env file.")
      print("Get a free key at: https://aistudio.google.com/app/apikey")
