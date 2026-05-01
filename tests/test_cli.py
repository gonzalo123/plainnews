from click.testing import CliRunner

from plainnews.cli import cli


class FakeAgent:
    def __call__(self, prompt: str) -> str:
        assert "https://example.com/article" in prompt
        return "# Clear headline\n\nA concise rewritten article."


def test_rewrite_rejects_non_http_url() -> None:
    result = CliRunner().invoke(cli, ["rewrite", "not-a-url"])

    assert result.exit_code != 0
    assert "URL must start with http:// or https://" in result.output


def test_rewrite_accepts_url_and_renders_result(monkeypatch) -> None:
    monkeypatch.setattr("plainnews.commands.rewrite.create_agent", lambda *, settings: FakeAgent())

    result = CliRunner().invoke(cli, ["rewrite", "https://example.com/article"])

    assert result.exit_code == 0
    assert "Clear headline" in result.output
    assert "concise rewritten article" in result.output
