# Statistical Test Selection Guide

**This guide is self-contained.** It carries every decision rule, assumption check,
effect-size threshold, interpretation cut-off, and reporting template needed to pick
and report a statistical test. You do **not** need to open the PDF lectures in
`assets/` — those are optional background only. Numbers follow the English convention
(period as decimal separator, `%` after the number), matching the skill's formatting rules.

---

## Step-by-Step Test Selection Algorithm

### Step 1 — Define the goal

```
What is the goal?
├── Compare groups           → Step 2
├── Relationship/correlation → Correlation section
├── Assess agreement         → Agreement section
├── Diagnostic performance   → Diagnostic Tests section
└── Measure risk             → Risk Measures section
```

### Step 2 — Determine the variable type

```
Type of the variable being compared?
├── Continuous / Ordinal     → Step 3
└── Nominal / Categorical    → Nominal Tests section
```

### Step 3 — Number of groups and their relationship

```
How many groups, independent or dependent?
├── 2 independent groups     → Step 4A
├── 2 dependent groups       → Step 4B
├── 3+ independent groups    → Step 4C
└── 3+ dependent groups      → Step 4D
```

### Step 4A — 2 Independent Groups (Continuous/Ordinal)

```
Normality (Shapiro-Wilk) + Outliers (box plot)?
├── Normal + NO outliers
│   ├── Variances homogeneous (Levene p>0.05) → Student's t-test
│   └── Variances heterogeneous               → Welch's t-test
└── Non-normal OR outliers present            → Mann-Whitney U
```

### Step 4B — 2 Dependent Groups (Continuous/Ordinal)

```
Normality of the paired differences (Shapiro-Wilk)?
├── Normal distribution → Paired-samples t-test
└── Non-normal          → Wilcoxon signed-rank test
```

### Step 4C — 3+ Independent Groups (Continuous/Ordinal)

```
Normality + Outliers?
├── Normal + NO outliers        → Welch's ANOVA → Post-hoc: Games-Howell
├── Non-normal OR
│   outliers present            → Kruskal-Wallis → Post-hoc: Dunn (Bonferroni)
├── Severe outliers             → Robust ANOVA (trimmed means + bootstrap)
└── Ordinal data                → Kruskal-Wallis (report medians)
```

### Step 4D — 3+ Dependent Groups / Repeated Measures (Continuous/Ordinal)

```
Normality + Outliers?
├── Normal (N>30 or SW p>0.05) → Repeated-measures ANOVA (rmANOVA)
│   ├── Sphericity holds (Mauchly p>0.05)  → Standard rmANOVA
│   └── Sphericity violated                → Greenhouse-Geisser correction
│   Post-hoc: Bonferroni
└── Non-normal OR N<30 OR outliers present → Friedman test
    Post-hoc: Durbin-Conover (Holm) or Dunn
```

---

## Comparing Groups — Details, Assumptions & Reporting

### 2 Independent Groups

**Assumptions to check, in order**
1. **Normality** within each group — Shapiro-Wilk (preferred for n < 50), Kolmogorov-Smirnov (n ≥ 50), plus a Q-Q plot. Assumption holds when p > 0.05.
2. **Outliers** — box plot / IQR. Even with normal data, clear outliers push you to Mann-Whitney U.
3. **Homogeneity of variance** — Levene's test. Only decides between Student's (p > 0.05) and Welch's (p ≤ 0.05) t-test; it does not affect the parametric-vs-nonparametric choice.

**Test → effect size**
| Test | Effect size | Small / Medium / Large |
|---|---|---|
| Student's / Welch's t-test | Cohen's d | 0.2 / 0.5 / 0.8 |
| Mann-Whitney U | Rank-biserial r | 0.1 / 0.3 / 0.5 |

**Descriptive to report:** mean ± SD for t-tests; median (IQR) for Mann-Whitney U.

**Reporting template (English):**
> Age differed significantly between groups (48.6 ± 15.8 vs 41.2 ± 12.4 years; Student's t-test, t(72)=2.31, p=0.024, Cohen's d=0.54).

### 2 Dependent Groups (paired / repeated on the same subject)

