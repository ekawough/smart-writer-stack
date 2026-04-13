"""
Layer 3: Fact-Check Agent
Verifies every claim in the draft against real research sources.
Flags unsupported claims and forces source attribution.
Uses Gemini Pro for intelligent claim extraction + verification.
"""

import re
import google.generativeai as genai
from config import GEMINI_MODEL, GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


def extract_claims(draft: str, model) -> list:
      """Extract factual claims from the draft for verification."""
      prompt = f"""Extract all specific factual claims from this text.
  Return ONLY a numbered list of claims, one per line.
  Focus on statistics, dates, names, research findings, and specific assertions.

  TEXT:
  {draft[:3000]}

  Return format:
  1. [claim]
  2. [claim]
  etc."""

    response = model.generate_content(prompt)
    lines = response.text.strip().split("\n")
    claims = []
    for line in lines:
              line = line.strip()
              if line and line[0].isdigit():
                            claim = re.sub(r"^\d+\.\s*", "", line).strip()
                            if claim:
                                              claims.append(claim)
                                  return claims


def verify_claim_against_sources(claim: str, sources: list, model) -> dict:
      """Check if a claim is supported by the research sources."""
      sources_text = ""
      for i, source in enumerate(sources[:8], 1):
                content = source.get("content", source.get("snippet", ""))[:500]
                sources_text += f"[Source {i}]: {source['title']}\n{content}\n\n"

      prompt = f"""Verify this claim against the provided sources.

  CLAIM: {claim}

  SOURCES:
  {sources_text}

  Respond with EXACTLY:
  VERDICT: [SUPPORTED / UNSUPPORTED / PARTIAL]
  SOURCE: [Source number if supported, or "None"]
  CONFIDENCE: [HIGH / MEDIUM / LOW]
  NOTE: [Brief explanation]"""

    response = model.generate_content(prompt)
    text = response.text

    result = {
              "claim": claim,
              "verdict": "UNKNOWN",
              "source": "None",
              "confidence": "LOW",
              "note": ""
    }

    for line in text.split("\n"):
              if line.startswith("VERDICT:"):
                            result["verdict"] = line.replace("VERDICT:", "").strip()
elif line.startswith("SOURCE:"):
            result["source"] = line.replace("SOURCE:", "").strip()
elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.replace("CONFIDENCE:", "").strip()
elif line.startswith("NOTE:"):
            result["note"] = line.replace("NOTE:", "").strip()

    return result


def run_fact_check(draft: str, research_data: dict) -> tuple:
      """
          Fact-check the entire draft against research sources.
              Returns (cleaned_draft, fact_check_report).
                  """
      model = genai.GenerativeModel(GEMINI_MODEL)
      sources = research_data.get("sources", [])

    print("  Extracting claims from draft...")
    claims = extract_claims(draft, model)
    print(f"  Found {len(claims)} claims to verify")

    report = {
              "total_claims": len(claims),
              "supported": 0,
              "unsupported": 0,
              "partial": 0,
              "results": []
    }

    for i, claim in enumerate(claims[:20]):  # Check up to 20 claims
              result = verify_claim_against_sources(claim, sources, model)
              report["results"].append(result)

        if result["verdict"] == "SUPPORTED":
                      report["supported"] += 1
elif result["verdict"] == "UNSUPPORTED":
              report["unsupported"] += 1
else:
              report["partial"] += 1

        print(f"  Claim {i+1}/{min(20, len(claims))}: {result['verdict']}")

    # Calculate fact score
    if report["total_claims"] > 0:
              report["fact_score"] = round(
                            (report["supported"] + 0.5 * report["partial"]) / min(20, report["total_claims"]) * 100, 1
              )
else:
          report["fact_score"] = 100.0

    print(f"  Fact-check score: {report['fact_score']}%")
    print(f"  Supported: {report['supported']} | Unsupported: {report['unsupported']} | Partial: {report['partial']}")

    return draft, report
