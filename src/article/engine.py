"""Loads the Article charter and runs it against a target project."""
from __future__ import annotations

import importlib.resources
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from article.checks import REGISTRY


@dataclass
class CheckResult:
    id: str
    title: str
    status: str  # "pass", "fail", or "skip"
    message: str
    weight: int = 1


@dataclass
class RunResult:
    charter_name: str
    charter_version: str
    results: list[CheckResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        scored = [r for r in self.results if r.status != "skip"]
        if not scored:
            return 100.0
        earned = sum(r.weight for r in scored if r.status == "pass")
        possible = sum(r.weight for r in scored)
        return round(100 * earned / possible, 1)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "fail")

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == "skip")

    def to_dict(self) -> dict:
        return {
            "charter_name": self.charter_name,
            "charter_version": self.charter_version,
            "score": self.score,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "results": [
                {"id": r.id, "title": r.title, "status": r.status, "message": r.message, "weight": r.weight}
                for r in self.results
            ],
        }


def load_charter(charter_path: Path | None = None) -> dict:
    if charter_path is not None:
        return yaml.safe_load(charter_path.read_text(encoding="utf-8"))
    data = importlib.resources.files("article").joinpath("data/article.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(data)


def run(target: Path, charter_path: Path | None = None) -> RunResult:
    charter = load_charter(charter_path)
    run_result = RunResult(charter_name=charter["name"], charter_version=charter["version"])

    for principle in charter["principles"]:
        check_fn = REGISTRY.get(principle["check"])
        if check_fn is None:
            outcome_status, outcome_message = "fail", f"No implementation registered for check '{principle['check']}'."
        else:
            outcome = check_fn(target)
            outcome_status, outcome_message = outcome.status, outcome.message

        run_result.results.append(
            CheckResult(
                id=principle["id"],
                title=principle["title"],
                status=outcome_status,
                message=outcome_message,
                weight=principle.get("weight", 1),
            )
        )

    return run_result
