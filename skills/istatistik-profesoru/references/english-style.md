<!-- Güncelleme: 20260725 0053 -->

# English Medical Writing Style Guide (SCI/SCIE Journals)

Version: 1.1

This document defines the default writing style for all English medical
manuscripts unless the target journal specifies otherwise.

------------------------------------------------------------------------

# 1. Numbers

-   Use a period (.) as the decimal separator.
-   Use commas for thousands.

Correct: 48.6 25.9 1,245

Incorrect: 48,6 25,9

------------------------------------------------------------------------

# 2. Percentages

-   Place the percentage sign after the number.
-   No space between number and %.

Correct: 73.5% 12%

Incorrect: %73.5 73.5 %

------------------------------------------------------------------------

# 3. P values

-   Always use italic lowercase *p*.
-   Report to three decimal places.
-   Never write p=0.000.
-   Use p<0.001 for extremely small values.
-   Leave **no space** around the `=` and `<` signs of a p-value (see §9).

Correct:

*p*=0.248

*p*=0.037

*p*=0.999

*p*<0.001

Incorrect:

P=0.04

p=.04

p=0.000

p < 0.001

**Italic scope:** the italic *p* applies to Markdown and `.docx` output. The
reportlab PDF pipeline in `scripts/md_to_pdf.py` converts `*...*` to italic, so
write `*p*` in the Markdown source and it will survive into the PDF.

------------------------------------------------------------------------

# 4. Mean ± Standard Deviation

Correct:

48.6 ± 15.8 years

25.9 ± 4.16 kg/m²

------------------------------------------------------------------------

# 5. Median (IQR)

Use normal parentheses and an en-dash (–) with a space on each side. Never use
square brackets or a comma between the bounds.

Correct:

12.5 (8.2 – 16.7)

Median (IQR)

Incorrect:

12.5 [8.2-16.7]

12.5 (8.2, 16.7)

------------------------------------------------------------------------

# 6. Units

Use SI units.

Leave one space between number and unit.

Correct:

5 mm

20 cm

75 kg

180 mL

Incorrect:

5mm

20cm

75kg

Exception:

°C

%

------------------------------------------------------------------------

# 7. Statistical Symbols

Italicize statistical variables.

Correct:

*p*

*n*

*r*

*R²*

OR

RR

HR

CI

------------------------------------------------------------------------

# 8. Confidence Interval

Same notation as §5: normal parentheses, en-dash (–) with a space on each side.

Correct:

OR 2.31 (95% CI: 1.42 – 3.88)

Incorrect:

OR 2.31 [1.42-3.88]

OR 2.31 (95% CI 1.42, 3.88)

------------------------------------------------------------------------

# 9. Mathematical Symbols

Two distinct cases — do not mix them:

**a) Threshold / cut-off expressions on a measured variable:** leave one space
before and after the symbol.

Correct:

BMI ≥ 30 kg/m²

Wo < 4 mm

Age ≤ 65 years

Incorrect:

BMI≥30

Wo<4 mm

**b) p-values and other test statistics:** leave **no space** around `=` or `<`.
This is the canonical form for text, tables and figure legends alike.

Correct:

p<0.001

p=0.028

(p>0.05)

Incorrect:

p < 0.001

p = 0.028

------------------------------------------------------------------------

# 10. Table and Figure Citation

Correct:

(Table 1)

(Table 2)

(Figure 1)

(Figure 2)

Do not abbreviate unless required by the journal.

------------------------------------------------------------------------

# 11. Abbreviations

Define abbreviations at first mention.

Correct:

Body mass index (BMI)

Computed tomography (CT)

Magnetic resonance imaging (MRI)

Subsequent use:

BMI

CT

MRI

------------------------------------------------------------------------

# 12. Academic Tone

Use objective scientific language.

Preferred verbs:

demonstrated

showed

revealed

identified

observed

evaluated

assessed

compared

Avoid:

