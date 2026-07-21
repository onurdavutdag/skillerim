# Turkish Thesis Style Guide

## Turkish Medical Thesis and Journal Writing Standards

Version: 1.0

This document defines the default writing style for all Turkish medical
theses and manuscripts unless the university or journal specifies
otherwise.

------------------------------------------------------------------------

# 1. General Principles

-   Use formal scientific language.
-   Write objectively.
-   Avoid colloquial expressions.
-   Prefer concise and clear sentences.
-   Ensure consistency throughout the manuscript.

------------------------------------------------------------------------

# 2. Turkish Language Rules

-   Follow the current Türk Dil Kurumu (TDK) spelling guide.
-   Use Turkish punctuation rules.
-   Use Turkish capitalization rules.
-   Use Turkish decimal notation.

------------------------------------------------------------------------

# 3. Decimal Numbers

Use comma (,) as the decimal separator.

Correct

48,6

25,91

0,024

Incorrect

48.6

25.91

------------------------------------------------------------------------

# 4. Thousands Separator

Use period (.) for thousands.

Correct

1.245

15.780

Incorrect

1,245

15,780

------------------------------------------------------------------------

# 5. Percentages

Place the percent sign before the number.

Correct

%73,5

%12

Incorrect

73,5%

12%

No space is left between % and the number.

------------------------------------------------------------------------

# 6. P Values

-   Use lowercase italic p.
-   Report three decimal places whenever possible.
-   Never write p=0,000.
-   Extremely small values should be reported as p\<0,001.

Correct

*p*=0,248

*p*=0,037

*p*=0,999

*p*\<0,001

Incorrect

P=0,04

p=0,000

------------------------------------------------------------------------

# 7. Mean and Standard Deviation

Correct

48,6 ± 15,8 yıl

25,9 ± 4,16 kg/m²

------------------------------------------------------------------------

# 8. Median and IQR

Correct

12,5 (8,2-16,7)

Median (IQR)

------------------------------------------------------------------------

# 9. Units

Use SI units.

Leave one space between the number and the unit.

Correct

5 mm

15 cm

120 mL

48,6 yıl

25 kg

Incorrect

5mm

15cm

25kg

Exceptions

\%

°C

------------------------------------------------------------------------

# 10. Comparison Symbols

Leave one space before and after comparison symbols.

Correct

Wo ≥ 4 mm

p \< 0,001

BMI \> 30 kg/m²

Incorrect

Wo≥4 mm

p\<0,001

BMI\>30

------------------------------------------------------------------------

# 11. Confidence Interval

Correct

OR=2,31 (%95 GA: 1,42-3,88)

or

OR=2,31 (%95 güven aralığı: 1,42-3,88)

------------------------------------------------------------------------

# 12. Abbreviations

Define abbreviations at first use.

Correct

Vücut kitle indeksi (VKİ)

Bilgisayarlı tomografi (BT)

Manyetik rezonans görüntüleme (MRG)

Subsequent use

VKİ

BT

MRG

------------------------------------------------------------------------

# 13. Statistical Terms

Preferred

ortalama

standart sapma

medyan

çeyrekler arası aralık

minimum

maksimum

güven aralığı

olasılık değeri

Avoid mixing Turkish and English terminology.

------------------------------------------------------------------------

# 14. Numbers in Text

Numbers used as measurements should always be written with numerals.

Correct

5 mm

8 yıl

73 hasta

25 kg

General rule

One-digit numbers may be written in words when they are not
measurements.

Example

Üç grup oluşturuldu.

However, numerals are acceptable throughout scientific writing for
consistency.

------------------------------------------------------------------------

# 15. Table Citation

Correct

(Tablo 1)

(Tablo 2)

As shown in Tablo 2...

------------------------------------------------------------------------

# 16. Figure Citation

Correct

(Şekil 1)

(Şekil 2)

Şekil 3'te gösterilmiştir.

------------------------------------------------------------------------

# 17. Parentheses

No space before parentheses.

Correct

(Tablo 2)

(p\<0,001)

Incorrect

(Tablo 2)

------------------------------------------------------------------------

# 18. Scientific Tone

Preferred verbs

değerlendirildi

incelendi

karşılaştırıldı

hesaplandı

saptandı

gözlendi

belirlendi

raporlandı

Avoid

bakıldı

tespit edildi (unless institution specifically prefers it)

çok iyi bulundu

mükemmel

oldukça iyi

------------------------------------------------------------------------

# 19. Academic Objectivity

Avoid subjective language.

Correct

İki grup arasında istatistiksel olarak anlamlı fark bulundu.

Incorrect

İki grup arasında oldukça önemli bir fark vardı.

------------------------------------------------------------------------

# 20. Results Section

Only report findings.

Do not interpret.

Correct

Wo ≥ 4 mm grubunda vida yerleştirme oranı anlamlı olarak yüksekti
(p=0,021).

Incorrect

Bu sonuç cerrahi uygulamada oldukça önemlidir.

------------------------------------------------------------------------

# 21. Discussion Section

Interpret results.

Compare with literature.

Discuss limitations.

Do not introduce new data.

------------------------------------------------------------------------

# 22. Tense

Methods

Past tense

Results

Past tense

Discussion

Present tense for established knowledge.

Past tense when referring to study findings.

------------------------------------------------------------------------

# 23. Punctuation

No space before punctuation marks.

Correct

..., olarak bulundu.

..., değerlendirildi.

Incorrect

..., olarak bulundu .

------------------------------------------------------------------------

# 24. Colon

Leave no space before colon.

Leave one space after colon.

Correct

Sonuçlar: Grup 1...

------------------------------------------------------------------------

# 25. Semicolon

Use only when necessary.

Avoid excessively long sentences.

Prefer splitting long sentences into two.

------------------------------------------------------------------------

# 26. Lists

Maintain parallel structure.

Example

• değerlendirildi

• karşılaştırıldı

• analiz edildi

------------------------------------------------------------------------

# 27. Common Medical Terms

Preferred

ameliyat sonrası

ameliyat öncesi

takip

yeniden ameliyat

vida yerleştirildi

vida uygulanmadı

pars-pedikül kompleksi

------------------------------------------------------------------------

# 28. Common Writing Preferences

Prefer

92 vida

instead of

92 adet vida

Prefer

6 pars-pedikül kompleksine vida uygulanmadı.

instead of

6 adet vidanın uygulanmadığı.

------------------------------------------------------------------------

# 29. Frequent Mistakes

Incorrect

%73.5

Correct

%73,5

Incorrect

48.6

Correct

48,6

Incorrect

p=0,000

Correct

p\<0,001

Incorrect

5mm

Correct

5 mm

Incorrect

Wo≥4 mm

Correct

Wo ≥ 4 mm

------------------------------------------------------------------------

# 30. Revision Highlighting in .docx Updates (MANDATORY)

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

# 31. Final Checklist

✓ Turkish decimal comma

✓ Percent sign before number

✓ Italic p

✓ Three decimal places for p

✓ p\<0,001 instead of p=0,000

✓ SI units

✓ One space between number and unit

✓ Define abbreviations at first use

✓ Scientific, objective language

✓ Past tense in Methods and Results

✓ No interpretation in Results

✓ Tables and figures cited correctly

✓ TDK spelling rules followed

✓ Consistent terminology throughout the thesis

✓ Updated .docx passages written in red (RGB 255,0,0)
