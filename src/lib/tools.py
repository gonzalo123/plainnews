import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from requests import RequestException
from strands import tool

from settings import get_settings

DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_MARKDOWN_CHARS = 100_000
USER_AGENT = "PlainNews/0.1 (+https://github.com/gonzalo123/plainnews)"

NOISY_SELECTORS = [
    "script",
    "style",
    "noscript",
    "nav",
    "aside",
    "footer",
    "form",
    "iframe",
    "svg",
    "button",
    "[role='navigation']",
    "[role='banner']",
    "[role='contentinfo']",
    "[class*='advert']",
    "[id*='advert']",
    "[class*='sponsor']",
    "[id*='sponsor']",
    "[class*='cookie']",
    "[id*='cookie']",
    "[class*='newsletter']",
    "[id*='newsletter']",
    "[class*='related']",
    "[id*='related']",
    "[class*='share']",
    "[id*='share']",
]


def is_supported_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def clean_html_to_markdown(html: str, *, max_chars: int = DEFAULT_MAX_MARKDOWN_CHARS) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for selector in NOISY_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()

    content = soup.find("main") or soup.find("article") or soup.body
    if content is None:
        return ""

    markdown = md(
        str(content),
        heading_style="ATX",
        bullets="-",
        strip=["a"],
    )
    markdown = normalize_markdown(markdown)

    if len(markdown) > max_chars:
        return markdown[:max_chars].rstrip() + "\n\n[Content truncated]"

    return markdown


def normalize_markdown(markdown: str) -> str:
    lines = [line.rstrip() for line in markdown.splitlines()]
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def fetch_url_as_markdown_impl(
    url: str,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_chars: int = DEFAULT_MAX_MARKDOWN_CHARS,
) -> str:
    if not is_supported_url(url):
        return "ERROR: URL must start with http:// or https://"

    try:
        response = requests.get(
            url,
            timeout=timeout_seconds,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
    except RequestException as error:
        return f"ERROR: Could not fetch URL: {error}"

    markdown = clean_html_to_markdown(response.text, max_chars=max_chars)
    if not markdown:
        return "ERROR: Could not find readable article content in the page"

    return markdown


@tool
def fetch_url_as_markdown(url: str) -> str:
    """
    Fetch an HTTP or HTTPS URL, remove navigation, ads, scripts and layout noise,
    extract the main article content, convert it to Markdown, and return up to
    100K characters of clean text.

    Use this tool when the user pastes a URL or asks you to analyze a web page.
    """

    settings = get_settings()
    return fetch_url_as_markdown_impl(
        url,
        timeout_seconds=settings.request_timeout_seconds,
        max_chars=settings.max_markdown_chars,
    )
