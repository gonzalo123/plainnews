from functools import wraps

import click

from plainnews.lib.agent import create_agent
from plainnews.lib.prompts import build_rewrite_prompt
from plainnews.lib.tools import is_supported_url
from plainnews.lib.ui import get_console, print_result
from plainnews.settings import resolve_settings


def runtime_options(function):
    @click.option(
        "--aws-profile",
        default=None,
        help="AWS profile name to use. Falls back to AWS_PROFILE if unset.",
    )
    @click.option(
        "--region",
        default=None,
        help="AWS region for Bedrock. Falls back to AWS_REGION if unset.",
    )
    @click.option(
        "--model",
        default=None,
        help="Bedrock model id. Falls back to BEDROCK_MODEL_ID if unset.",
    )
    @click.option(
        "--language",
        default="English",
        show_default=True,
        help="Output language for the rewritten article.",
    )
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapper


@click.command(name="rewrite")
@click.argument("url")
@runtime_options
def rewrite_command(
    url: str,
    aws_profile: str | None,
    region: str | None,
    model: str | None,
    language: str,
) -> None:
    """Rewrite a news article from its URL."""

    if not is_supported_url(url):
        raise click.ClickException("URL must start with http:// or https://")

    settings = resolve_settings(
        aws_profile=aws_profile,
        aws_region=region,
        bedrock_model_id=model,
    )
    console = get_console()

    try:
        agent = create_agent(settings=settings)
        with console.status("Rewriting the article with Bedrock...", spinner="dots"):
            result = agent(build_rewrite_prompt(url, language=language))
    except Exception as error:
        raise click.ClickException(str(error)) from error

    print_result("PlainNews", str(result))
