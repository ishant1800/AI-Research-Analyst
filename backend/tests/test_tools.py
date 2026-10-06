import pytest
from app.services.search_service import SearchService
from app.services.web_scraper import WebScraper

def test_mock_search_service():
    service = SearchService(provider="mock")
    results = service.search("solid-state battery density", max_results=3)
    assert len(results) > 0
    assert any("battery" in r.title.lower() or "battery" in r.snippet.lower() for r in results)
    for r in results:
        assert r.url.startswith("http")
        assert len(r.snippet) > 10

def test_search_fallback_on_empty():
    service = SearchService(provider="mock")
    results = service.search("quantum teleportation astrophysics warp drive", max_results=2)
    assert len(results) > 0
    assert results[0].url.startswith("http")

def test_web_scraper_html_cleaning():
    scraper = WebScraper(max_chars=500)
    raw_html = """
    <!DOCTYPE html>
    <html>
      <head><title>Test Article</title><style>.hidden { display: none; }</style></head>
      <body>
        <nav><a href="/home">Home</a><a href="/about">About</a></nav>
        <article>
          <h1>Solid-State Breakthrough</h1>
          <p>Cell density verified at 480 Wh/kg during independent laboratory stress tests.</p>
        </article>
        <footer><p>Copyright 2025 All Rights Reserved.</p></footer>
        <script>console.log("tracking");</script>
      </body>
    </html>
    """
    clean_text = scraper.extract_clean_text(raw_html)
    assert "Solid-State Breakthrough" in clean_text
    assert "480 Wh/kg" in clean_text
    assert "console.log" not in clean_text
    assert "Copyright" not in clean_text
    assert "display: none" not in clean_text

def test_web_scraper_char_bound():
    scraper = WebScraper(max_chars=100)
    huge_html = "<html><body><p>" + ("word " * 500) + "</p></body></html>"
    result = scraper.extract_clean_text(huge_html)
    assert len(result) < 300 # Includes truncation notice
    assert "truncated" in result.lower()
