import os
from functools import lru_cache
from pathlib import Path

import boto3
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
ENV_FILE = BASE_DIR / "env" / ENVIRONMENT / ".env"

load_dotenv(dotenv_path=ENV_FILE)


class Settings(BaseSettings):
    aws_profile: str | None = Field(default=None, validation_alias="AWS_PROFILE")
    aws_region: str = Field(default="us-west-2", validation_alias="AWS_REGION")
    bedrock_model_id: str | None = Field(default=None, validation_alias="BEDROCK_MODEL_ID")
    request_timeout_seconds: int = Field(default=15, validation_alias="REQUEST_TIMEOUT_SECONDS")
    max_markdown_chars: int = Field(default=100_000, validation_alias="MAX_MARKDOWN_CHARS")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def resolved_bedrock_model_id(self) -> str:
        if self.bedrock_model_id:
            return self.bedrock_model_id

        return default_bedrock_model_id()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def resolve_settings(
    *,
    aws_profile: str | None = None,
    aws_region: str | None = None,
    bedrock_model_id: str | None = None,
) -> Settings:
    settings = get_settings()
    updates: dict[str, str | None] = {}

    if aws_profile:
        updates["aws_profile"] = aws_profile
    if aws_region:
        updates["aws_region"] = aws_region
    if bedrock_model_id:
        updates["bedrock_model_id"] = bedrock_model_id

    if not updates:
        return settings

    return settings.model_copy(update=updates)


def create_boto_session(settings: Settings) -> boto3.Session:
    kwargs: dict[str, str] = {}

    if settings.aws_profile:
        kwargs["profile_name"] = settings.aws_profile
    if settings.aws_region:
        kwargs["region_name"] = settings.aws_region

    return boto3.Session(**kwargs)


def default_bedrock_model_id() -> str:
    return "global.anthropic.claude-sonnet-4-6"
