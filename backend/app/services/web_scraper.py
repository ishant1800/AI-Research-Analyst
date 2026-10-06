import httpx
from bs4 import BeautifulSoup
import logging
import re
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class WebScraper:
    def __init__(self, max_chars: Optional[int] = None, timeout_seconds: float = 8.0):
        self.max_chars = max_chars or settings.MAX_PAGE_EXTRACT_CHARS
        self.timeout = timeout_seconds

    def scrape_url(self, url: str) -> str:
        """Fetch and extract readable plain-text content from a URL."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return "Invalid URL provided."

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=HEADERS) as client:
                response = client.get(url)
                if response.status_code != 200:
                    return f"HTTP error {response.status_code} encountered while retrieving {url}."

                html = response.text
                return self.extract_clean_text(html)
        except Exception as e:
            logger.warning(f"Failed to fetch content from {url}: {e}")
            return f"Retrieval failed for {url}: {str(e)}"

    def extract_clean_text(self, html: str) -> str:
        """Parse HTML, strip navigational/boilerplate elements, and normalize whitespace."""
        soup = BeautifulSoup(html, "html.parser")

        # Strip scripts, stylesheets, comments, and boilerplate navigation
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"]):
            tag.decompose()

        # Find main article container if available
        article = soup.find("article") or soup.find("main") or soup.find("div", {"id": re.compile(r"content|main|post", re.I)})
        target = article if article else soup.body or soup

        # Extract text
        text = target.get_text(separator=" \n ")
        # Clean excessive spacing
        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and len(stripped) > 2:
                cleaned_lines.append(stripped)

        clean_text = "\n".join(cleaned_lines)
        if len(clean_text) > self.max_chars:
            clean_text = clean_text[:self.max_chars] + "\n...[Content truncated for token context budget]..."

        return clean_text

web_scraper = WebScraper()
