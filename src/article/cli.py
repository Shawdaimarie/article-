from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from article import __version__
from article.engine import load_charter, run

console = Console()

STATUS_STYLE = {"pass": "bold green", "fail": "bold red", "skip": "dim"}
STATUS_SYMBOL = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}


@click.group()
@click.version_option(__version__, prog_name="article")
def main():
    """Article: check a project against a machine-readable charter of engineering principles."""


@main.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
@click.option("--charter", "charter_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None, help="Use a custom charter YAML instead of the built-in one.")
@click.option("--json", "as_json", is_flag=True, help="Print machine-readable JSON instead of a table.")
@click.option("--min-score", type=float, default=0.0, help="Exit non-zero if the overall score is below this threshold.")
@click.option("--report-url", default=None, help="Article backend URL to report this run to, e.g. https://article.onrender.com")
@click.option("--api-key", default=None, help="Bearer token for --report-url, if the backend requires one.")
@click.option("--project-name", default=None, help="Project name to report under (defaults to the target directory's name).")
def check(path: Path, charter_path: Path | None, as_json: bool, min_score: float, report_url: str | None, api_key: str | None, project_name: str | None):
    """Run the charter against PATH (defaults to the current directory)."""
    result = run(path.resolve(), charter_path=charter_path)

    if as_json:
        click.echo(json.dumps(result.to_dict(), indent=2))
    else:
        table = Table(title=f"{result.charter_name} v{result.charter_version} — {path.resolve()}")
        table.add_column("Status", width=6)
        table.add_column("Principle")
        table.add_column("Detail")
        for r in result.results:
            table.add_row(f"[{STATUS_STYLE[r.status]}]{STATUS_SYMBOL[r.status]}[/]", r.title, r.message)
        console.print(table)
        console.print(f"\nScore: [bold]{result.score}[/bold]/100  "
                      f"({result.passed} passed, {result.failed} failed, {result.skipped} skipped)")

    if report_url:
        from article.client import report_run
        name = project_name or path.resolve().name
        try:
            report_run(report_url, name, result, api_key=api_key)
            if not as_json:
                console.print(f"[dim]Reported run for '{name}' to {report_url}[/dim]")
        except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
            console.print(f"[yellow]Warning: failed to report run to {report_url}: {exc}[/yellow]", err=True)

    if result.score < min_score:
        sys.exit(1)


@main.command(name="principles")
@click.option("--charter", "charter_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
def list_principles(charter_path: Path | None):
    """List every principle in the charter."""
    charter = load_charter(charter_path)
    table = Table(title=f"{charter['name']} v{charter['version']}")
    table.add_column("ID", overflow="fold", no_wrap=True)
    table.add_column("Title")
    table.add_column("Statement")
    for p in charter["principles"]:
        table.add_row(p["id"], p["title"], p["statement"].strip())
    # A dedicated wide console for this table: IDs are meant to be copy-pasted
    # (e.g. into --charter overrides), so they must never be truncated with "…".
    Console(width=max(console.width, 120)).print(table)


if __name__ == "__main__":
    main()