proved

obviously

clearly

remarkably

interestingly

------------------------------------------------------------------------

# 13. Voice

Use active voice whenever appropriate.

Preferred:

We evaluated 49 patients.

The screw was inserted successfully.

Avoid unnecessary passive constructions.

------------------------------------------------------------------------

# 14. Tense

Methods: Past tense

Results: Past tense

Discussion: Present tense for established knowledge. Past tense for
study findings.

------------------------------------------------------------------------

# 15. Numbers in Text

Spell out numbers one through nine when they are not measurements.

Examples:

Three patients

Eight surgeons

Use numerals for:

10 or greater

measurements

percentages

ages

statistical values

Correct:

8 patients

12 patients

5 mm

7 years

73.5%

------------------------------------------------------------------------

# 16. Lists

Use serial (Oxford) comma.

Correct:

brain, spine, and peripheral nerve surgery

------------------------------------------------------------------------

# 17. Hyphenation

Correct:

follow-up

preoperative

postoperative

well-defined

long-term

short-term

multicenter

single-center

------------------------------------------------------------------------

# 18. Common Medical Terminology

Correct:

postoperative

preoperative

follow-up

reoperation

screw placement

pedicle screw

pars-pedicle complex

------------------------------------------------------------------------

# 19. Results Section

Report facts only.

Do not interpret findings.

Correct:

The Wo ≥ 4 mm group demonstrated a significantly higher screw insertion
rate (*p*=0.012).

Incorrect:

This finding suggests that surgeons should always use larger screws.

------------------------------------------------------------------------

# 20. Discussion Section

Interpret findings.

Compare with previous literature.

Discuss limitations.

Avoid introducing new results.

------------------------------------------------------------------------

# 21. References to Tables/Figures

Correct:

(Table 2)

(Figure 3)

As shown in Figure 2...

------------------------------------------------------------------------

# 22. Spacing

One space after punctuation — never two, never zero.

Correct:

The mean age was 48.6 years. The BMI was...

Incorrect:

The mean age was 48.6 years.  The BMI was...

The mean age was 48.6 years.The BMI was...

------------------------------------------------------------------------

# 23. Common Formatting

Correct:

L4–L5

C2

95% CI

p<0.001

48.6 ± 15.8

OR 2.15

RR 1.42

------------------------------------------------------------------------

# 24. Avoid

Very

Quite

Really

Clearly

Obviously

Interestingly

Amazing

Remarkable (unless statistically justified)

------------------------------------------------------------------------

# 25. Preferred Reporting Style

Instead of:

There was a statistically significant difference.

Prefer:

The difference was statistically significant (*p*=0.021).

------------------------------------------------------------------------

# 26. Revision Highlighting in .docx Updates (MANDATORY)

When an **existing .docx file is updated** by applying the rules in this
style guide, every inserted or modified text segment MUST be written in
**red font color (RGB 255, 0, 0)** so the user can immediately see which
parts were revised.

-   Unchanged text keeps its original color.
-   Newly created documents (not updates) use normal black text.

python-docx implementation:

```python
from docx.shared import RGBColor
run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)  # updated text
```

------------------------------------------------------------------------

# 27. Final Checklist

✓ Decimal point

✓ Percent sign after number

✓ Italic *p*

✓ Three decimal places for *p*

✓ p<0.001 instead of p=0.000

✓ No space around the p-value operator (p<0.001), one space around measurement thresholds (BMI ≥ 30)

✓ Median/CI as (8.2 – 16.7) — parentheses + spaced en-dash, never brackets

✓ SI units

✓ One space between value and unit

✓ Define abbreviations at first use

✓ Objective scientific language

✓ Past tense for Methods and Results

✓ Present tense for established knowledge

✓ No interpretation in Results

✓ Active voice when possible

✓ Consistent terminology throughout the manuscript

✓ Updated .docx passages written in red (RGB 255,0,0)
