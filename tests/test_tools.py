import requests

from plainnews.settings import Settings
from plainnews.lib.tools import (
    clean_html_to_markdown,
    fetch_url_as_markdown,
    fetch_url_as_markdown_impl,
    is_supported_url,
)


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_extracts_article_and_removes_noise() -> None:
    html = """
    <html>
      <body>
        <nav>Subscribe now</nav>
        <article>
          <h1>You won't believe what happened</h1>
          <p>The city council approved the budget on Monday.</p>
          <script>alert("noise")</script>
          <div class="advertisement">Buy stuff</div>
        </article>
      </body>
    </html>
    """

    markdown = clean_html_to_markdown(html)

    assert "# You won't believe what happened" in markdown
    assert "The city council approved the budget on Monday." in markdown
    assert "Subscribe now" not in markdown
    assert "Buy stuff" not in markdown
    assert "alert" not in markdown


def test_falls_back_to_main_before_body() -> None:
    html = """
    <html>
      <body>
        <p>Body noise</p>
        <main><p>Main story content</p></main>
      </body>
    </html>
    """

    markdown = clean_html_to_markdown(html)

    assert "Main story content" in markdown
    assert "Body noise" not in markdown


def test_falls_back_to_body_when_no_main_or_article() -> None:
    html = "<html><body><p>Only body content</p></body></html>"

    markdown = clean_html_to_markdown(html)

    assert "Only body content" in markdown


def test_truncates_long_markdown() -> None:
    html = f"<html><body><main><p>{'x' * 200}</p></main></body></html>"

    markdown = clean_html_to_markdown(html, max_chars=50)

    assert len(markdown) < 80
    assert "[Content truncated]" in markdown


def test_fetch_returns_clear_error_for_bad_url() -> None:
    result = fetch_url_as_markdown_impl("not-a-url")

    assert result == "ERROR: URL must start with http:// or https://"


def test_fetch_handles_request_error(monkeypatch) -> None:
    def fake_get(*args, **kwargs):
        raise requests.Timeout("too slow")

    monkeypatch.setattr("plainnews.lib.tools.requests.get", fake_get)

    result = fetch_url_as_markdown_impl("https://example.com/article")

    assert result.startswith("ERROR: Could not fetch URL:")
    assert "too slow" in result


def test_fetch_converts_successful_response(monkeypatch) -> None:
    def fake_get(*args, **kwargs):
        return FakeResponse("<html><body><article><p>Hello news</p></article></body></html>")

    monkeypatch.setattr("plainnews.lib.tools.requests.get", fake_get)

    result = fetch_url_as_markdown_impl("https://example.com/article")

    assert "Hello news" in result


def test_tool_uses_configured_fetch_settings(monkeypatch) -> None:
    calls = {}
    settings = Settings(request_timeout_seconds=3, max_markdown_chars=42)

    def fake_fetch(url: str, *, timeout_seconds: int, max_chars: int) -> str:
        calls["url"] = url
        calls["timeout_seconds"] = timeout_seconds
        calls["max_chars"] = max_chars
        return "Configured markdown"

    monkeypatch.setattr("plainnews.lib.tools.get_settings", lambda: settings)
    monkeypatch.setattr("plainnews.lib.tools.fetch_url_as_markdown_impl", fake_fetch)

    result = fetch_url_as_markdown("https://example.com/article")

    assert result == "Configured markdown"
    assert calls == {
        "url": "https://example.com/article",
        "timeout_seconds": 3,
        "max_chars": 42,
    }


def test_supported_url_validation() -> None:
    assert is_supported_url("https://example.com/article")
    assert is_supported_url("http://example.com/article")
    assert not is_supported_url("ftp://example.com/article")
    assert not is_supported_url("https:///missing-host")
