# bilim-klasoredit — User Guide

> ## ⚠️ MAINTENANCE RULE (read first)
> **This is a LIVING document.** When a section/rule is added to, changed in, or
> removed from the skill, or a new subagent is connected, this file is updated with
> the SAME change.
>
> _Last update: 2026-07-21 — the skill name was changed to `bilim-klasoredit`;
> the subagent name was synchronized with `bilim-s-pdf`._

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

**Naming rule summary:**
- `YYYY` = publication/posted year, `LastName.` = only the first author's last name
  (ends with a period), `Journal Name.` = the journal's **full name** (ends with a
  period; not converted to the NLM/PubMed abbreviation; if a preprint server —
  Research Square, etc. — the server's name is used).
- In the title, `:` and the subtitle-separator em dash `—` → `.`; other Windows-invalid
  characters (`\ / * ? " < > |`) are cleaned.
- If the total name (including the extension, excluding the folder path) exceeds the default
  **120-character** limit: first the subtitle is dropped; if the subtitle is distinguishing
  information, the last word(s) are cropped at a word boundary instead (no ellipsis).
- If there is a `+` sign immediately before/after the year in the original filename
  (the user's priority/filter tag), its position (prefix/suffix) is preserved exactly in the new
  name — a `+` in the middle of the title (e.g. a scientific term)
  is not included in this rule.
- Author/year/journal information is **never fabricated without being verified** from the PDF text
  — a file that cannot be confirmed is skipped, and the user is notified.

Full rule and step-by-step method: in the subagent definition itself
(`~/.claude/agents/bilim-s-pdf.md`).

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
| Subagent | `../../agents/bilim-s-pdf.md` |