- Check normality of the **paired differences** (not the raw values).
- Normal → paired-samples t-test (effect size: Cohen's d on the differences).
- Non-normal → Wilcoxon signed-rank test (effect size: matched-pairs rank-biserial r).
- Examples: before/after treatment in the same patient, left vs right measurement.

### 3+ Independent Groups

- **Welch's ANOVA is the recommended default** when data are normal, because it does not assume equal variances and loses little power when they happen to be equal. Post-hoc: **Games-Howell** (does not assume equal variances).
- Classic one-way ANOVA (equal-variance) is acceptable when Levene p > 0.05; post-hoc Tukey HSD (equal group sizes) or Bonferroni (small samples).
- Non-normal or outliers → **Kruskal-Wallis**; post-hoc **Dunn** with Bonferroni correction; report medians (IQR).
- Severe outliers → **Robust ANOVA** (trimmed means + bootstrap).

**Effect sizes:** eta-squared η² for ANOVA (small 0.01, medium 0.06, large 0.14); epsilon-squared ε² for Kruskal-Wallis.

### 3+ Dependent Groups / Repeated Measures

- Normal → **rmANOVA**. Check **sphericity** with Mauchly's test; if violated (p ≤ 0.05), apply the **Greenhouse-Geisser** correction to the degrees of freedom. Post-hoc: pairwise t-tests with Bonferroni. Effect size: partial η².
- Non-normal, N < 30, or outliers → **Friedman test**. Post-hoc: Durbin-Conover (Holm) or Dunn. Effect size: **Kendall's W** (0 = no agreement, 1 = complete).

---

## Nominal/Categorical Tests

```
Categorical variable — how many groups, independent?
├── 2 independent groups (2x2 table)
│   ├── Cells with expected count ≥5 make up >80%  → Chi-square
│   └── Cells with expected count <5 make up >20%   → Fisher's exact
├── 2 dependent groups (paired/matched)             → McNemar test
├── 3+ independent groups (larger table)            → Chi-square (r×c)
│   If significant → pairwise Chi-square + Bonferroni (α = 0.05/k)
└── 3+ dependent groups                             → Cochran's Q test
```

**Expected-count rule (Cochran's rule):** the chi-square approximation is valid when
no cell has an expected count below 1 and at least 80% of cells have expected counts ≥ 5.
For a 2×2 table this reduces to "use Fisher's exact if any expected count < 5."

**Effect size for association**
| Table | Effect size | Interpretation |
|---|---|---|
| 2×2 | Phi (φ) | 0.1 small · 0.3 medium · 0.5 large |
| larger than 2×2 | Cramér's V | depends on df; roughly 0.1 small · 0.3 medium · 0.5 large |

**Footnote symbols** (per the skill's mandatory legend): `††` Pearson's chi-square,
`†` Fisher's exact, `†††` McNemar. Cochran's Q and r×c chi-square are not in the fixed
legend — name them in words or assign a new footnote symbol and define it under the table.

---

## Correlation

```
Variable types?
├── Continuous + Continuous
│   ├── Both normally distributed        → Pearson (r)
│   └── At least one non-normal/ordinal  → Spearman (rho)
├── Continuous + Dichotomous             → Point-biserial correlation
├── Nominal + Nominal                    → Phi (2x2) or Cramér's V (>2x2)
└── Ordinal + Ordinal                    → Spearman (rho)
```

**Interpreting the correlation coefficient (r or rho):**

| Value | Interpretation |
|---|---|
| < 0.20 | No / very weak relationship |
| 0.20 – 0.39 | Weak |
| 0.40 – 0.59 | Moderate |
| 0.60 – 0.79 | Strong |
| ≥ 0.80 | Very strong |

Always report the coefficient with its p-value and n; correlation is not causation, and
a coefficient can be inflated by outliers — inspect the scatter plot before trusting it.

---

## Risk Measures

```
Study design?
├── Prospective / cohort / RCT     → Risk Ratio (RR)
└── Retrospective / case-control   → Odds Ratio (OR)
```

**Why the design decides:** in case-control studies RR depends entirely on the (arbitrary)
number of controls sampled, whereas OR is invariant to it — so OR is the measure to report
for case-control designs. When the outcome is rare, OR ≈ RR.

**2×2 layout** (rows = exposure/treatment, columns = outcome):

| | Outcome present | Outcome absent |
|---|---|---|
| **Exposed** | a | b |
| **Not exposed** | c | d |

- Risk in exposed = a / (a+b); risk in unexposed = c / (c+d); **RR** = the ratio of the two.
- Odds in exposed = a / b; odds in unexposed = c / d; **OR** = the ratio of the two.
- **ARR** (absolute risk reduction) = |risk_unexposed − risk_exposed|.
- **RRR** (relative risk reduction) = 1 − RR.
- **NNT** (number needed to treat) = 1 / ARR (round up to the next whole patient).

**Interpretation**
- RR/OR > 1 (and 95% CI entirely > 1): exposure **increases** the outcome.
- RR/OR < 1 (and 95% CI entirely < 1): exposure **decreases** the outcome (protective).
- RR/OR = 1, **or the 95% CI includes 1.0**: no statistically significant association — do not claim an increase or decrease.
- Report RRR alongside ARR/NNT: RRR alone hides the baseline risk (a 25% relative reduction can be a 5% or a 0.02% absolute reduction). Risk-measure calculators do not produce a p-value; judge significance from whether the 95% CI crosses 1.0.

---

## Diagnostic Tests

Compare an **index test** against a **reference (gold) standard** in a 2×2 table
(rows = index test result, columns = true disease status):

| | Disease present | Disease absent |
|---|---|---|
| **Test positive** | TP (a) | FP (b) |
| **Test negative** | FN (c) | TN (d) |

**Four-fold table measures**
- **Sensitivity** = TP / (TP + FN) — of the truly diseased, the fraction the test catches (high sensitivity → good for ruling out).
- **Specificity** = TN / (TN + FP) — of the truly healthy, the fraction the test clears (high specificity → good for ruling in).
- **PPV** = TP / (TP + FP); **NPV** = TN / (TN + FN). Both depend on disease **prevalence**, so their transferability across settings is limited.
- **PLR** = Sensitivity / (1 − Specificity); **NLR** = (1 − Sensitivity) / Specificity. Likelihood ratios are prevalence-independent and are the preferred way to summarize how a result shifts pre-test to post-test probability — report LRs rather than relying on PPV/NPV.

**ROC analysis** (for a continuous/ordinal index test)
- The ROC curve dichotomizes at every possible cut-off; the hypothesis test compares the **AUC** against 0.5 (chance).
- AUC interpretation: **0.5 = no discrimination (chance)**, ~0.7–0.8 acceptable, ~0.8–0.9 excellent, **1.0 = perfect**.
- **Optimal cut-off:** commonly the point maximizing Youden's index (sensitivity + specificity − 1). After choosing it, dichotomize the data at that value and report the full four-fold metrics (Sens, Spec, PPV, NPV, PLR, NLR) at that threshold.
- A precondition for a meaningful ROC of a marker between two groups is that the marker actually differs between those groups.
- **Comparing two AUCs (two tests):** use **DeLong's test**.

Report AUC with its 95% CI, e.g. `AUC = 0.914 (95% CI: 0.85 – 0.97)`.

---

## Agreement Assessment

```
Variable type?
├── Categorical (2+ raters/methods) → Cohen's Kappa (2 raters) / Fleiss' Kappa (3+ raters)
│                                      Weighted Kappa for ordered categories
└── Continuous (2+ raters/methods)
    ├── Consistency of raters → ICC (Intraclass Correlation Coefficient)
    │   ├── Systematic differences unimportant → Consistency model
    │   └── Systematic differences important    → Absolute-agreement model
    └── New method vs a gold standard → Bland-Altman analysis
```

**Cohen's Kappa** measures agreement **beyond chance** for categorical (e.g. present/absent)
ratings. It is a consistency (not accuracy) measure: 1 = perfect agreement, 0 = no better
than chance, negative = worse than chance. Interpretation (Landis-Koch):

| Kappa | Agreement |
|---|---|
| < 0.20 | Poor / slight |
| 0.21 – 0.40 | Fair |
| 0.41 – 0.60 | Moderate |
| 0.61 – 0.80 | Substantial (good) |
| 0.81 – 1.00 | Almost perfect |

**ICC** — for numeric ratings by 2+ raters. Choose the model deliberately:
- **One-way vs two-way random effects:** two-way random is the most common (same raters assess every subject, e.g. clinicians at one center).
- **Consistency vs absolute agreement:** use *absolute agreement* when systematic differences between raters matter (multiple raters); use *consistency* when they can be ignored.
- Prefer the **Average measures** value when the mean of several raters will be used in practice; **Single** for a single-rater use case.
- Interpretation (Koo-Li): < 0.50 poor · 0.50–0.75 moderate · 0.75–0.90 good · > 0.90 excellent.

**Bland-Altman** — for agreement between a new method and a gold standard on a numeric variable.
- Preconditions: (1) numeric variable, (2) one method is the reference standard (not two new methods), (3) the **paired differences are normally distributed** (check with Shapiro-Wilk on the computed difference).
- Plots the difference of the two methods against their mean.
- Reports the **mean bias** and the **95% limits of agreement (LoA)** = mean bias ± 1.96 × SD of the differences.
- Bland-Altman gives **no p-value**: the clinician decides whether the bias and the LoA are clinically acceptable.
- Not for repeated measures (before/after), not for more than two methods, not for non-normal differences (use Passing-Bablok there).
- Reporting: `mean bias 0.004 (95% LoA: -1.212 – 1.220)`.

---

## Descriptive Statistics — Reporting Rules

| Variable type | Reported statistic |
|---|---|
| Continuous, normal distribution | Mean ± SD |
| Continuous, non-normal / ordinal | Median (IQR) |
| Nominal / categorical | n (%) |

**Normality criterion:** Shapiro-Wilk p > 0.05 **AND** skewness between −2 and +2 **AND**
kurtosis between −7 and +7. Use Shapiro-Wilk for n < 50 and Kolmogorov-Smirnov for n ≥ 50,
supported by a Q-Q plot and histogram.

---

## Post-hoc Summary

| Primary test | Post-hoc test | Correction |
|---|---|---|
| Welch's ANOVA | Games-Howell | — |
| One-way ANOVA (equal variance) | Tukey HSD / Bonferroni | built-in / Bonferroni |
| Kruskal-Wallis | Dunn | Bonferroni |
| rmANOVA | Pairwise t-test | Bonferroni |
| Friedman | Durbin-Conover | Holm |
| r×c Chi-square | Pairwise Chi-square | Bonferroni (α = 0.05/k) |

---

## Effect Size Quick Reference

| Test | Effect size | Small | Medium | Large |
|---|---|---|---|---|
| Student's / Welch's / paired t-test | Cohen's d | 0.2 | 0.5 | 0.8 |
| Mann-Whitney U / Wilcoxon | Rank-biserial r | 0.1 | 0.3 | 0.5 |
| ANOVA | Eta-squared η² | 0.01 | 0.06 | 0.14 |
| Kruskal-Wallis | Epsilon-squared ε² | 0.01 | 0.06 | 0.14 |
| Friedman | Kendall's W | 0.1 | 0.3 | 0.5 |
| Chi-square (2×2) | Phi φ | 0.1 | 0.3 | 0.5 |
| Chi-square (r×c) | Cramér's V | 0.1 | 0.3 | 0.5 |
| Correlation | r / rho | 0.20–0.39 weak, 0.40–0.59 moderate, 0.60–0.79 strong, ≥0.80 very strong |

---

## Source lectures

This guide distills the following Jamovi teaching decks (in `assets/`), by G. Aksel,
H. Akoğlu, and Ş. K. Çorbacıoğlu: two-group numeric comparison, ANOVA /
Kruskal-Wallis, rmANOVA and Friedman, nominal comparisons (2-group and multi-group),
correlation types, risk measures, diagnostic tests / ROC, and agreement (Kappa, ICC,
Bland-Altman). The decision rules and thresholds above are self-contained — consult the
PDFs only if you want the original worked examples.
