"""
Layer 5: AI Content Detector
Detects AI-generated text patterns using a free HuggingFace model.
Uses roberta-base-openai-detector (trained to distinguish human vs AI text).
Runs locally - no API key, no cost.
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from config import AI_DETECTOR_MODEL

_detector = None


def get_detector():
      """Load the AI detection model (cached after first load)."""
      global _detector
      if _detector is None:
                print(f"  Loading AI detector model: {AI_DETECTOR_MODEL}")
                print("  (First run downloads ~500MB - cached after that)")
                _detector = pipeline(
                    "text-classification",
                    model=AI_DETECTOR_MODEL,
                    device=0 if torch.cuda.is_available() else -1
                )
            return _detector


def chunk_text(text: str, chunk_size: int = 400) -> list:
      """Split text into chunks that fit the model's context window."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
              if len(current_chunk) + len(sentence) < chunk_size:
                            current_chunk += " " + sentence
else:
            if current_chunk.strip():
                              chunks.append(current_chunk.strip())
                          current_chunk = sentence

    if current_chunk.strip():
              chunks.append(current_chunk.strip())

    return chunks


def run_ai_detection(text: str) -> dict:
      """
          Detect AI-generated content in the text.
              Returns a report with AI probability scores per chunk.
                  """
    detector = get_detector()
    chunks = chunk_text(text)

    print(f"  Analyzing {len(chunks)} text chunks for AI content...")

    results = []
    ai_scores = []

    for i, chunk in enumerate(chunks[:20]):  # Analyze up to 20 chunks
              try:
                            prediction = detector(chunk[:512], truncation=True)
                            label = prediction[0]["label"]
                            score = prediction[0]["score"]

                  # Model labels: "LABEL_1" = AI, "LABEL_0" = Human (or "Fake"/"Real")
                            if "fake" in label.lower() or label == "LABEL_1":
                                              ai_prob = score
              else:
                                ai_prob = 1 - score

                  ai_scores.append(ai_prob)
            results.append({
                              "chunk": chunk[:100] + "...",
                              "ai_probability": round(ai_prob, 3),
                              "label": "AI-GENERATED" if ai_prob > 0.7 else "LIKELY HUMAN" if ai_prob < 0.3 else "MIXED"
            })
except Exception as e:
            print(f"  Warning: Could not analyze chunk {i}: {e}")

    overall_ai_probability = sum(ai_scores) / len(ai_scores) if ai_scores else 0.0

    if overall_ai_probability > 0.7:
              detection_verdict = "HIGHLY AI-GENERATED"
elif overall_ai_probability > 0.4:
        detection_verdict = "PARTIALLY AI-GENERATED"
else:
        detection_verdict = "LIKELY HUMAN-WRITTEN"

    report = {
              "overall_ai_probability": round(overall_ai_probability, 3),
              "detection_verdict": detection_verdict,
              "chunks_analyzed": len(results),
              "chunk_results": results,
              "recommendation": (
                            "Significant rewriting recommended to reduce AI patterns."
                            if overall_ai_probability > 0.5
                            else "Text appears sufficiently original."
              )
    }

    print(f"  AI detection: {detection_verdict} ({overall_ai_probability:.1%} AI probability)")
    return report
