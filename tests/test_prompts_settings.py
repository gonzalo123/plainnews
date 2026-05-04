from lib.prompts import SYSTEM_PROMPT, build_rewrite_prompt
from settings import Settings, default_bedrock_model_id


def test_build_rewrite_prompt_contains_url() -> None:
    prompt = build_rewrite_prompt("https://example.com/news")

    assert "https://example.com/news" in prompt
    assert "available tool" in prompt
    assert "Write the full answer in English." in prompt


def test_build_rewrite_prompt_accepts_output_language() -> None:
    prompt = build_rewrite_prompt("https://example.com/news", language="Spanish")

    assert "Write the full answer in Spanish." in prompt


def test_system_prompt_uses_requested_output_language() -> None:
    assert "requested by the user" in SYSTEM_PROMPT
    assert "requested output language" in SYSTEM_PROMPT


def test_default_model_id() -> None:
    assert default_bedrock_model_id() == "global.anthropic.claude-sonnet-4-6"


def test_settings_resolves_default_model() -> None:
    settings = Settings()

    assert settings.resolved_bedrock_model_id == "global.anthropic.claude-sonnet-4-6"
