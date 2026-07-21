# bilim-klasoredit — Kullanım Kılavuzu

> ## ⚠️ BAKIM KURALI (önce oku)
> **Bu bir CANLI dokümandır.** Skill'e bir bölüm/kural eklendiğinde,
> değiştirildiğinde veya silindiğinde ya da yeni bir subagent bağlandığında
> bu dosya da AYNI değişiklikle güncellenir.
>
> _Son güncelleme: 2026-07-21 — skill adı `bilim-klasoredit` olarak
> değiştirildi; subagent adı `bilim-s-pdf` ile senkronize edildi._

---

## 1. Genel bakış

`bilim-klasoredit`, herhangi bir "Bilim ..." proje klasörünü
(ör. Bilim Fare Tümör, Bilim Tez C2, Bilim Spinal Araknoid Kist Vaka
Sunumu) 6 sabit üst kategoriye indirgeyen bir Claude Code skill'idir:
**Introduction, Materyal-Method, Result, Discussion-Conclusion,
(projeye özgü 5. kategori), Diğer**. İçerik Türkçedir. Tetikleyici:
kullanıcı "6'lar kuralını uygula", "bu şekilde sınıflandır", "proje
klasörünü düzenle/sınıflandır" dediğinde.

İşlem bitince kök dizin **tam olarak** bu 6 numaralı klasör + `output/`
(ayrı global CLAUDE.md kuralı) + `desktop.ini` (varsa) içerir; başka loose
dosya/kısayol kalmaz (6. kategoriye taşınır). Kural detayı: `SKILL.md`.

## 2. Çağırdığı subagent: `bilim-s-pdf`

| Özellik | Değer |
|---|---|
| Konum | `~/.claude/agents/bilim-s-pdf.md` (bağımsız, plugin'e sarılı değil) |
| Tools | `Read, Glob, Bash` |
| Ne zaman çağrılır | Introduction/Materyal-Method'a standart olmayan adlı bir makale PDF'i girdiğinde (isteğe bağlı) veya kullanıcı doğrudan "PDF'leri adlandır"/"vancouver stilinde adlandır" dediğinde |
| Amaç | İndirilmiş makale PDF'lerini `YYYY Soyad. Dergi Adı. Başlık.pdf` kalıbına göre **aynı klasörde** yeniden adlandırır |
| Girdi | Bir klasördeki (veya belirtilen) `*.pdf` dosyaları |
| Çıktı | Yeniden adlandırılmış dosyalar + eski→yeni ad tablosu raporu |

**Adlandırma kuralı özeti:**
- `YYYY` = yayın/posted yılı, `Soyad.` = yalnızca ilk yazarın soyadı
  (nokta ile biter), `Dergi Adı.` = derginin **tam adı** (nokta ile
  biter; NLM/PubMed kısaltmasına çevrilmez; preprint sunucusuysa —
  Research Square vb. — sunucunun adı kullanılır).
- Başlıkta `:` ve alt-başlık ayıracı em dash `—` → `.`; diğer Windows'ta
  geçersiz karakterler (`\ / * ? " < > |`) temizlenir.
- Toplam ad (uzantı dahil, klasör yolu hariç) varsayılan **120 karakter**
  sınırını aşarsa: önce alt-başlık atılır; alt-başlık ayırt edici bilgiyse
  bunun yerine son kelime(ler) kelime sınırında kırpılır (üç nokta yok).
- Orijinal dosya adında yılın hemen önünde/ardında bir `+` işareti varsa
  (kullanıcının öncelik/filtre etiketi), konumu (prefix/suffix) yeni
  adda birebir korunur — başlık ortasındaki `+` (ör. bilimsel terim)
  bu kurala dahil değildir.
- Yazar/yıl/dergi bilgisi PDF metninden **doğrulanmadan asla uydurulmaz**
  — emin olunamayan dosya atlanır, kullanıcıya bildirilir.

Tam kural ve adım adım yöntem: subagent tanımının kendisinde
(`~/.claude/agents/bilim-s-pdf.md`).

## 3. Kırmızı çizgiler

- 6 kategori dışında kökte loose dosya/klasör **bırakılmaz**.
- Taşıma her zaman rename/move'dur, kopyala-sil **değil** (OneDrive büyük
  dosya yeniden yüklemesini önlemek için).
- `bilim-s-pdf` dosya **içeriğine dokunmaz**, yalnızca adını
  değiştirir; yazar/yıl/dergi bilgisini uydurmaz.

## 4. Bileşen envanteri

| Tür | Yol |
|---|---|
| Skill talimatı | `SKILL.md` |
| Kılavuz (bu dosya) | `README.md` |
| Subagent | `../../agents/bilim-s-pdf.md` |
