# Worked example — Bilim Fare Tümör (before → after)

A concrete illustration of the "6s Rule" applied to a real "Bilim ..." folder.
Category languages here: categories 1-4 English, 5-6 Turkish (the project's
stated preference). Use this as a reference for how loose items map to the 6
numbered categories — not as a fixed file list.

## Before (root — loose, unclassified)

```
Bilim Fare Tümör/
├── makale okunacak/                     (2 PDF, literature)
├── EndNote referanslar/
├── etik kurul başvuru formu.docx
├── ilaç dozaj protokolü.pdf
├── ölçüm fotoğrafları/                  (caliper photos)
├── benzer tez örneği/                   (format-reference thesis)
├── istatistik çıktısı SPSS.pdf
├── pilot çalışma histopatoloji/         (H&E images)
├── tez taslağı v3.docx
├── BAP bütçe tablosu.xlsx
├── satın alma faturaları/
├── eski taslak v1.docx                  (outdated)
├── masaüstü kısayolu.lnk
└── Diğerleri/                           (MIXED: 1 makale + 1 fatura + 1 foto)
```

## Mapping (each item → category)

| Item | → Category |
|---|---|
| makale okunacak/, EndNote referanslar/ | `1) Introduction` |
| etik kurul başvuru formu.docx, ilaç dozaj protokolü.pdf, ölçüm fotoğrafları/, benzer tez örneği/ | `2) Materyal-Method` |
| istatistik çıktısı SPSS.pdf, pilot çalışma histopatoloji/ | `3) Result` |
| — (not written yet) | `4) Discussion-Conclusion` (empty) |
| tez taslağı v3.docx, BAP bütçe tablosu.xlsx, satın alma faturaları/ | `5) Tez Metni-Sunum` / Proje Yönetimi (project phase) |
| eski taslak v1.docx, masaüstü kısayolu.lnk | `6) Diğer` |
| **Diğerleri/** (mixed) | split: makale → `1)`, fatura → `5)`, foto → `2)`; empty folder deleted |

Note: the format-reference thesis (`benzer tez örneği/`) goes to
`2) Materyal-Method`, NOT Introduction — it "sheds light on how it will be done."

## After (root — exactly 6 numbered categories)

```
Bilim Fare Tümör/
├── 1) Introduction/
├── 2) Materyal-Method/
├── 3) Result/
├── 4) Discussion-Conclusion/      (empty — stage not reached)
├── 5) Tez Metni-Sunum/
├── 6) Diğer/
├── output/                         (separate global rule, unnumbered)
└── desktop.ini                     (if present)
```

No loose file/shortcut remains in the root. Moves were done with `Move-Item`
(rename/move, not copy-delete) to avoid OneDrive re-upload of large photo/video
files. Old top-level numbering prefixes on moved items were dropped; subfolders'
internal numbering was preserved.
