# dhyuzmani — Kullanım Kılavuzu

> ## ⚠️ BAKIM KURALI (önce oku)
> **Bu yaşayan bir belgedir.** `SKILL.md`, `references/` veya `scripts/` içinde bir kural
> eklendiğinde, değiştiğinde veya kaldırıldığında bu dosya **aynı değişiklikle** güncellenir.
>
> **Bu skill'e özgü ikinci kural:** `SKILL.md` süreç akışının tek doğru kaynağıdır;
> `references/veri-kaynaklari.md` veri kaynakları ve tuzakların, `references/ajan-sablonu.md`
> ise tarama ajanı promptunun tek doğru kaynağıdır. Biri değişince diğerleriyle çelişmediği
> doğrulanır.
>
> _Son güncelleme: 2026-08-11 — skill oluşturuldu._

---

## 1. Genel bakış

`dhyuzmani`, DHY (Devlet Hizmet Yükümlülüğü) kurasında **beyin ve sinir cerrahisi uzman kadrosu
açılan hastaneleri** kullanıcının referans şehrine (varsayılan **Hatay/Antakya**) göre analiz eden
bir Claude Code skill'idir.

Cevapladığı soru şudur: *bir kadro çıktığı hastanede kaç beyin cerrahı var, hastane kaç yataklı,
kaç ameliyathanesi var ve Hatay'a karayoluyla ne kadar uzak?*

Çıktı, filtrelenebilir tek bir Excel dosyasıdır.

## 2. Ne zaman tetiklenir

- "DHY kadrolarını analiz et", "beyin cerrahisi kadroları"
- "Hangi hastanede kaç beyin cerrahı var"
- "Hatay'a en yakın kadrolar", "atama için hastaneleri karşılaştır"
- "Yeni dönem kurası çıktı" (yeni PDF verildiğinde önce OCR, sonra analiz)
- Kullanıcı doğrudan "dhyuzmani" dediğinde

## 3. Veri modeli — neyin taze, neyin sabit olduğu

Bu ayrım skill'in temel tasarım kararıdır:

| Veri | Kaynak | Davranış | Gerekçe |
|---|---|---|---|
| Karayolu mesafesi | KGM cetveli (`assets/`) | yerel, anında | Mesafeler yıllarca değişmez |
| Yatak kapasitesi | KHGM türevi harita (`assets/`) | yerel, anında | Tescilli kapasite nadiren değişir |
| **Uzman sayısı** | Hastane siteleri, MHRS, haber | **her çalıştırmada web** | Atama/ayrılmayla sürekli değişir |
| **Ameliyathane** | Resmî tanıtım, açılış haberleri | **her çalıştırmada web** | Yeni bina/tadilatla değişir |
| Kadro / dönem | Kura sonuç CSV'leri | yerel | Geçmiş kura sonucu sabittir |

Kullanıcı kararı: tarama **her zaman listenin tamamını** kapsar, kısmi tarama yapılmaz (~10–15 dk).

## 4. Bileşen envanteri

### Scriptler

| Dosya | Girdi | Çıktı | İş |
|---|---|---|---|
| `dhyuzmani_kadro.py` | Kura CSV klasörü | `kadro.json` | Branşa uyan satırları birim düzeyinde gruplar; OCR kaynaklı ad bozukluklarını normalize eder |
| `dhyuzmani_mesafe.py` | `kadro.json` | `mesafe.json` | İl merkezleri için KGM değeri, ilçeler için doğrulanmış ofset; `~` ile yaklaşıklık işareti |
| `dhyuzmani_yatak.py` | `mesafe.json` | `yatak.json` | Yerel haritadan okur; eksik hastane varsa KHGM listesini indirip bulanık eşleşmeyle bulur |
| `dhyuzmani_excel.py` | `yatak.json` + tarama JSON | `.xlsx` | Hepsini birleştirip biçimli Excel üretir (dondurulmuş başlık, filtre, vurgu, Notlar sayfası) |

Hepsi bağımsız çalıştırılabilir; `--birim` ile tek hastane sorgusu da yapılabilir.

### Referanslar

