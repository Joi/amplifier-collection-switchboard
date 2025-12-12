"""Unified personal workflow CLI.

Usage:
    do daily          - Generate daily note
    do gtd inbox      - Show GTD inbox
    do pres list      - List presentations
    do read list      - Show reading queue
    do knowledge gaps - Run gap detection
    do repos status   - Check repo status
"""

import click

from .daily import daily
from .gtd import gtd
from .pres import pres
from .reading import read
from .knowledge import knowledge
from .repos import repos


@click.group()
@click.version_option()
def cli():
    """Personal workflow CLI.
    
    Unified access to daily notes, GTD, presentations, reading queue,
    knowledge management, and repository sync.
    """
    pass


# Register subcommands
cli.add_command(daily)
cli.add_command(gtd)
cli.add_command(pres)
cli.add_command(read)
cli.add_command(knowledge)
cli.add_command(repos)


if __name__ == "__main__":
    cli()
