# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Static HTML class materials published to GitHub Pages. The publishable site
lives entirely under `docs/` (plain HTML/CSS/JS, no build step); `main.py` is
only a local preview server for that directory. Supporting Python/R code may
prepare assets that the HTML includes, but it is not deployed as site code.

- Deployed site: <https://qmakescl.github.io/class-material/>
- Deploy trigger: pushes to `main` touching `docs/` or the Pages workflow run
  `.github/workflows/deploy-pages.yml` (also runnable manually from Actions).
  One-time setup requirement: repo **Settings → Pages → Build and
  deployment → Source** must be **GitHub Actions**.

## Commands

Python/package commands must go through `uv`, never bare `python`/`pip`.

```sh
uv sync                              # sync the .venv (Python >=3.12, see .python-version)
uv run python main.py                # preview docs/ at http://127.0.0.1:8000
uv run python main.py --port 8080    # preview on a different port/host (--host)
uv run python -m compileall -q main.py  # syntax-check after editing main.py
uv add <package>                     # add a runtime dependency
uv add --dev <package>                # add a dev dependency
uv remove <package>                  # remove a dependency
```

`uv.lock` is generated — update it via `uv` commands, never edit by hand. In
sandboxes without access to the default uv cache path, prefix commands with
`UV_CACHE_DIR=/tmp/class-material-uv-cache`.

No test suite or linter/formatter is configured yet. If tests are added,
`pytest` is the intended dev dependency; don't impose a formatter that isn't
already set up.

## Architecture

- `docs/index.html` — the single page's content.
- `docs/assets/styles.css` — shared styling.
- `docs/assets/` — images and other attachments referenced by the page.
- `main.py` — `ThreadingHTTPServer` + `SimpleHTTPRequestHandler` bound to
  `docs/`, purely for local preview; it is not part of the deployed site and
  has no bearing on how GitHub Pages serves the content.
- `src/python/` — standalone Python scripts for preprocessing or generating
  assets for HTML. This is deliberately **not** a Python package: do not add
  `__init__.py` or package scaffolding.
- `src/R/` — R scripts for preprocessing or generating assets for HTML.
- `datasets/` — source datasets needed by scripts in `src/python/` or
  `src/R/`. Keep these outside `docs/`; generated publishable assets belong
  under an appropriate `docs/` subdirectory.

Because the site can be served from a GitHub Pages *project* subpath (not
domain root), all internal links and asset references in `docs/` must be
relative paths — never root-absolute (`/...`) paths.

## Working conventions (from AGENTS.md)

This repo is jointly maintained with Codex; `AGENTS.md` is the shared
source of truth and applies repo-wide (a more specific `AGENTS.md` in a
subdirectory would take precedence there, though none currently exists).
Key points not already covered above:

- Only touch files relevant to the request; preserve existing user changes.
- New Python code should favor 3.12 syntax and the standard library.
- Put standalone Python work in `src/python/` and R work in `src/R/`; use
  repository-relative paths to inputs in `datasets/` and outputs in `docs/`.
- Add a short docstring/comment for public functions or non-obvious logic.
- Never commit secrets, API keys, per-user env files, or `.venv`.
- When adding a new run method or user-facing behavior, update `README.md`
  too.
- After site changes, run the local preview server and confirm the HTML
  pages and key static assets respond correctly.
- After changing a Python script under `src/python/`, syntax-check that
  script (and run it with its required data when practical). After changing
  an R script under `src/R/`, check it with the available R runtime; report
  an unavailable runtime explicitly.
- Before the final response for a material file creation or change, follow
  `AI_LOGGING.md`: append the request, response summary, work performed,
  changed files, and verification result to an independent
  `ai-logs/tasks/YYYY/MM/YYYY-MM-DD-NN.md` file, then add one summary row to
  `ai-logs/daily/YYYY/MM/YYYY-MM-DD.md`. Do not log read-only questions,
  explanations, or reviews without repository changes. Never record secrets,
  private reasoning, or raw tool output.
