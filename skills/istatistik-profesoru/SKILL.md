---
name: istatistik-profesoru
description: Veri seti üzerinde istatistiksel analiz yapar ve iki kapsamlı rapor oluşturur: (1) uzman yorumlu detaylı analiz raporu, (2) Python teknik kodu raporu. Kullanıcı bir veri seti paylaştığında, "analiz yap", "istatistiksel test", "gruplar arasında fark var mı", "korelasyon", "regresyon", "ANOVA", "t-testi", "anlamlı mı" gibi ifadeler kullandığında bu skili mutlaka kullan. Veri analizi, hipotez testi, değişkenler arası ilişki, grup karşılaştırması veya tahmin modeli istendiğinde de tetikle — kullanıcı "analiz" kelimesini açıkça kullanmasa bile. Bu skill "İstatistik Profesörü"dür; kullanıcı "istatistik profesörü" dediğinde de bu skili kullan.
---

# istatistik-profesörü
*Statistics Professor (İstatistik Profesörü)*

A skill that performs comprehensive statistical analysis and reporting when a dataset is shared. Trigger conditions are listed in the frontmatter `description` above.

## Automatic language detection

If the input document is primarily written in Turkish, use:

references/turkish-style.md

If the input document is primarily written in English, use:

references/english-style.md

If the user does not specify a language, always assume Turkish.

Whenever a `.docx` file is created or updated, always apply the spelling and
punctuation rules from the language-appropriate style file above (Turkish →
turkish-style.md, English → english-style.md), in addition to the number/percent/
p-value formatting rules in "Step 4.5". This covers TDK/journal spelling,
capitalization, punctuation spacing, and comparison-symbol spacing.

**Revision highlighting (MANDATORY):** whenever an **existing** `.docx` file is
UPDATED, all inserted or modified text must be written in **red font color
(RGB 255, 0, 0)** so the user can immediately see what changed. Unchanged text
keeps its original color. Newly created documents (not updates) use normal
black text. python-docx: `run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)`.

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
print(df.shape)
print(df.dtypes)
print(df.describe())
print(df.isnull().sum())
```

Scope of inspection:
- Number of observations (rows) and variables (columns)
- Variable types: continuous, categorical, ordinal, binary
- Missing-data ratio and distribution
- Suspected outliers (IQR method or z-score)
- Basic statistics (min, max, mean, median, std)

---

### Step 3 — Assumption Checks

**Normality:**
```python
from scipy import stats

