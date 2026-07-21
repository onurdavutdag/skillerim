---
name: bilim-klasoredit
description: >-
  Bir "Bilim ..." proje klasöründeki (ör. Bilim Fare Tümör, Bilim Tez C2) tüm
  dosya ve alt klasörleri 6 üst kategoriye indirger: Introduction,
  Materyal-Method, Result, Discussion-Conclusion, (projeye özgü 5. kategori),
  Diğer. Kullanıcı "6'lar kuralını uygula", "bu şekilde sınıflandır", "proje
  klasörünü düzenle/sınıflandır", "dosyaları kategorilere ayır", "diğer bilim
  dosyalarına da uygula" dediğinde bu skill'i kullan. İşlem sonunda kök dizin
  tam olarak bu 6 klasör + output/ + desktop.ini (varsa) içerir, başka loose
  dosya kalmaz. İlk kullanımda yalnızca 5. kategori ismi ve kategori dilleri
  netleştirilir; sonraki her "Bilim ..." projesinde tekrar sorulmadan doğrudan
  uygulanır.
---

# Bilim Project Folder Classification — The "6s Rule"

The presentation "at most 6 items" rule adapted to a folder structure.
Source: user, while applying the Bilim Tez C2 precedent to the Bilim Fare Tümör
project, 21 July 2026.

## The 6 categories

A **sequence number** is added before the folder name: `1) Introduction`, `2)
Materyal-Method` ... `6) Diğer` — the order is always this 1-6 sequence, whatever
the category language is. Source: user, 21 July 2026.

1. **Introduction** — pure literature/background: articles to read/read,
   Bibtex/EndNote reference folders.
2. **Materyal-Method** — method, protocols, measurement/experiment visuals, ethics
   committee application and administrative documents, drug/equipment information. Reviews and
   format-reference other thesis/example folders also go here (not to Introduction)
   — they count as material that "sheds light on how it will be done".
3. **Result** — findings/results: analysis outputs (statistics outputs,
   processed datasets) AND the results of completed pilot/preliminary studies
   (report, photo/video, histopathology). Left empty if the project is not at this stage.
4. **Discussion-Conclusion** — left empty if not yet written.
5. **(project-specific name)** — adapted to the project's phase: if at the writing
   stage, "Tez Metni-Sunum" (main text, journal preparation, presentation); if at the data-collection/early
   stage, "Proje Yönetimi-Fon Başvuruları" (BAP, Tübitak,
   expense/purchase). The name is clarified once for the project, and is not asked again in the same
   project.
6. **Diğer** — residual/outdated/duplicate/do-not-touch content, shortcuts left in the
   root.

When done, the root contains **exactly** these 6 folders (numbered: `1) ...` – `6) ...`)
+ `output/` (a separate project rule, in CLAUDE.md, unnumbered) + `desktop.ini`
(if present).

## Operation rules

- **The category language can be mixed.** The user states, per project, which
  category will be in which language (e.g. Bilim Fare Tümör: 1-4
  English, 5-6 Turkish). Unless the user states otherwise, the same language preference is taken as the default in the next "bilim"
  project too.
- **Mixed-content folders** (e.g. "Diğerleri") are split by content type,
  distributed to the relevant category; the emptied folder is deleted.
- **A move = rename/move, NOT copy-delete** — done within the same unit (the same disk/OneDrive
  sync folder). Especially for large photo/video files, it prevents
  OneDrive from re-uploading.
- **Old top-level numbering prefixes** (e.g. `1) `, `2) `) are dropped when moving to the new
  category; the subfolders' own internal numbering is preserved.
- When requested for another "Bilim ..." project folder, this rule is applied
  directly, not asked again — only a short clarification is asked, if needed, for the project-specific 5th category name,
  the category languages, and the mixed-folder splitting detail.

## Application steps

1. **Take an inventory.** List the root directory (`Get-ChildItem` / `ls`), see all
   loose files and folders.
2. **If it is the first use, clarify** (`AskUserQuestion`): what the 5th category's name
   will be, in which language(s) the category names will be. If it is already clarified earlier in this
   project (if it is in CLAUDE.md/memory), do not ask again.
3. **Assign each item to a category** — per the 6 definitions above. Open mixed
   folders first, distribute their content one by one.
4. **Show the move plan** (source → target list) — especially in a large project applied for the first time,
   let the user see at a glance what goes where. In known/repeat projects this step can be kept short.
5. **Move.** The target category folders are created with numbered names (`1)
   Introduction`, `2) Materyal-Method` ...). In PowerShell, for a same-unit
   move use `Move-Item`:
   ```powershell
   New-Item -ItemType Directory -Force -Path "1) Introduction"
   Move-Item -Path "<source>" -Destination "<numbered-target-category>\<new-name>" -Confirm:$false
   ```
   For files that are dehydrated (cloud-only) with OneDrive "Files On-Demand",
   `Move-Item` moves the metadata without downloading the content — it causes no problem.
6. **Delete the emptied folders**, verify that nothing remains in the root besides the 6 numbered
   categories + `output/` + `desktop.ini`.
7. **Optional inventory note** — you can document the classification as
   `output/md/İnceleme ... .md` (precedent: Bilim Tez C2); not mandatory.

## Precedent projects

Bilim Tez C2 (applied first) → Bilim Fare Tümör (Introduction/
Materyal-Method/Result/Discussion-Conclusion English; the 5th and 6th categories
Turkish).

## PDF naming subtask — the `bilim-s-pdf` subagent

If the name of the article PDFs entering Introduction or Materyal-Method is not
standard (if the author/year/journal information is not in the name), the `bilim-s-pdf`
subagent can be called to convert to a Vancouver-style pattern:

```
YYYY LastName. Journal Name. Title.pdf
```

This step is **not automatic/mandatory** — it kicks in if the user additionally asks
during classification, or when the user directly says "rename the PDFs"/"name in Vancouver
style". The rule details (the journal name is written in full — not abbreviated, ":"/em dash → ".", the 120-character limit,
the no-fabrication ban, the "+" sign position preservation) are in the subagent definition
(`~/.claude/agents/bilim-s-pdf.md`). Detailed introduction: this
skill's `README.md`.
