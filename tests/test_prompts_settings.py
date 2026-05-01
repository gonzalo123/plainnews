from plainnews.lib.prompts import build_rewrite_prompt
from plainnews.settings import Settings, default_bedrock_model_id


def test_build_rewrite_prompt_contains_url() -> None:
    prompt = build_rewrite_prompt("https://example.com/news")

    assert "https://example.com/news" in prompt
    assert "available tool" in prompt


def test_default_model_id() -> None:
    assert default_bedrock_model_id() == "global.anthropic.claude-sonnet-4-6"


def test_settings_resolves_default_model() -> None:
    settings = Settings()

    assert settings.resolved_bedrock_model_id == "global.anthropic.claude-sonnet-4-6"
