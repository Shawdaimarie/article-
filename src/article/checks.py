"""Concrete, static-analysis implementations of each Article principle.

Every function takes the root of a target project and returns a
``CheckOutcome``. Checks never execute code from the target project — they
only read files — so running ``article check`` against an untrusted repo is
safe.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict

EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", "dist", "build", ".tox",
    "*.egg-info",
}
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz",
    ".woff", ".woff2", ".ttf", ".eot", ".so", ".dylib", ".dll", ".pyc",
    ".db", ".sqlite", ".sqlite3",
}
MAX_FILE_BYTES = 2 * 1024 * 1024


@dataclass
class CheckOutcome:
    status: str  # "pass", "fail", or "skip"
    message: str


def _iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.suffix.lower() in BINARY_EXTENSIONS:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _find_first(root: Path, names: list[str]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def transparency(root: Path) -> CheckOutcome:
    readme = _find_first(root, ["README.md", "README.rst", "README.txt", "README"])
    if readme is None:
        return CheckOutcome("fail", "No README found at the project root.")
    text = _read_text(readme)
    if len(text.strip()) < 300:
        return CheckOutcome("fail", f"{readme.name} exists but is too short to explain the project (< 300 chars).")
    lowered = text.lower()
    if not any(keyword in lowered for keyword in ("usage", "install", "getting started", "quickstart")):
        return CheckOutcome("fail", f"{readme.name} doesn't appear to document usage or installation.")
    return CheckOutcome("pass", f"{readme.name} documents the project with a usage/installation section.")


KNOWN_LICENSES = ("mit", "apache", "bsd", "gpl", "mpl", "isc", "unlicense")


def licensing_hygiene(root: Path) -> CheckOutcome:
    license_file = _find_first(root, ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"])
    if license_file is None:
        return CheckOutcome("fail", "No LICENSE file found at the project root.")
    text = _read_text(license_file).lower()
    if not any(name in text for name in KNOWN_LICENSES):
        return CheckOutcome("fail", f"{license_file.name} exists but doesn't match a recognizable OSI license.")
    return CheckOutcome("pass", f"{license_file.name} declares a recognizable license.")


SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Generic API key assignment", re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]")),
    ("Private key block", re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP|DSA) PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
]


def security_by_default(root: Path) -> CheckOutcome:
    hits = []
    for path in _iter_text_files(root):
        text = _read_text(path)
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(f"{path.relative_to(root)} (looks like: {label})")
    if hits:
        return CheckOutcome("fail", "Possible hardcoded secret(s) found: " + "; ".join(hits[:5]))
    if _find_first(root, ["SECURITY.md", ".github/SECURITY.md"]) is None:
        return CheckOutcome("fail", "No secrets found, but SECURITY.md is missing (no vulnerability reporting channel).")
    return CheckOutcome("pass", "No hardcoded secrets detected, and SECURITY.md documents how to report vulnerabilities.")


DATA_COLLECTION_PATTERN = re.compile(
    r"(?i)\b(collect(s|ing)?\s+(personal|user)\s+data|\bPII\b|analytics\.track|telemetry)\b"
)


def privacy_and_data_respect(root: Path) -> CheckOutcome:
    found_indicator = False
    for path in _iter_text_files(root):
        if DATA_COLLECTION_PATTERN.search(_read_text(path)):
            found_indicator = True
            break
    if not found_indicator:
        return CheckOutcome("skip", "No data-collection indicators found; principle not applicable.")
    if _find_first(root, ["PRIVACY.md"]) is None:
        return CheckOutcome("fail", "Data-collection language found, but no PRIVACY.md documents what is collected.")
    return CheckOutcome("pass", "Data-collection language found and PRIVACY.md documents the policy.")


AI_INDICATOR_PATTERN = re.compile(
    r"(?i)\b(LLM|large language model|GPT|machine learning|\bmodel\b|prompt engineering|\bAI\b)\b"
)
HUMAN_OVERSIGHT_PATTERN = re.compile(r"(?i)human[\s-]?(review|oversight|in[\s-]the[\s-]loop)")


def human_oversight_for_ai(root: Path) -> CheckOutcome:
    docs = [p for p in [_find_first(root, ["README.md"])] if p]
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        docs.extend(sorted(docs_dir.glob("*.md")))

    found_ai_indicator = any(AI_INDICATOR_PATTERN.search(_read_text(d)) for d in docs)
    if not found_ai_indicator:
        return CheckOutcome("skip", "No AI/ML indicators found in project docs; principle not applicable.")
    if any(HUMAN_OVERSIGHT_PATTERN.search(_read_text(d)) for d in docs):
        return CheckOutcome("pass", "AI/ML use is documented alongside a human oversight statement.")
    return CheckOutcome("fail", "AI/ML use is mentioned in docs, but no human oversight/review statement was found.")


def accessibility(root: Path) -> CheckOutcome:
    html_files = [p for p in _iter_text_files(root) if p.suffix.lower() in (".html", ".htm")]
    if not html_files:
        return CheckOutcome("skip", "No HTML files found; principle not applicable.")
    problems = []
    for path in html_files:
        text = _read_text(path)
        if not re.search(r"<html[^>]*\blang=", text, re.IGNORECASE):
            problems.append(f"{path.relative_to(root)}: missing lang= on <html>")
        for img_match in re.finditer(r"<img\b[^>]*>", text, re.IGNORECASE):
            if not re.search(r"\balt=", img_match.group(0), re.IGNORECASE):
                problems.append(f"{path.relative_to(root)}: <img> without alt=")
                break
    if problems:
        return CheckOutcome("fail", "; ".join(problems[:5]))
    return CheckOutcome("pass", f"All {len(html_files)} HTML file(s) declare a language and use alt text.")


def testing_and_maintainability(root: Path) -> CheckOutcome:
    test_dirs = [root / "tests", root / "test"]
    has_tests = any(
        d.is_dir() and any(d.rglob("test_*.py")) or d.is_dir() and any(d.rglob("*_test.py"))
        for d in test_dirs
    )
    has_ci = (root / ".github" / "workflows").is_dir() and any((root / ".github" / "workflows").glob("*.yml"))
    has_ci = has_ci or (root / ".gitlab-ci.yml").is_file() or (root / ".circleci" / "config.yml").is_file()
    if has_tests and has_ci:
        return CheckOutcome("pass", "Automated tests and a CI workflow are both present.")
    missing = []
    if not has_tests:
        missing.append("no test files under tests/")
    if not has_ci:
        missing.append("no CI workflow under .github/workflows/")
    return CheckOutcome("fail", "; ".join(missing))


def inclusive_community(root: Path) -> CheckOutcome:
    coc = _find_first(root, ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"])
    contributing = _find_first(root, ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"])
    if coc and contributing:
        return CheckOutcome("pass", "CODE_OF_CONDUCT.md and CONTRIBUTING.md are both present.")
    missing = [name for name, found in (("CODE_OF_CONDUCT.md", coc), ("CONTRIBUTING.md", contributing)) if not found]
    return CheckOutcome("fail", f"Missing: {', '.join(missing)}.")


def dependency_integrity(root: Path) -> CheckOutcome:
    pyproject = root / "pyproject.toml"
    requirements = root / "requirements.txt"
    package_json = root / "package.json"
    lockfiles = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock"]
    has_lockfile = any((root / lf).is_file() for lf in lockfiles)

    if pyproject.is_file():
        text = _read_text(pyproject)
        # Inspect each quoted string in isolation (rather than one regex spanning
        # the whole file) so that e.g. `version = "1.0.0"` on one line can never
        # be mistaken for the *next* line's `readme = "README.md"` entry.
        dep_line = re.compile(r'^([A-Za-z0-9_.\-]+(?:\[[A-Za-z0-9_,\-]+\])?)\s*([><=!~^].+)$')
        deps = []
        for quoted in re.findall(r'"([^"]*)"', text):
            match = dep_line.match(quoted)
            if match:
                deps.append((match.group(1), match.group(2)))
        unpinned = [name for name, spec in deps if "==" not in spec]
        if unpinned:
            return CheckOutcome("fail", f"pyproject.toml has unpinned dependencies: {', '.join(unpinned[:5])}")
        if deps:
            return CheckOutcome("pass", "All dependencies in pyproject.toml are pinned to exact versions.")

    if requirements.is_file():
        lines = [l.strip() for l in _read_text(requirements).splitlines() if l.strip() and not l.startswith("#")]
        unpinned = [l for l in lines if "==" not in l]
        if unpinned:
            return CheckOutcome("fail", f"requirements.txt has unpinned entries: {', '.join(unpinned[:5])}")
        if lines:
            return CheckOutcome("pass", "All entries in requirements.txt are pinned to exact versions.")

    if package_json.is_file():
        if has_lockfile:
            return CheckOutcome("pass", "package.json is backed by a lockfile.")
        return CheckOutcome("fail", "package.json has no accompanying lockfile.")

    return CheckOutcome("skip", "No recognized dependency manifest found; principle not applicable.")


def sustainability_longevity(root: Path) -> CheckOutcome:
    changelog = _find_first(root, ["CHANGELOG.md", "CHANGELOG", "CHANGELOG.rst"])
    if changelog is None:
        return CheckOutcome("fail", "No CHANGELOG found.")
    text = _read_text(changelog)
    if not text.strip() or not re.search(r"\d+\.\d+\.\d+", text):
        return CheckOutcome("fail", f"{changelog.name} exists but doesn't record versioned entries.")
    return CheckOutcome("pass", f"{changelog.name} records versioned history.")


REGISTRY: Dict[str, Callable[[Path], CheckOutcome]] = {
    "transparency": transparency,
    "licensing_hygiene": licensing_hygiene,
    "security_by_default": security_by_default,
    "privacy_and_data_respect": privacy_and_data_respect,
    "human_oversight_for_ai": human_oversight_for_ai,
    "accessibility": accessibility,
    "testing_and_maintainability": testing_and_maintainability,
    "inclusive_community": inclusive_community,
    "dependency_integrity": dependency_integrity,
    "sustainability_longevity": sustainability_longevity,
}
