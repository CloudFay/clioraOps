"""
Main CLI entry point for ClioraOps.
"""

import click
from clioraOps_cli.config.settings import resolve_mode
from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.version import __version__


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
    """Review a command for safety."""
    app.run("review", *command)


# -------------------------
# DESIGN / ARCHITECT
# -------------------------
@cli.command()
@click.argument("topic")
@click.pass_obj
def design(app, topic):
    """Design an architecture."""
    app.run("design", topic)


def main():
    cli()


if __name__ == "__main__":
    main()
