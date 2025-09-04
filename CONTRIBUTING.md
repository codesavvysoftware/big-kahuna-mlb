# Contributing

Thanks for helping improve Big Kahuna!

## Getting Started
1) Install deps (Pipenv preferred):
```bash
pipenv install
pipenv install XlsxWriter

Run a smoke test:

pipenv run python big_kahuna.py --help

Branch & PR

Create feature branches from main: feat/<short-name> or fix/<short-name>.

Open a PR with a clear description, sample run (command + output snippet), and note any new flags.

Code Style

Python 3.10+.

Prefer small, pure functions; avoid global state where possible.

Keep I/O (API calls, CSV/Excel) separated from modeling logic.

If adding a new metric or tab, include a docstring and a short README note.

Testing (lightweight)

Add a tiny fixture or mock where possible (e.g., a one-game schedule JSON).

At minimum, ensure --help runs and the script can run with a dummy DK CSV.

Adding Inputs (park, bullpen, wRC+)

Add or update dictionaries in one place (or configs/), include a comment with the source & date.

Versioning

Keep CHANGELOG in the PR description or a ## [Unreleased] section in README.

Code of Conduct

Be respectful. No harassment or discrimination. Disagreements are fine; personal attacks aren’t.