stat, p = stats.shapiro(df['variable'])  # n < 50
stat, p = stats.kstest(df['variable'], 'norm')  # n >= 50
```
- Shapiro-Wilk: preferred for n < 50
- Kolmogorov-Smirnov: for n ≥ 50
- Visual check with Q-Q plot and histogram

**Homogeneity of Variance (for between-groups comparisons):**
```python
stat, p = stats.levene(group1, group2)
```

**Evaluation criterion:** p > 0.05 → assumption holds, p ≤ 0.05 → assumption violated → non-parametric test

---

### Step 4 — Test Selection

Use the decision table below. For detailed selection, follow `references/test-secim-rehberi.md` — it is self-contained.

| Situation | Condition | Parametric Test | Non-parametric Alternative |
|---|---|---|---|
| 2 independent groups | Normal + homogeneous variance | Independent t-test | Mann-Whitney U |
| 2 dependent groups | Normal | Paired t-test | Wilcoxon signed-rank |
| 3+ independent groups | Normal + homogeneous variance | One-way ANOVA | Kruskal-Wallis |
| 3+ dependent groups | Normal | Repeated-measures ANOVA | Friedman |
| 2 continuous variables | Normal | Pearson correlation | Spearman / Kendall |
| Categorical × Categorical | Expected frequency ≥ 5 | Chi-square | Fisher's Exact |
| Continuous prediction | Linear relationship | Linear regression | — |
| Binary outcome prediction | — | Logistic regression | — |

**Post-hoc (after ANOVA):**
- Tukey HSD: equal group sizes
- Bonferroni: small sample
- Games-Howell: unequal variance

Briefly explain to the user the selected test and **why it was chosen**.

---

### Step 4.5 — Numeric Value Formatting Rules (MANDATORY)

In all reports (report1, report2), tables, and any separate Word/PDF outputs, the following formatting rules are **always** followed. These rules are mandatory for consistency with academic/thesis-format tables:

1. **Mean ± Standard Deviation:** leave **a space before and after** the `±` sign.
   - Correct: `28.03 ± 5.04`
   - Wrong: `28.03±5.04`

2. **Confidence intervals and median (IQR) notation:** do **not** use square brackets `[...]`; instead use normal parentheses `(...)` with an **en-dash (–)** between the lower and upper bounds, leaving a space before and after the dash (–).
   - Correct: `(-5.359 – -0.662)`, for median `1.00 (0.30 – 2.50)`
   - Wrong: `[-5.36, -0.66]`, `[0.30-2.50]`

3. **Number of decimal places:**
   - Difference/effect estimate (point estimate) and the lower/upper bounds of the confidence interval: **3 places after the decimal** (e.g., `-0.673`, `-1.848`, `0.502`).
   - Descriptive statistics (mean, standard deviation, median, quartiles): 2 places is sufficient (e.g., `28.03 ± 5.04`).
   - p-values: 3 places (e.g., `0.013`); if smaller than 0.001, written as `<0.001`.

4. **Decimal separator and percent (%) notation — language-dependent (TDK / international journals):** the percentage value is written with **exactly 1 decimal** place; leave a space before the unit.
   - **In Turkish reports:** decimal separator is a **comma**; the `%` sign goes **before** the number. **All numbers, including p, use a comma.** E.g., `%73,5`, `36 (%73,5)`, `28,03 ± 5,04`, `25,9 ± 4,16 kg/m²`.
   - **In English reports:** decimal separator is a **period**; the `%` sign goes **after** the number. E.g., `73.5%`, `36 (73.5%)`, `28.03 ± 5.04`, `25.9 ± 4.16 kg/m²`.
   - In Python, format the percentage with `:.1f`; for Turkish `f"%{p:.1f}".replace('.', ',')`, for English `f"{p:.1f}%"`. Do not produce two-decimal percentages.

5. **p-value notation in text (commentary):**
   - Decimal separator is **language-dependent**: a **comma** in Turkish reports (`p=0,028`, `p<0,001`), a **period** in English reports (`p=0.028`, `p<0.001`).
   - **p < 0.05 (significant):** name the relevant variable and write the p-value in its **original 3-decimal** form (e.g., `p=0.028`; if smaller than 0.001, `p<0.001`).
   - **p > 0.05 (non-significant):** do **not** write the 3-decimal value; indicate non-significant variables collectively with `(p>0.05)`.
   - This abbreviation (p>0.05) is only for text/commentary. **In tables, the p-value is always given in its original 3-decimal form — it is never abbreviated, including for non-significant (p>0.05) ones.**

**Example — full format:**
```
Difference (95% CI): -0.673 (-1.848 – 0.502)
Mean ± SD: 28.03 ± 5.04
Median (IQR): 1.00 (0.30 – 2.50)
```

These rules apply both in the tables of Markdown/PDF reports and, if requested, in the separately produced Word (.docx) tables. When formatting f-strings in Python code, use `:.3f` (for CI/difference) and `:.2f` (for descriptive statistics); never produce square-bracket/comma patterns such as `[{lo:.2f}, {hi:.2f}]`.

**Test-name footnote symbols (MANDATORY):** In results tables, the following standard symbol indicating the test used is added next to the p-value; the legend for these symbols (only those actually used in that table) is written as a footnote below the table:

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

If a test not in this list is used, assign the next consistently available symbol and define it explicitly in the footnote — since a symbol's meaning may change from table to table, each table must carry its own legend.

---

### Step 5 — Perform the Analyses (Python)

Required libraries:
```python
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns
import pingouin as pg
```

---

### Step 6 — Create and Save the Two Reports

Save the reports to the `results/<data-name>/` folder in the project root:

```
results/
└── <data-name>/        ← the data file name or the name given by the user
    ├── report1.md      ← Detailed analysis report (Markdown)
    ├── report1.pdf     ← Detailed analysis report (PDF)
    ├── report2.md      ← Python technical report (Markdown)
    └── report2.pdf     ← Python technical report (PDF)
```

Create the folder if it does not exist. Tell the user the folder name before writing the files.

**PDF Generation:**

Write each report first as `.md`, then convert it to PDF.

**Critical rules (to prevent images from not loading and letters like Ş/Ğ appearing as boxes):**

1. **Images are always saved with an absolute path** (`os.path.abspath(...)`) and are referenced in the markdown with that absolute path as `![caption](absolute/path/chart.png)`. Do not use relative paths — if the PDF converter runs from a different working directory, the image reference breaks.
2. **A font with Turkish-character support is explicitly registered/specified.** In no method rely on the default font (Helvetica, LaTeX's default font, the browser's default sans-serif); these render characters like Ş, ş, Ğ, ğ, İ, ı as boxes (□).

**Method 1 (preferred): the `md_to_pdf` function with reportlab**

Use the following function as-is — it includes Turkish font registration and image-embedding support:

```python
import os

