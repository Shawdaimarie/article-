# Contributing to Article

Thanks for considering a contribution. Article is a small project on
purpose — the goal is a charter and engine that stay legible, not one that
grows without bound.

## Development setup

```bash
git clone https://github.com/Shawdaimarie/article-.git
cd article-
python -m venv .venv && source .venv/bin/activate
pip install -e ".[api,dev]"
pytest
```

## Before opening a pull request

1. Run `pytest` — all tests must pass.
2. Run `article check .` against the repo itself — it should still score
   100/100 against its own charter. If your change legitimately requires a
   new exception, update `principles/article.yaml` **and**
   `src/article/data/article.yaml` together (a test enforces they stay in
   sync).
3. Update `CHANGELOG.md` under an `## [Unreleased]` heading.

## Proposing a new principle

Principles are meant to be few, durable, and checkable — not a wishlist.
Open an issue first describing:

- the principle in one sentence,
- why it's durable (not tied to one framework, language, or trend),
- what a concrete, automatable check for it would look like.

## Code style

- Python 3.10+, type hints on public functions.
- No new runtime dependencies without discussion — the CLI is meant to stay
  fast to install.
- Every new check in `src/article/checks.py` needs unit tests in
  `tests/test_checks.py` covering its pass, fail, and (if applicable) skip
  paths.

By contributing, you agree your contributions will be licensed under this
project's [MIT License](LICENSE).
