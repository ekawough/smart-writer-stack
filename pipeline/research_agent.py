"""
Layer 1: Research Agent
Uses DuckDuckGo (free, no API key) to search the web and gather real sources.
Returns structured research data with URLs, titles, and summaries.
"""

import json
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from config import RESEARCH_MAX_RESULTS, RESEARCH_MAX_CONTENT_LENGTH


def search_web(query: str, max_results: int = None) -> list:
      """Search DuckDuckGo for real sources. No API key needed."""
      max_results = max_results or RESEARCH_MAX_RESULTS
      results = []
      with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                              results.append({
                                                "title": r.get("title", ""),
                                                "url": r.get("href", ""),
                                                "snippet": r.get("body", "")
                              })
                      return results


def fetch_page_content(url: str, max_length: int = None) -> str:
      """Fetch and extract main text from a URL."""
      max_length = max_length or RESEARCH_MAX_CONTENT_LENGTH
      try:
                headers = {"User-Agent": "Mozilla/5.0 (research bot)"}
                resp = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(resp.text, "lxml")
                # Remove scripts and styles
                for tag in soup(["script", "style", "nav", "footer"]):
                              tag.decompose()
                          text = soup.get_text(separator=" ", strip=True)
                return text[:max_length]
except Exception as e:
        return f"[Could not fetch content: {e}]"


def run_research(topic: str) -> dict:
      """
          Main research function. Searches multiple query variations
              and returns structured data with real sources.
                  """
      print(f"  Searching for: {topic}")

    # Generate multiple search queries for comprehensive coverage
      queries = [
          topic,
          f"{topic} research study",
          f"{topic} academic evidence",
          f"{topic} recent findings",
          f"{topic} statistics data"
      ]

    all_sources = []
    seen_urls = set()

    for query in queries:
              results = search_web(query, max_results=5)
              for r in results:
                            if r["url"] not in seen_urls:
                                              seen_urls.add(r["url"])
                                              all_sources.append(r)

                    # Fetch full content for top sources
                    print(f"  Fetching content from {min(10, len(all_sources))} sources...")
    for i, source in enumerate(all_sources[:10]):
              source["content"] = fetch_page_content(source["url"])
        print(f"  [{i+1}/10] {source['title'][:60]}...")

    research_data = {
              "topic": topic,
              "total_sources": len(all_sources),
              "sources": all_sources,
              "queries_used": queries
    }

    print(f"  Research complete: {len(all_sources)} sources found")
    return research_data
