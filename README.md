# skillerim

A repository of my own Claude Code skills and subagents.

## Contents

| Path | What it does |
|---|---|
| _(moved out)_ | `bilim-klasoredit` and `bilim-s-pdf` left this repo on 25 July 2026. They now live in the **`klasoredit` plugin** (`plugin-klasoredit`), renamed `klasoreditbilim` and `klasoreditbilim-s-pdf`, alongside a second skill (`klasoreditplugin`) that enforces and audits plugin naming/sync rules. |
| [`skills/istatistik-profesoru/`](skills/istatistik-profesoru/) | A skill that performs statistical analysis on a shared dataset and produces two reports: an expert-commentary report + a Python technical code report. (Note: the 16 lecture-material PDFs under `assets/` present in the local copy were not included in this repo for copyright reasons.) |
| [`third-party/caveman/`](third-party/caveman/) | **Not written by me** — a personal archive copy of the [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) plugin (MIT license) that I actively use. Detail: [`VENDORED.md`](third-party/caveman/VENDORED.md). |

## Installation

To use a file, copy the relevant `.md` file into your own `~/.claude/skills/` or `~/.claude/agents/` folder.
