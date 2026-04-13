"""
Layer 6: Plagiarism Checker
Free local plagiarism detection using cosine similarity on TF-IDF vectors.
Compares draft against research source content.
No external API needed - runs entirely locally.
"""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import PLAGIARISM_THRESHOLD


def split_into_paragraphs(text: str) -> list:
      """Split text into paragraphs."""
      paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
      return paragraphs


def get_source_texts(research_data: dict) -> list:
      """Extract all source texts."""
      sources = []
      for source in research_data.get("sources", []):
                content = source.get("content", source.get("snippet", ""))
                if content and not content.startswith("[Could not fetch"):
                              sources.append({
                                                "text": content[:2000],
                                                "title": source.get("title", "Unknown"),
                                                "url": source.get("url", "")
                              })
                      return sources


def check_similarity(text1: str, text2: str) -> float:
      """Calculate cosine similarity between two texts using TF-IDF."""
      try:
                vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words="english")
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
except Exception:
        return 0.0


def run_plagiarism_check(draft: str, research_data: dict = None) -> dict:
      """
          Check draft for plagiarism against source documents.
              Returns a report with similarity scores per paragraph.
                  """
      paragraphs = split_into_paragraphs(draft)
      source_texts = get_source_texts(research_data) if research_data else []

    if not source_texts:
              # Still run basic n-gram duplication check within the document
              print("  No source corpus - running internal duplication check only")
              return _internal_duplication_check(paragraphs)

    print(f"  Checking {len(paragraphs)} paragraphs against {len(source_texts)} sources...")

    results = []
    max_similarities = []
    threshold = PLAGIARISM_THRESHOLD

    for para in paragraphs[:20]:
              para_results = []
              for source in source_texts[:10]:
                            sim = check_similarity(para, source["text"])
                            if sim > threshold:
                                              para_results.append({
                                                                    "source_title": source["title"][:60],
                                                                    "source_url": source["url"],
                                                                    "similarity": round(sim, 3)
                                              })

                        max_sim = max([r["similarity"] for r in para_results], default=0.0)
        max_similarities.append(max_sim)

        if para_results:
                      results.append({
                                        "paragraph": para[:150] + "...",
                                        "max_similarity": round(max_sim, 3),
                                        "flagged": max_sim > threshold,
                                        "matching_sources": sorted(para_results, key=lambda x: -x["similarity"])[:3]
                      })

    overall_similarity = float(np.mean(max_similarities)) if max_similarities else 0.0
    flagged_count = sum(1 for r in results if r.get("flagged", False))

    if overall_similarity > 0.5:
              plagiarism_verdict = "HIGH SIMILARITY - Rewrite Required"
elif overall_similarity > 0.3:
        plagiarism_verdict = "MODERATE SIMILARITY - Review Recommended"
else:
        plagiarism_verdict = "LOW SIMILARITY - Appears Original"

    report = {
              "overall_similarity": round(overall_similarity, 3),
              "plagiarism_verdict": plagiarism_verdict,
              "paragraphs_checked": len(paragraphs[:20]),
              "flagged_paragraphs": flagged_count,
              "detailed_results": results[:10],
              "threshold_used": threshold
    }

    print(f"  Plagiarism check: {plagiarism_verdict}")
    print(f"  Overall similarity: {overall_similarity:.1%} | Flagged: {flagged_count} paragraphs")

    return report


def _internal_duplication_check(paragraphs: list) -> dict:
      """Fallback: check for internal repetition within the document."""
    duplicates = []
    for i, p1 in enumerate(paragraphs):
              for j, p2 in enumerate(paragraphs[i+1:], i+1):
                            sim = check_similarity(p1, p2)
                            if sim > 0.8:
                                              duplicates.append({"para1": i, "para2": j, "similarity": round(sim, 3)})

                    return {
                              "overall_similarity": 0.0,
                              "plagiarism_verdict": "No external sources to compare against",
                              "internal_duplicates": len(duplicates),
                              "duplicate_details": duplicates[:5]
                    }
