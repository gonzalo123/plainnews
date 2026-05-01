import click

from plainnews.commands.rewrite import rewrite_command


@click.group()
def cli() -> None:
    """Rewrite clickbait news articles into clear Markdown."""


cli.add_command(rewrite_command)


if __name__ == "__main__":
    cli()
