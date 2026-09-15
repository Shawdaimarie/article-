# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/);
versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-09-15

### Added

- The Article Charter: ten durable, machine-readable engineering principles
  (`principles/article.yaml`).
- `article` CLI (`check`, `principles` commands) with a real static-analysis
  implementation for every principle.
- Backend API (FastAPI + SQLAlchemy) that stores and serves charter-run
  history, plus a minimal HTML dashboard.
- Full test suite for checks, the scoring engine, the CLI, and the API.
- GitHub Actions CI running the test suite and dogfooding `article check .`
  against this repository on every push.
- `render.yaml` blueprint for one-click deployment of the backend + Postgres.
