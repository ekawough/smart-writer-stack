"""
Layer 4: Hallucination Scorer
Scores the draft for hallucination risk using semantic similarity.
Compares draft sentences against research source content.
High similarity = grounded. Low similarity = potential hallucination.
Uses sentence-transformers (free, runs locally, no API needed).
"""

import numpy as np
from sentence_transformers import SentenceTransformer, util
from config import HALLUCINATION_THRESHOLD, EMBEDDING_MODEL

# Load free local model (downloads once, ~90MB)
_model = None

def get_model():
      global _model
      if _model is None:
                print(f"  Loading embedding model: {EMBEDDING_MODEL}")
                _model = SentenceTransformer(EMBEDDING_MODEL)
            return _model


def split_into_sentences(text: str) -> list:
      """Split text into sentences for analysis."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 30]


def get_source_corpus(research_data: dict) -> list:
      """Get all source text as a flat list of chunks."""
    corpus = []
    for source in research_data.get("sources", []):
              content = source.get("content", source.get("snippet", ""))
              if content and not content.startswith("[Could not fetch"):
                            # Split into ~200 char chunks
                            chunks = [content[i:i+200] for i in range(0, len(content), 200)]
                            corpus.extend(chunks)
                    return corpus[:500]  # Cap at 500 chunks for performance


def run_hallucination_score(draft: str, research_data: dict) -> dict:
      """
          Score the draft for hallucination risk.
              Returns a report with per-sentence scores and overall risk level.
                  """
    model = get_model()

    sentences = split_into_sentences(draft)
    corpus = get_source_corpus(research_data)

    if not corpus:
              print("  Warning: No source corpus available for hallucination check")
        return {
                      "overall_score": 0.0,
                      "risk_level": "UNKNOWN",
                      "sentences_checked": 0,
                      "flagged_sentences": []
        }

    print(f"  Encoding {len(sentences)} sentences and {len(corpus)} source chunks...")

    # Encode all texts
    sentence_embeddings = model.encode(sentences[:50], convert_to_tensor=True)
    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

    # Find max similarity of each sentence to any source chunk
    scores = []
    flagged = []
    threshold = HALLUCINATION_THRESHOLD

    for i, (sentence, sent_emb) in enumerate(zip(sentences[:50], sentence_embeddings)):
              similarities = util.cos_sim(sent_emb, corpus_embeddings)[0]
        max_sim = float(similarities.max())
        scores.append(max_sim)

        if max_sim < threshold:
                      flagged.append({
                                        "sentence": sentence[:200],
                                        "similarity_score": round(max_sim, 3),
                                        "risk": "HIGH" if max_sim < 0.2 else "MEDIUM"
                      })

    overall_score = float(np.mean(scores)) if scores else 0.0

    if overall_score > 0.5:
              risk_level = "LOW"
elif overall_score > 0.3:
        risk_level = "MEDIUM"
else:
        risk_level = "HIGH"

    report = {
              "overall_score": round(overall_score, 3),
              "risk_level": risk_level,
              "sentences_checked": len(scores),
              "flagged_count": len(flagged),
              "flagged_sentences": flagged[:10],  # Top 10 most suspicious
              "threshold_used": threshold
    }

    print(f"  Hallucination risk: {risk_level} (avg similarity: {overall_score:.3f})")
    print(f"  Flagged {len(flagged)} potentially hallucinated sentences")

    return report
