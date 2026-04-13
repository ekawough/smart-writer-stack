# Smart Writer Stack

**AI-powered professional writing platform** powered by Google Gemini Pro.

Research any topic, ghostwrite professional documents, then automatically fact-check, score for hallucinations, detect AI content, and check for plagiarism - all in one free pipeline.

## Quick Start

```bash
git clone https://github.com/ekawough/smart-writer-stack.git
cd smart-writer-stack
pip install -r requirements.txt
cp .env.example .env
# Add your free Gemini API key to .env
python run_pipeline.py "Your topic here" dissertation
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

## The 6-Layer Pipeline

| Layer | Tool | Cost |
|-------|------|------|
| 1. Research | DuckDuckGo Search | FREE |
| 2. Writing | Gemini Pro | FREE (1500 req/day) |
| 3. Fact Check | Gemini Pro | FREE |
| 4. Hallucination Score | sentence-transformers | FREE (local) |
| 5. AI Detection | roberta-base-openai-detector | FREE (local) |
| 6. Plagiarism Check | TF-IDF cosine similarity | FREE (local) |

## Supported Document Types

dissertation, thesis, essay, report, article, proposal

## Output

Each run saves to /outputs/ as Markdown, JSON, and DOCX with a full quality scorecard.

## License

MIT