def md_to_pdf(md_text, out_path, md_dir=None):
    """md_dir: base folder for resolving relative image paths inside the markdown (if omitted, an absolute path is expected)."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                     Paragraph, Spacer, HRFlowable, Image)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import re

    # --- Register a font with Turkish-character support (cross-platform search) ---
    font_candidates = [
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),           # Windows
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),                    # Linux
        ("/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),                       # macOS
    ]
    F, FB = 'Helvetica', 'Helvetica-Bold'
    for reg, bold in font_candidates:
        if os.path.exists(reg) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont('TR', reg))
            pdfmetrics.registerFont(TTFont('TRB', bold))
            F, FB = 'TR', 'TRB'
            break
    if F == 'Helvetica':
        print("WARNING: No font with Turkish-character support found, using Helvetica — "
              "characters like Ş/Ğ/İ/ı may appear incorrectly.")

    H1 = ParagraphStyle('H1', fontName=FB, fontSize=13, spaceAfter=8, alignment=1,
                         textColor=colors.HexColor('#1F3864'))
    H2 = ParagraphStyle('H2', fontName=FB, fontSize=10, spaceAfter=4, spaceBefore=10,
                         textColor=colors.HexColor('#2E4DA0'))
    H3 = ParagraphStyle('H3', fontName=FB, fontSize=9, spaceAfter=3, spaceBefore=6,
                         textColor=colors.HexColor('#4472C4'))
    BODY = ParagraphStyle('B', fontName=F, fontSize=8.5, spaceAfter=3, leading=12)
    CODE = ParagraphStyle('C', fontName='Courier', fontSize=7.5, spaceAfter=4,
                           backColor=colors.HexColor('#F5F5F5'), leading=11)
    NOTE = ParagraphStyle('N', fontName=F, fontSize=7.5, textColor=colors.grey, spaceBefore=6)

    doc = SimpleDocTemplate(out_path, pagesize=landscape(A4),
                             leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=1.5*cm, bottomMargin=1.5*cm)
    elems = []
    page_w = landscape(A4)[0] - 3*cm

    in_code, code_buf = False, []
    table_rows, in_table = [], False
    img_count = 0

    def flush_table():
        nonlocal table_rows, in_table
        if not (in_table and table_rows):
            return
        col_count = max(len(r) for r in table_rows)
        col_w = [page_w / col_count] * col_count
        tbl_data = [[Paragraph(c.replace('**', ''), BODY) for c in tr] for tr in table_rows]
        tbl = Table(tbl_data, colWidths=col_w[:len(table_rows[0])], repeatRows=1)
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4DA0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FB),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (-1, -1), F),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EEF2FF')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        tbl.setStyle(TableStyle(cmds))
        elems.append(tbl)
        elems.append(Spacer(1, 0.3*cm))
        table_rows = []
        in_table = False

    for line in md_text.split('\n'):
        if line.strip().startswith('```'):
            if not in_code:
                in_code, code_buf = True, []
            else:
                in_code = False
                if code_buf:
                    elems.append(Paragraph('<br/>'.join(code_buf), CODE))
            continue
        if in_code:
            code_buf.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Image: ![caption](path)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if img_match:
            flush_table()
            alt, path = img_match.group(1), img_match.group(2)
            full_path = path if os.path.isabs(path) else os.path.join(md_dir or '', path)
            full_path = os.path.abspath(full_path)
            if os.path.exists(full_path):
                img = Image(full_path)
                ratio = min(page_w / img.drawWidth, 1.0)
                img.drawWidth *= ratio
                img.drawHeight *= ratio
                elems.append(img)
                elems.append(Spacer(1, 0.2*cm))
                img_count += 1
            else:
                elems.append(Paragraph(f"[Image not found: {path}]", NOTE))
            continue

        if line.startswith('|'):
            if '---' in line:
                continue
            table_rows.append([c.strip() for c in line.strip('|').split('|')])
            in_table = True
            continue
        else:
            flush_table()

        if line.startswith('# '):
            elems.append(Paragraph(line[2:], H1))
            elems.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#2E4DA0'), spaceAfter=6))
        elif line.startswith('## '):
            elems.append(Paragraph(line[3:], H2))
        elif line.startswith('### '):
            elems.append(Paragraph(line[4:], H3))
        elif line.startswith('> '):
            elems.append(Paragraph(line[2:], NOTE))
        elif line.startswith('- '):
            elems.append(Paragraph(f"• {line[2:]}", BODY))
        elif line.strip():
            elems.append(Paragraph(line, BODY))
        elif elems:
            elems.append(Spacer(1, 0.2*cm))

    flush_table()
    doc.build(elems)
    print(f"PDF created: {out_path} ({img_count} images embedded)")
    return True

# Usage — also use absolute paths when saving charts:
# plt.savefig(os.path.join(OUT_DIR, "histogram_age.png"), dpi=150, bbox_inches='tight')
# inside report1_md: f"![Age histogram]({os.path.join(OUT_DIR, 'histogram_age.png')})"
md_to_pdf(report1_md, os.path.join(OUT_DIR, "report1.pdf"), md_dir=OUT_DIR)
```

**Method 2 (if weasyprint is installed):**

```python
import subprocess

html = f"""<html><head><meta charset="utf-8">
<style>
  body {{ font-family: "Arial", "DejaVu Sans", "Liberation Sans", sans-serif; }}
  img {{ max-width: 100%; }}
