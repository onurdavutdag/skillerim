# skillerim

A repository of my own Claude Code skills and subagents.

## Contents

| Path | What it does |
|---|---|
| [`skills/bilim-klasoredit/`](skills/bilim-klasoredit/) | A skill that reduces a "Bilim ..." project folder to 6 top categories (the literal folder names: Introduction, Materyal-Method, Result, Discussion-Conclusion, the project-specific 5th category, Diğer). |
| [`agents/bilim-s-pdf.md`](agents/bilim-s-pdf.md) | A subagent that renames article PDFs to a Vancouver-style pattern (`YYYY LastName. Journal Name. Title.pdf`) — called by `bilim-klasoredit`. |
| [`skills/istatistik-profesoru/`](skills/istatistik-profesoru/) | A skill that performs statistical analysis on a shared dataset and produces two reports: an expert-commentary report + a Python technical code report. (Note: the 16 lecture-material PDFs under `assets/` present in the local copy were not included in this repo for copyright reasons.) |
| [`third-party/caveman/`](third-party/caveman/) | **Not written by me** — a personal archive copy of the [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) plugin (MIT license) that I actively use. Detail: [`VENDORED.md`](third-party/caveman/VENDORED.md). |

## Installation

To use a file, copy the relevant `.md` file into your own `~/.claude/skills/` or `~/.claude/agents/` folder.
