---
name: istatistik-profesoru
description: Bu skill, bir veri seti üzerinde istatistiksel analiz yapıp iki kapsamlı rapor üretmek gerektiğinde kullanılmalıdır: (1) uzman yorumlu detaylı analiz raporu, (2) Python teknik kodu raporu. Kullanıcı bir veri seti paylaştığında; "analiz yap", "istatistiksel test", "gruplar arasında fark var mı", "korelasyon", "regresyon", "ANOVA", "t-testi", "anlamlı mı" gibi ifadeler kullandığında tetiklenir. Veri analizi, hipotez testi, değişkenler arası ilişki, grup karşılaştırması veya tahmin modeli istendiğinde de kullanılır — kullanıcı "analiz" kelimesini açıkça kullanmasa bile. Bu skill "İstatistik Profesörü"dür; kullanıcı "istatistik profesörü" dediğinde de bu skill kullanılır.
version: 1.1
---

# istatistik-profesörü
*Statistics Professor (İstatistik Profesörü)*

A skill that performs comprehensive statistical analysis and reporting when a dataset is shared. Trigger conditions are listed in the frontmatter `description` above.

## Automatic language detection

If the input document is primarily written in Turkish, use `references/turkish-style.md`.
If it is primarily written in English, use `references/english-style.md`.
If the user does not specify a language, always assume Turkish.

Whenever a `.docx` file is created or updated, apply the spelling and punctuation rules
from the language-appropriate style file above, in addition to the number/percent/p-value
rules in "Step 4.5". This covers TDK/journal spelling, capitalization, punctuation spacing,
and comparison-symbol spacing.

**Revision highlighting (MANDATORY):** whenever an **existing** `.docx` file is UPDATED,
write all inserted or modified text in **red font color (RGB 255, 0, 0)** so the user can
immediately see what changed. Unchanged text keeps its original color. Newly created
documents use normal black text. python-docx: `run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)`.

## Process

### Step 1 — Gather Information After the Data Arrives

Before starting the analysis, ask the user:

> "I have a few questions before starting the analysis:
> 1. Which variable(s) do you want to work on? (e.g., age, income, treatment group)
> 2. What type of analysis are you aiming for? (e.g., between-groups difference, relationship/correlation, prediction)
> 3. What are your dependent and independent variables?"

Do not proceed to the analysis before the user responds.

---

### Step 2 — Dataset Preliminary Inspection

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data.csv")  # or the appropriate format
print(df.shape, df.dtypes, df.describe(), df.isnull().sum(), sep="\n")
```

Scope of inspection: number of observations and variables; variable types (continuous,
categorical, ordinal, binary); missing-data ratio and pattern; suspected outliers (IQR or
z-score); basic statistics (min, max, mean, median, std).

**Missing-data policy (state it explicitly in Report 1):** report the missing ratio per
variable. Below ~5% missing and no visible pattern, listwise deletion is acceptable — say so.
Above that, or when missingness looks related to another variable, do not silently drop rows:
tell the user, and state which option was taken (listwise deletion, pairwise deletion, or
imputation). Never impute without telling the user.

---

### Step 3 — Assumption Checks

**Normality:**
```python
from scipy import stats
from statsmodels.stats.diagnostic import lilliefors

