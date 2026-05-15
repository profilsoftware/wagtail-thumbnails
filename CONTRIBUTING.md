# Contributing

Thanks for your interest in improving wagtail-thumbnails. This is a small library — bug fixes, documentation tweaks, and small features are all welcome.

## Setup

```bash
git clone https://github.com/kmsky/wagtail-thumbnails
cd wagtail-thumbnails
uv sync --extra dev
uv run pre-commit install
```

## Running checks

```bash
uv run pytest                  # tests
uv run ruff check .            # lint
uv run ruff format --check .   # formatting
uv run mypy src/               # type-checking
```

## Pull requests

- Open an issue first for non-trivial changes so we can agree on scope.
- Keep PRs focused. One change per PR.
- Add tests for new behaviour. Aim for the existing coverage level.
- Update `CHANGELOG.md` under `[Unreleased]`.
- Don't bump the version in your PR — the maintainer handles releases.

## Reporting issues

Please include:

- `wagtail-thumbnails` version
- Python, Django, Wagtail, DRF versions
- A minimal repro (settings + code snippet + expected vs. actual behaviour)
