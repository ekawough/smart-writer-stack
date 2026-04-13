"""
Layer 2: Writing Agent (Ghostwriter)
Uses Google Gemini Pro to produce professional long-form documents.
Grounded in the research data from Layer 1 to minimize hallucinations.
Supports: dissertation, essay, report, article, thesis, proposal
"""

import google.generativeai as genai
import os
from config import GEMINI_MODEL, GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

DOC_TYPE_PROMPTS = {
      "dissertation": """You are an expert academic ghostwriter specializing in PhD dissertations.
      Write in a formal, scholarly tone with proper academic structure.
      Include: Abstract, Introduction, Literature Review, Methodology, Discussion, Conclusion, References.
      Every factual claim MUST cite a specific source from the research data provided.""",

      "essay": """You are a professional essay writer.
      Write in a clear, analytical tone with strong thesis, body paragraphs, and conclusion.
      Every factual claim must reference a source from the provided research.""",

      "report": """You are a professional report writer.
      Write in a structured, objective tone with executive summary, findings, analysis, and recommendations.
      All data and statistics must cite their source from the research provided.""",

      "article": """You are a professional journalist and content writer.
      Write in an engaging, informative tone suitable for publication.
      All factual claims must link to real sources from the research provided.""",

      "thesis": """You are an expert academic writer specializing in Master's and PhD theses.
      Write with rigorous academic standards. Include proper structure and cite all sources.""",

      "proposal": """You are an expert research proposal writer.
      Write in a persuasive yet academic tone. Include background, rationale, objectives, and methodology."""
}


def build_prompt(topic: str, research_data: dict, doc_type: str) -> str:
      """Build a grounded writing prompt using real research sources."""
      system_prompt = DOC_TYPE_PROMPTS.get(doc_type, DOC_TYPE_PROMPTS["essay"])

    # Build source context from research
      sources_text = ""
      for i, source in enumerate(research_data.get("sources", [])[:10], 1):
                sources_text += f"\n[Source {i}] {source['title']}\n"
                sources_text += f"URL: {source['url']}\n"
                sources_text += f"Content: {source.get('content', source.get('snippet', ''))[:800]}\n"
                sources_text += "-" * 40 + "\n"

      prompt = f"""{system_prompt}

  TOPIC: {topic}
  DOCUMENT TYPE: {doc_type.upper()}

  RESEARCH SOURCES (use ONLY these sources for citations - do NOT invent sources):
  {sources_text}

  IMPORTANT RULES:
  1. Only cite sources listed above. Never invent fake citations.
  2. If a fact cannot be sourced from the above, do not include it.
  3. Format citations as [Source N] inline in the text.
  4. Write at least 2000 words for a {doc_type}.
  5. Use professional {doc_type} structure and formatting.

  Now write the complete {doc_type} on: {topic}
  """
      return prompt


def run_writing(topic: str, research_data: dict, doc_type: str = "dissertation") -> str:
      """Generate a full document using Gemini Pro, grounded in research sources."""
      model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = build_prompt(topic, research_data, doc_type)

    print(f"  Generating {doc_type} with Gemini {GEMINI_MODEL}...")
    response = model.generate_content(
              prompt,
              generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=8192,
              )
    )

    draft = response.text
    print(f"  Writing complete: {len(draft.split())} words generated")
    return draft