stat, p = stats.shapiro(df['variable'])          # default; valid up to n = 5000
stat, p = lilliefors(df['variable'], dist='norm')  # alternative for large n
```
- Shapiro-Wilk is the default normality test.
- If a Kolmogorov-Smirnov-family test is preferred, use the **Lilliefors** variant, which
  estimates the mean and SD from the data.
- **Never use `stats.kstest(x, 'norm')` on raw data** — it compares against the *standard*
  normal N(0,1) and rejects almost any unstandardized clinical variable (age, blood pressure, BMI).
- Support the decision with a Q-Q plot and histogram; check skewness (−2 to +2) and kurtosis (−7 to +7).

**Homogeneity of variance (between-groups comparisons only):**
```python
stat, p = stats.levene(group1, group2)
```

**Two separate decisions — do not merge them:**

| Check | Result | Consequence |
|---|---|---|
| Normality (or clear outliers) | violated | Switch to the **non-parametric** test |
| Levene (variance homogeneity) | violated | Stay parametric, switch to **Welch's** t-test / Welch's ANOVA |

Levene failure alone never justifies a non-parametric test.

---

### Step 4 — Test Selection

Use the decision table below. For the full decision tree — including agreement (Kappa, ICC,
Bland-Altman), diagnostic tests/ROC, risk measures (RR, OR, NNT) and every effect-size
threshold — follow `references/test-secim-rehberi.md`; it is self-contained.

| Situation | Condition | Test | Non-parametric alternative |
|---|---|---|---|
| 2 independent groups | Normal, variances homogeneous | Student's t-test | Mann-Whitney U |
| 2 independent groups | Normal, variances heterogeneous | **Welch's t-test** | Mann-Whitney U |
| 2 dependent groups | Paired differences normal | Paired t-test | Wilcoxon signed-rank |
| 3+ independent groups | Normal (default choice) | **Welch's ANOVA** → Games-Howell | Kruskal-Wallis → Dunn (Bonferroni) |
| 3+ independent groups | Normal + Levene p>0.05 | One-way ANOVA → Tukey HSD | Kruskal-Wallis → Dunn |
| 3+ dependent groups | Normal; check sphericity (Mauchly) | rmANOVA (Greenhouse-Geisser if violated) | Friedman → Durbin-Conover |
| 2 continuous variables | Both normal | Pearson correlation | Spearman / Kendall |
| Categorical × Categorical | ≥80% of cells have expected count ≥5 and none <1 | Pearson chi-square | Fisher's exact |
| 2 dependent categorical | Paired 2×2 | McNemar | — |
| Continuous prediction | Linear relationship | Linear regression | — |
| Binary outcome prediction | — | Logistic regression | — |

Briefly explain to the user the selected test and **why it was chosen**.

**Multiplicity:** when several tests are run on the same dataset (a common thesis pattern),
state the number of comparisons and say whether an alpha correction was applied. For planned
post-hoc comparisons use the correction bound to the primary test (see the table above). For
many exploratory tests, either apply Bonferroni/Holm or explicitly label the results as
exploratory and uncorrected — do not leave it unstated.

---

### Step 4.5 — Numeric Value Formatting Rules (MANDATORY)

These rules apply to both reports, all tables, and any separate Word/PDF output.

1. **Mean ± SD:** one space before and after `±` → `28.03 ± 5.04`, never `28.03±5.04`.

2. **Confidence intervals and median (IQR):** normal parentheses `(...)`, never square
   brackets; an **en-dash (–)** with a space on each side between the bounds.
   - Correct: `(-5.359 – -0.662)`, `1.00 (0.30 – 2.50)`
   - Wrong: `[-5.36, -0.66]`, `[0.30-2.50]`

3. **Decimals:** effect/difference estimates and CI bounds → **3 decimals** (`-0.673`);
   descriptive statistics (mean, SD, median, quartiles) → 2 decimals; p-values → 3 decimals,
   written `<0.001` when smaller.

4. **Decimal separator and percent — language-dependent.** The percentage carries **exactly
   1 decimal**; leave a space before a unit.
   - **Turkish:** comma separator, `%` **before** the number, commas everywhere including p →
     `%73,5`, `36 (%73,5)`, `28,03 ± 5,04`, `25,9 ± 4,16 kg/m²`, `p=0,028`.
   - **English:** period separator, `%` **after** the number → `73.5%`, `36 (73.5%)`, `p=0.028`.
   - In Python: `f"%{p:.1f}".replace('.', ',')` for Turkish, `f"{p:.1f}%"` for English.
     Never produce two-decimal percentages.

5. **Spacing around operators:**
   - p-values and test statistics: **no space** → `p<0.001`, `p=0.028`, `(p>0.05)`.
   - Measurement thresholds: **one space** → `BMI > 30 kg/m²`, `Wo ≥ 4 mm`.

6. **Italic p:** write the symbol as `*p*` in Markdown and `.docx` output. `scripts/md_to_pdf.py`
   converts `*...*` to italic, so the italics survive into the PDF.

7. **p-value in running text:**
   - Significant (p<0.05): name the variable and give the 3-decimal value (`p=0.028`, or `p<0.001`).
   - Non-significant: do not list values one by one; group them as `(p>0.05)`.
   - **In tables the p-value is always the original 3-decimal value — never abbreviated**, including
     non-significant ones.

**Example:**
```
Difference (95% CI): -0.673 (-1.848 – 0.502)
Mean ± SD: 28.03 ± 5.04
Median (IQR): 1.00 (0.30 – 2.50)
```

In Python f-strings use `:.3f` (CI/difference) and `:.2f` (descriptives); never emit
square-bracket/comma patterns such as `[{lo:.2f}, {hi:.2f}]`.

**Test-name footnote symbols (MANDATORY):** add the symbol of the test used next to each
p-value in a results table, and write the legend for the symbols **actually used in that
table** as a footnote below it:

| Symbol | Test |
|---|---|
| * | Independent-samples Student's t-test |
| ** | Mann-Whitney U test |
| ‡ | Welch's t-test |
| † | Fisher's exact test |
| †† | Pearson's chi-square test |
| ††† | McNemar test |
| § | Paired-samples t-test |
| §§ | Wilcoxon signed-rank test |
| a | McNemar-Bowker test of symmetry |
| N/A | Not applicable |

**If a test is not on this list** (Kruskal-Wallis, ANOVA, Spearman, regression, Stuart-Maxwell …),
**do not reuse one of the existing symbols for it** — `‡` in particular belongs to Welch's t-test
only. Either propose a new symbol and tell the user, or name the test in words in the footnote.
Each table carries its own legend.

---

### Step 5 — Perform the Analyses (Python)

```python
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import pingouin as pg   # effect sizes and post-hoc: pg.compute_effsize, pg.pairwise_gameshowell
```

Use `pingouin` for effect sizes and post-hoc tests (`pg.compute_effsize(a, b, eftype='cohen')`,
`pg.pairwise_gameshowell`, `pg.welch_anova`) rather than hand-rolling the formulas. If pingouin
is not installed, say so and compute the effect size explicitly.

---

### Step 6 — Create and Save the Two Reports

Write the reports under the project root:

```
output/analiz/<veri-adı>/
├── Rapor1 YYYYAAGG SSDD.md    ← Detailed analysis report
├── Rapor1 YYYYAAGG SSDD.pdf
├── Rapor2 YYYYAAGG SSDD.md    ← Python technical report
├── Rapor2 YYYYAAGG SSDD.pdf
└── *.png                       ← charts, absolute paths when referenced
```

`<veri-adı>` is the data file name or a name given by the user. The `YYYYAAGG SSDD` suffix is
the **local** creation date-time (take it from `date` if unsure). Create the folder if missing
and tell the user the folder name before writing. When updating an existing report, keep its
original file name — the date tag is only added when a file is first created.

**PDF generation:** write each report as `.md` first, then convert.

Two rules prevent the recurring failures (missing images, Ş/Ğ shown as boxes):

1. Save every chart with an **absolute path** (`os.path.abspath`) and reference it in the
   markdown with that absolute path — `![caption](/abs/path/chart.png)`. A relative path breaks
   as soon as the converter runs from another working directory.
2. Never rely on a default font (Helvetica, LaTeX default, browser sans-serif); a font with
   Turkish coverage must be registered explicitly.

**Method 1 (preferred): `scripts/md_to_pdf.py`** — handles Turkish font registration, absolute
image resolution, pipe tables and inline `*italic*`/`**bold**`. No extra installation beyond reportlab.

```python
import sys, os
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from md_to_pdf import md_to_pdf

