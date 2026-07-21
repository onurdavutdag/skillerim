# skillerim

Kendi Claude Code skill ve subagent'larımın deposu.

## İçerik

| Yol | Ne işe yarar |
|---|---|
| [`skills/bilim-klasoredit/`](skills/bilim-klasoredit/) | Bir "Bilim ..." proje klasörünü 6 üst kategoriye (Introduction, Materyal-Method, Result, Discussion-Conclusion, proje-özgü 5. kategori, Diğer) indirgeyen skill. |
| [`agents/bilim-s-pdf.md`](agents/bilim-s-pdf.md) | Makale PDF'lerini Vancouver-tarzı bir kalıba (`YYYY Soyad. Dergi Adı. Başlık.pdf`) göre yeniden adlandıran subagent — `bilim-klasoredit` tarafından çağrılır. |

## Kurulum

Bir dosyayı kullanmak için ilgili `.md` dosyasını kendi `~/.claude/skills/` veya `~/.claude/agents/` klasörüne kopyala.
