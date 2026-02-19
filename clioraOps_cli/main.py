"""
Main CLI entry point for ClioraOps.
"""

import click
from pathlib import Path
from dotenv import load_dotenv
from clioraOps_cli.config.settings import resolve_mode
from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.version import __version__

# Load environment variables from .env file if it exists
# Try multiple locations
env_paths = [
    Path.cwd() / ".env",  # Current working directory
    Path(__file__).parent.parent / ".env",  # Project root
]

for env_file in env_paths:
    if env_file.exists():
        load_dotenv(env_file)
        break


@click.group()
@click.option(
    "--mode",
    type=click.Choice(["beginner", "architect"]),
    help="Force execution mode"
)
@click.pass_context
@click.version_option(version=__version__)
def cli(ctx, mode):
    """ClioraOps - DevOps Learning Companion"""
    
    resolved_mode = resolve_mode(mode)
    ctx.obj = ClioraOpsApp(resolved_mode)


# -------------------------
# INITIALIZE PROJECT
# -------------------------
@cli.command()
@click.argument("path", default=".")
@click.pass_obj
def init(app, path):
    """Initialize project and scan for secrets."""
    app.run("init", path)


# -------------------------
# START SESSION
# -------------------------
@cli.command()
@click.pass_obj
def start(app):
    """Start interactive session."""
    app.start()


# -------------------------
# REVIEW COMMAND
# -------------------------
@cli.command()
@click.argument("command", nargs=-1)
@click.pass_obj
def review(app, command):
    """Review a command or script for safety."""
    app.run("review", *command)


# -------------------------
# GENERATE COMMAND
# -------------------------
@cli.command()
@click.argument("args", nargs=-1)
@click.pass_obj
def generate(app, args):
    """Generate DevOps code/config."""
    app.run("generate", *args)


# -------------------------
# DESIGN / ARCHITECT
# -------------------------
@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument("args", nargs=-1)
@click.pass_obj
def design(app, args):
    """Design an architecture diagram."""
    app.run("design", *args)


def main():
    cli()


if __name__ == "__main__":
    main()
