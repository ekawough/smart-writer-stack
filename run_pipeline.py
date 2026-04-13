"""
Smart Writer Stack - Main Pipeline Orchestrator
Powered by Google Gemini Pro (free tier)
Layers: Research > Write > Fact-Check > Hallucination Score > AI Detection > Plagiarism
"""

import sys
from pipeline.research_agent import run_research
from pipeline.writing_agent import run_writing
from pipeline.fact_check_agent import run_fact_check
from pipeline.hallucination_scorer import run_hallucination_score
from pipeline.ai_detector import run_ai_detection
from pipeline.plagiarism_checker import run_plagiarism_check
from pipeline.output_formatter import format_final_output


def run_full_pipeline(topic: str, doc_type: str = "dissertation"):
      print(f"\n{'='*60}")
      print(f"SMART WRITER STACK - Starting Pipeline")
      print(f"Topic: {topic} | Doc Type: {doc_type}")
      print(f"{'='*60}\n")

    print("[1/6] Research Agent...")
    research_data = run_research(topic)

    print("[2/6] Writing Agent (Gemini Pro)...")
    draft = run_writing(topic, research_data, doc_type)

    print("[3/6] Fact-Check Agent...")
    fact_checked_draft, fact_report = run_fact_check(draft, research_data)

    print("[4/6] Hallucination Scorer...")
    hallucination_report = run_hallucination_score(fact_checked_draft, research_data)

    print("[5/6] AI Detection...")
    ai_detection_report = run_ai_detection(fact_checked_draft)

    print("[6/6] Plagiarism Checker...")
    plagiarism_report = run_plagiarism_check(fact_checked_draft)

    output = format_final_output(
              topic=topic,
              doc_type=doc_type,
              draft=fact_checked_draft,
              fact_report=fact_report,
              hallucination_report=hallucination_report,
              ai_detection_report=ai_detection_report,
              plagiarism_report=plagiarism_report
    )

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE - Output saved to /outputs/")
    print(f"{'='*60}\n")
    return output


if __name__ == "__main__":
      if len(sys.argv) < 2:
                print('Usage: python run_pipeline.py "Your topic" [doc_type]')
                print('Example: python run_pipeline.py "Climate change effects" dissertation')
                sys.exit(1)
            topic = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "dissertation"
    run_full_pipeline(topic, doc_type)