plt.savefig(os.path.join(OUT_DIR, "histogram_yas.png"), dpi=150, bbox_inches='tight')
# in the markdown: f"![Yaş histogramı]({os.path.join(OUT_DIR, 'histogram_yas.png')})"
md_to_pdf(rapor1_md, os.path.join(OUT_DIR, "Rapor1 20260725 0053.pdf"), md_dir=OUT_DIR)
```

It also runs standalone: `python md_to_pdf.py "Rapor1 ....md" "Rapor1 ....pdf"`.

**Method 2 (weasyprint, if installed):** `base_url` is mandatory so relative image paths resolve.
```python
from weasyprint import HTML
HTML(string=html, base_url=OUT_DIR).write_pdf(out_pdf)   # CSS: font-family: "Arial", "DejaVu Sans"
```

**Method 3 (pandoc, if installed):**
```python
subprocess.run(["pandoc", md_path, "-o", pdf_path, "--pdf-engine=xelatex",
                "-V", "mainfont=Arial", "--resource-path", OUT_DIR])
```

Try the methods in this order — reportlab first, because it needs no extra installation and is
the most reliable against Turkish-character and image problems. On failure print the error and
move to the next. If none work, name the missing tool and deliver the `.md`.

When PDF generation completes, give a one-line summary: which method was used and how many
images were embedded (e.g. "Rapor1 ... .pdf created — reportlab, 3 images embedded").

---

## REPORT 1: Detailed Analysis Report

*Written in the detected language (default: Turkish).*

1. **Dataset summary** — definition and size, variable descriptions and types, missing-data and outlier status.
2. **Analysis objective** — research question, H₀ / H₁, variables examined.
3. **Method** — selected test(s), assumption-check results (table + commentary), rationale for the choice.
4. **Results** — test statistic, degrees of freedom, p-value; effect size (Cohen's d / η² / r);
   confidence intervals; visuals (histogram, box plot, scatter, Q-Q, heatmap).
5. **Expert commentary** — statistical significance; practical/clinical significance from the effect
   size (Cohen's d: 0.2 / 0.5 / 0.8; η²: 0.01 / 0.06 / 0.14); interpretation; limitations (sample
   size, sampling method, multiplicity, missing data); recommendations and future directions.

---

## REPORT 2: Python Technical Report

*Written in the detected language (default: Turkish).*

1. **Libraries used** — table of library / purpose / step where used (pandas, numpy, scipy.stats,
   statsmodels, matplotlib, seaborn, pingouin).
2. **Step-by-step code flow** — for each step: its purpose, the function and parameters used, an
   annotated code block.
3. **Full runnable code** — the entire analysis start to finish as a single block, comments in the
   report's language, outputs interpreted, charts saved to `output/analiz/<veri-adı>/`.

---

## Important Notes

- Do not start the analysis before the data arrives; ask for the data first.
- Always report statistical significance (p-value) together with **practical significance** (effect size).
- If an assumption is violated, state it explicitly and take the correct branch — non-parametric for
  a normality violation, Welch for a variance violation (Step 3).
- Use `references/test-secim-rehberi.md` for test selection; it is self-contained. The PDFs in
  `assets/` are optional background lecture material only.
- Number/percent/p-value formatting and `.docx` spelling follow **Step 4.5** and the language style
  files — applies to every report table and Word/PDF output.
- To exercise the skill without user data, `scripts/generate_sample_data.py` writes three sample
  datasets (two-group, correlation, ANOVA); `references/evals.json` holds the four trigger scenarios
  these datasets correspond to.
