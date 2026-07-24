# istatistik-profesoru — User Guide

> ## ⚠️ MAINTENANCE RULE (read first)
> **This is a LIVING document.** When a rule is added to, changed in, or removed from
> `SKILL.md` or any file under `references/` and `scripts/`, this file is updated with
> the SAME change.
>
> **Second rule, specific to this skill:** `SKILL.md`, `references/test-secim-rehberi.md`
> and the two style guides must never contradict each other. `test-secim-rehberi.md` is the
> single source of truth for **test selection**; `SKILL.md` Step 4.5 is the single source of
> truth for **number formatting**. When one changes, verify the others.
>
> _Last update: 2026-07-25 — statistical fixes (kstest removed, Levene→Welch branch corrected,
> Welch added to the decision table), formatting contradictions resolved across the style guides,
> the embedded PDF function moved to `scripts/md_to_pdf.py`, output path aligned with the global
> `output/` + date-tag rules._

---

## 1. Overview

`istatistik-profesoru` ("İstatistik Profesörü") is a Claude Code skill that runs a complete
statistical analysis on a shared dataset and delivers **two** reports:

1. **Rapor 1** — detailed analysis with expert commentary (assumptions, test choice, effect
   size, clinical interpretation, limitations).
2. **Rapor 2** — Python technical report (libraries, annotated step-by-step code, one runnable block).

Both are produced as `.md` **and** `.pdf`. Report language follows the input document
(Turkish by default).

**Trigger:** the user shares a dataset, or says "analiz yap", "istatistiksel test",
"gruplar arasında fark var mı", "korelasyon", "regresyon", "ANOVA", "t-testi", "anlamlı mı",
or "istatistik profesörü" — including cases where the word "analiz" never appears.

## 2. Output contract

```
output/analiz/<veri-adı>/
├── Rapor1 YYYYAAGG SSDD.md / .pdf
├── Rapor2 YYYYAAGG SSDD.md / .pdf
└── *.png
```

The date-time suffix is the local creation time and is added only when a file is **first**
created; updates keep the original name. Structural files of the skill itself
(`SKILL.md`, `README.md`, `scripts/*.py`) never carry a date tag.

## 3. Component inventory

| Type | Path | Role |
|---|---|---|
| Skill instruction | `SKILL.md` | Process (6 steps), decision table, mandatory formatting rules, report outlines |
| Guide (this file) | `README.md` | Overview + maintenance rule |
| Test selection | `references/test-secim-rehberi.md` | Self-contained decision tree: group comparison, correlation, risk measures, diagnostic/ROC, agreement (Kappa/ICC/Bland-Altman), effect sizes, post-hoc |
| Turkish style | `references/turkish-style.md` | TDK spelling/punctuation, comma decimals, `%` before the number |
| English style | `references/english-style.md` | Journal spelling/punctuation, period decimals, `%` after the number |
| Eval scenarios | `references/evals.json` | 4 trigger scenarios with their expected outputs |
| PDF converter | `scripts/md_to_pdf.py` | Markdown → PDF; Turkish font registration, absolute image paths, pipe tables, inline italic/bold. Importable **and** runnable as a CLI |
| Sample data | `scripts/generate_sample_data.py` | Writes 3 sample datasets (two-group, correlation, ANOVA) to `output/analiz/ornek-veri/` |
| Lecture material | `assets/*.pdf` | 15 Jamovi teaching decks — **optional background only**, never required. Excluded from the `skillerim` GitHub repo for copyright reasons |

No subagent is called. Dependencies: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`,
`seaborn`, `pingouin`, `reportlab` (optional: `weasyprint`, `pandoc`).

## 4. Red lines

- **Never** `scipy.stats.kstest(x, 'norm')` on raw data — it tests against N(0,1) and rejects
  almost any unstandardized clinical variable. Shapiro-Wilk is the default; Lilliefors is the
  KS-family alternative.
- A **Levene** failure means Welch, **not** a non-parametric test. Only a normality/outlier
  problem justifies going non-parametric.
- A footnote symbol is never reused for a test it does not belong to (`‡` = Welch's t-test only).
  Tests outside the fixed legend get a new symbol (with the user told) or are named in words.
- Significance is never reported without an effect size.
- Missing data is never imputed or dropped silently — the policy is stated in Rapor 1.
- An updated `.docx` carries its revisions in red (RGB 255, 0, 0).

## 5. Sync

The skill also lives in the `skillerim` GitHub repo
(`~/.claude/repos/skillerim/skills/istatistik-profesoru/`). Per the global CLAUDE.md rule, every
change here is pushed there in the same session. `assets/` is the documented exception — it stays
local only.
