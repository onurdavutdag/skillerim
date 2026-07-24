# bilim-klasoredit — User Guide

> ## ⚠️ MAINTENANCE RULE (read first)
> **This is a LIVING document.** When a section/rule is added to, changed in, or
> removed from the skill, or a new subagent is connected, this file is updated with
> the SAME change.
>
> _Last update: 2026-07-25 — description rewritten in third person (skill-reviewer
> standard); PDF-naming full rules de-duplicated (single source of truth = the
> subagent definition); an `examples/` worked before/after example was added._

---

## 1. Overview

`bilim-klasoredit` is a Claude Code skill that reduces any "Bilim ..." project folder
(e.g. Bilim Fare Tümör, Bilim Tez C2, Bilim Spinal Araknoid Kist Vaka
Sunumu) to 6 fixed top categories:
**Introduction, Materyal-Method, Result, Discussion-Conclusion,
(the project-specific 5th category), Diğer** (these are the literal folder names). The content is in Turkish. Trigger:
when the user says "6'lar kuralını uygula", "bu şekilde sınıflandır", "proje
klasörünü düzenle/sınıflandır".

When done, the root directory contains **exactly** these 6 numbered folders + `output/`
(a separate global CLAUDE.md rule) + `desktop.ini` (if present); no other loose
file/shortcut remains (it is moved to the 6th category). Rule detail: `SKILL.md`.

## 2. The subagent it calls: `bilim-s-pdf`

| Property | Value |
|---|---|
| Location | `~/.claude/agents/bilim-s-pdf.md` (independent, not wrapped in a plugin) |
| Tools | `Read, Glob, Bash` |
| When called | When a non-standard-named article PDF enters Introduction/Materyal-Method (optional), or when the user directly says "rename the PDFs"/"name in Vancouver style" |
| Purpose | Renames downloaded article PDFs to the `YYYY LastName. Journal Name. Title.pdf` pattern **in the same folder** |
| Input | The `*.pdf` files in a folder (or the specified ones) |
| Output | Renamed files + an old→new name table report |

**Naming rule (summary only):** Pattern `YYYY LastName. Journal Name. Title.pdf`
— journal name in **full** (not the NLM/PubMed abbreviation); `:` / subtitle em
dash → `.`; a **120-character** cap (drop the subtitle, then crop at a word
boundary); a `+` priority tag by the year keeps its prefix/suffix position; and
author/year/journal are **never fabricated** — unverifiable files are skipped.

**Full rule and step-by-step method live only in the subagent definition**
(`~/.claude/agents/bilim-s-pdf.md`) — the single source of truth. This README
intentionally does not duplicate the detailed edge cases (invalid-character list,
preprint-server names, middle-of-title `+` exception).

## 3. Red lines

- No loose file/folder outside the 6 categories is **left** in the root.
- A move is always rename/move, **not** copy-delete (to prevent OneDrive from re-uploading large
  files).
- `bilim-s-pdf` does **not touch the file content**, it only changes the name;
  it does not fabricate author/year/journal information.

## 4. Component inventory

| Type | Path |
|---|---|
| Skill instruction | `SKILL.md` |
| Guide (this file) | `README.md` |
| Worked example | `examples/bilim-fare-tumor-ornegi.md` |
| Subagent | `../../agents/bilim-s-pdf.md` |