</style></head><body>{markdown_to_html(report1_md)}</body></html>"""
# base_url is MANDATORY so relative image paths can be resolved:
from weasyprint import HTML
HTML(string=html, base_url=OUT_DIR).write_pdf(os.path.join(OUT_DIR, "report1.pdf"))
```

**Method 3 (if pandoc is installed on the system):**

```python
subprocess.run([
    "pandoc", "report1.md", "-o", "report1.pdf",
    "--pdf-engine=xelatex",
    "-V", "mainfont=Arial",       # mandatory for Turkish-character support
    "--resource-path", OUT_DIR,   # folder containing the images
])
```

Try the methods in this order (reportlab first, because it requires no extra installation and is the most reliable against Turkish/image issues). If a method fails, print the error and move on to the next. If none work, tell the user which tool is missing and continue with the `.md` file.

When PDF generation is complete, give the user a short summary: how many pages/images were produced and which method was used (e.g., "report1.pdf created — reportlab, 3 images embedded").

---

## REPORT 1: Detailed Analysis Report

*Written in the detected language (see "Automatic language detection"; default: Turkish).*

### 1. Dataset Summary
- Definition and size of the dataset
- Description and types of the variables
- Missing-data and outlier status

### 2. Analysis Objective
- Research question and hypothesis (H₀ / H₁)
- Variables examined

### 3. Method
- Selected test(s) and their explanation
- Assumption-check results (table + commentary)
- Rationale for test selection

### 4. Results
- Test statistic, degrees of freedom, p-value
- Effect size: Cohen's d / eta-squared (η²) / r
- Confidence intervals (if needed)
- Visuals: histogram, box plot, scatter plot, Q-Q plot, heatmap

### 5. Expert Commentary
- Statistical significance: interpretation of p < 0.05 / p < 0.01
- Practical/clinical significance: interpretation of effect size
  - Cohen's d: small=0.2, medium=0.5, large=0.8
  - η²: small=0.01, medium=0.06, large=0.14
- Interpretation and importance of the results
- Limitations (sample size, sampling method, etc.)
- Recommendations and future research directions

---

## REPORT 2: Python Technical Report

*Written in the detected language (see "Automatic language detection"; default: Turkish).*

### 1. Libraries Used

| Library | Purpose | Step Where Used |
|---|---|---|
| pandas | Data loading and manipulation | Data preprocessing |
| numpy | Numerical computation | All steps |
| scipy.stats | Statistical tests | Assumption checks + main tests |
| statsmodels | ANOVA, regression | Advanced analyses |
| matplotlib | Basic visualization | All charts |
| seaborn | Statistical visualization | Distribution and relationship charts |
| pingouin | Advanced statistics | Effect size, post-hoc |

### 2. Step-by-Step Code Flow

For each step:
- The purpose of the step
- The function and parameters used
- An annotated code block

### 3. Full Runnable Code

Python code that runs the entire analysis from start to finish, as a single block.
- Comments should be in the report's language
- Outputs should be interpreted
- Charts should be in a saveable format

---

## Important Notes

- Do not start the analysis before the data arrives; ask for the data first
- Always report statistical significance (p-value) together with **practical significance** (effect size)
- If an assumption is violated, state this explicitly and choose the non-parametric alternative
- Use `references/test-secim-rehberi.md` for test selection — it is self-contained; the PDFs in `assets/` are optional background only
- Number/percent/p-value formatting and `.docx` spelling/punctuation follow **Step 4.5** and "Automatic language detection" — applies to all report tables and Word/PDF outputs