| Dosya | İçerik |
|---|---|
| `references/veri-kaynaklari.md` | Kaynak öncelik sırası, 11.08.2026 taramasında öğrenilen tuzaklar, KGM/KHGM şemaları, doğrulama değerleri |
| `references/ajan-sablonu.md` | Paralel tarama ajanının promptu, çıktı JSON şeması, partileme ve düşen ajanı sürdürme kuralları |

### Varlıklar

| Dosya | Boyut | Not |
|---|---|---|
| `assets/kgm_il_mesafe.xlsx` | ~56 KB | KGM İller Arası Mesafe Cetveli, 03.03.2026 |
| `assets/ilce_mesafe.json` | ~10 KB | 46 ilçe hastanesi, Hatay'a doğrulanmış ofsetler |
| `assets/yatak_map.json` | ~4 KB | 88 birim tescilli yatak (KHGM türevi + 4 web düzeltmesi) |

**KHGM tesis listesi (5 MB) depoda tutulmaz** — türetilmiş harita yeterlidir. Yeni bir hastane
çıkarsa script dosyayı indirip `~/.claude/.cache/dhyuzmani/` altına önbellekler.

## 5. Alt ajanlar

Bu skill'in kendi tanımlı alt ajanı yoktur; tarama adımında **jenerik `general-purpose` ajanları**
kullanılır. Promptları `references/ajan-sablonu.md`'den gelir.

| Özellik | Değer |
|---|---|
| Ajan tipi | `general-purpose` (WebSearch + WebFetch) |
| Sayı | Hastane sayısı ÷ 10 (88 hastane → 9 ajan) |
| Başlatma | Hepsi tek mesajda, arka planda |
| Girdi | 10 hastane adı + il |
| Çıktı | Katı JSON dizisi: `birim, bc_uzman, bc_kaynak, ameliyathane, am_kaynak, not` |
| Kısıt | Tahmin yasak; bulunamayan alan `null`; `0` ≠ `null` |
| Hata | Düşen ajan yeniden başlatılmaz, `SendMessage` ile sürdürülür |

## 6. Gizlilik ve telif

⚠️ **Kura CSV'leri binlerce hekimin ad-soyadını içerir.** Bu dosyalar:
- Skill deposuna **kopyalanmaz** — scriptler kullanıcının proje klasöründen okur
- Hiçbir uzak depoya, artifact'e veya dış servise **gönderilmez**
- Skill çıktısına yalnız **hastane düzeyinde toplu veri** girer (ad-soyad asla)

`assets/` altındaki KGM ve KHGM verileri kamuya açık resmî veridir; telif riski taşımaz.

## 7. Doğrulama

Skill'de bir değişiklik yapıldığında koşturulacak kontroller:

```bash
# 1. Kadro: 88 birim / 127 kadro dönmeli
python -B scripts/dhyuzmani_kadro.py "<proje>/output/csv" --json /tmp/kadro.json

# 2. Mesafe: KGM resmî değerleriyle karşılaştır
python -B scripts/dhyuzmani_mesafe.py --birim "X" --il ADANA          # 196 km
python -B scripts/dhyuzmani_mesafe.py --birim "X" --il GAZİANTEP      # 194 km
python -B scripts/dhyuzmani_mesafe.py --birim "X" --il KAHRAMANMARAŞ  # 176 km

# 3. Yatak: 88/88 dolu olmalı
python -B scripts/dhyuzmani_yatak.py --json /tmp/mesafe.json --cikti /tmp/yatak.json

# 4. Excel: 88 satır, Türkçe karakterler bozulmamış
python -B scripts/dhyuzmani_excel.py --json /tmp/yatak.json --cikti /tmp/test.xlsx
```

## 8. Senkron

Bu skill üç katmanda durur (senkron kuralı):

| Katman | Yol |
|---|---|
| Yerel (kaynak) | `Desktop\claude working\skillerim\skills\dhyuzmani\` |
| Global (çalışan) | `~/.claude/skills/dhyuzmani/` — hook aynalar, elle kopyalanmaz |
| GitHub | `github.com/onurdavutdag/skillerim` — içerik aynı oturumda commit + push |
