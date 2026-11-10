# Article

**A machine-readable charter of engineering principles, plus a CLI and
backend that actually check a project against it.**

[![CI](https://github.com/Shawdaimarie/article-/actions/workflows/ci.yml/badge.svg)](https://github.com/Shawdaimarie/article-/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Frameworks, languages, and models turn over every few years. What shouldn't
turn over is a small set of engineering values — transparency, security,
privacy, accessibility, honest licensing, human oversight of AI — that keep
a project trustworthy long after the tech stack underneath it is gone.
Article writes those values down as ten checkable principles and gives you a
tool that actually verifies them, instead of a document nobody rereads.

## Installation

```bash
git clone https://github.com/Shawdaimarie/article-.git
cd article-
pip install -e .
```

Or, for the backend/reporting features too:

```bash
pip install -e ".[api]"
```

## Usage

Run the charter against any project (defaults to the current directory):

```bash
article check .
```

```
       The Article Charter v1.0.0 — /path/to/your-project
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Status ┃ Principle                 ┃ Detail                            ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ PASS   │ Transparency              │ README.md documents usage...     │
│ FAIL   │ Security by Default       │ No secrets found, but SECURITY.md│
│  ...   │ ...                       │ ...                               │
└────────┴───────────────────────────┴───────────────────────────────────┘

Score: 90.0/100 (9 passed, 1 failed, 0 skipped)
```

Other useful flags:

```bash
article check . --json                  # machine-readable output
article check . --min-score 80          # exit 1 if below threshold (for CI)
article check . --report-url <api-url>  # send the result to a backend (see below)
article principles                      # list every principle and its statement
```

`article check` never executes anything from the project it's checking — it
only reads files. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for why
that matters and how the pieces fit together.

## The charter

Defined in [`principles/article.yaml`](principles/article.yaml), each
principle maps to a real, automatable check in
[`src/article/checks.py`](src/article/checks.py):

| Principle | What it checks |
| --- | --- |
| Transparency | A README exists and documents usage/installation |
| Licensing Hygiene | A recognizable OSI license is declared |
| Security by Default | No hardcoded secrets; a `SECURITY.md` exists |
| Privacy & Data Respect | If data collection is mentioned, a `PRIVACY.md` explains it |
| Human Oversight for AI | If AI/ML is used, a human-review step is documented |
| Accessibility | HTML declares a language and images carry alt text |
| Testing & Maintainability | Automated tests exist and CI runs them |
| Inclusive Community | `CODE_OF_CONDUCT.md` and `CONTRIBUTING.md` exist |
| Dependency Integrity | Dependencies are pinned or lockfiled, not open-ended |
| Sustainability & Longevity | `CHANGELOG.md` records versioned history |

This project runs its own charter in CI on every push and requires a
perfect score to pass — see the badge above.

## Responsible AI

This project was scaffolded with the help of an AI coding assistant, and its
own "Human Oversight for AI" principle applies to itself: every check result
Article produces is a starting point for **human review**, not a verdict to
apply blindly. A FAIL doesn't mean "bad project" — it means "a human should
look at this and decide if it matters here." The static checks are
deliberately conservative heuristics, not a legal or security audit.

## Reporting runs to a backend (optional)

The CLI works completely offline. If you want to track a score over time,
run the included backend (FastAPI + Postgres) and point the CLI at it:

```bash
article check . --report-url https://your-deployment.onrender.com
```

Deploy your own instance with one click using [`render.yaml`](render.yaml),
or run it locally:

```bash
pip install -e ".[api]"
uvicorn article.api.main:app --reload
```

See [`PRIVACY.md`](PRIVACY.md) for exactly what the backend stores (short
answer: a project name, a score, and per-principle results — nothing else).

## Development

```bash
pip install -e ".[api,dev]"
pytest
article check .   # should stay at 100/100
```

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) and the
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) — see the license file for the full text.

## Local review — November 2026

API history now requires ARTICLE_API_TOKEN (at least 32 characters). Set the same value as the CLI report API key; the dashboard accepts it in a password field and retains it only in memory. Use HTTPS behind a production gateway. Python 3.11+ is required. Scores must be finite and between 0 and 100, counts nonnegative, and list limits between 1 and 200.
