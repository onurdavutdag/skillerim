# Kayıt şeması ve Excel sözleşmesi

Bu dosya, **tarama ajanları ile script'ler arasındaki sözleşmedir**. Ajan buraya yazar, script buradan okur.
Şema değişirse üç ajan promptu ve `emlaktoplayici_excelbas.py` **birlikte** güncellenir.

## 1. Tarama JSON'u (ajanın diske yazdığı)

Dosya adı: `output/json/<site> <YYYYAAGG SSDD>.json`

```json
{
  "meta": {
    "site": "sahibinden",
    "kategori": "satilik-daire",
    "konum": "hatay",
    "arama_url": "https://www.sahibinden.com/satilik-daire/hatay?price_min=2800000&price_max=3000000",
    "filtre": { "fiyat_min": 2800000, "fiyat_max": 3000000 },
    "tarama_zamani": "2026-08-14T19:22:00",
    "sitedeki_ilan_sayisi": 149,
    "taranan_sayfa": "3/3",
    "atlanan": 0,
    "blok_yedi_mi": false,
    "notlar": "fiyat filtresi URL parametresiyle uygulandı"
  },
  "ilanlar": [
    {
      "ilan_no": "1327480381",
      "site": "sahibinden",
      "baslik": "A Gayrimenkul'den İsmet İnönü Mahallesinde Satılık Daire",
      "fiyat": 2950000,
      "m2_brut": 140,
      "m2_net": null,
      "oda": "3+1",
      "il": "Hatay",
      "ilce": "İskenderun",
      "semt": "Cumhuriyet",
      "tarih": "2026-08-10",
      "link": "https://www.sahibinden.com/ilan/1327480381/detay",
      "bina_yasi": null,
      "bina_yasi_bant": null,
      "kat": null,
      "toplam_kat": null,
      "isitma": null,
      "tapu_durumu": null,
      "aciklama": null
    }
  ]
}
```

### Alan kuralları

| Alan | Tip | Zorunlu | Not |
|---|---|:---:|---|
| `ilan_no` | string | ✅ | Site içinde benzersiz. Sayı olsa bile **string** — baştaki sıfırlar korunsun |
| `site` | string | ✅ | `sahibinden` / `hepsiemlak` / `emlakjet` |
| `baslik` | string | ✅ | Ham başlık, kırpılmadan |
| `fiyat` | int | ✅ | **TL, ayraçsız tam sayı.** `"2.950.000 TL"` → `2950000` |
| `m2_brut` / `m2_net` | int / null | — | Site hangisini veriyorsa o dolar; ikisi de varsa ikisi de |
| `oda` | string | — | Site nasıl yazıyorsa (`3+1`, `1.5+1`) |
| `il` / `ilce` / `semt` | string / null | `ilce` ✅ | `ilce` tekilleştirme anahtarının parçası, boş bırakılamaz |
| `tarih` | `YYYY-MM-DD` / null | — | İlan yayın/güncelleme tarihi |
| `link` | string | ✅ | Tam URL |
| `bina_yasi` | int / null | — | **Yıl değil, yaş.** Yalnız düz sayı buraya girer |
| `bina_yasi_bant` | string / null | — | Site bant veriyorsa ham metin (`"11-15 arası"`, `"31 ve üzeri"`). **sahibinden hep bant verir.** Banttan tek sayı türetilmez — skorlayıcı bandı kendi çözer |
| `kat` / `toplam_kat` | int / null | — | `kat` bodrum için negatif, zemin `0` |
| `tapu_durumu` / `aciklama` | string / null | — | Yalnız detay taramasında dolar |

**`0` ile `null` farklıdır.** `0` = baktım, değeri sıfır. `null` = doğrulayamadım.
Bulunamayan alan **atlanmaz**, `null` yazılır — script eksik anahtarı hata sayar.

## 2. Ajanın geriye döndürdüğü (ana bağlama giren)

Yalnız bu — başka hiçbir şey:

```json
{"site": "sahibinden", "ilan_sayisi": 149, "dosya_yolu": "output/json/sahibinden 20260814 1922.json",
 "blok_yedi_mi": false, "atlanan": 0, "notlar": "3 sayfa, pagingSize=50"}
```

## 3. Detay JSON'u (ayrı geçişte toplanır)

Detay alanları listede yoktur, ilan sayfasına girmeyi gerektirir — bu yüzden ayrı dosya, ayrı script:

```json
{ "1327480381": {"tapu_durumu": "Kat Mülkiyetli", "aciklama": "...", "bina_yasi": 3, "kat": 2, "toplam_kat": 5} }
```

Anahtar `ilan_no`. Kayıt `bina_yasi_bant`, `isitma` ve `m2_net` de taşıyabilir. Eksik ilan
`Belirtilmemiş` olarak işlenir, satır silinmez.

## 4. Excel çıktısı

### Sayfa "Ana"

Başlıklar Excel'e **ASCII** basılır (`Ilan Basligi`, `Ilce`, `m2 (Brut)`) — Windows/Excel
kodlama sürprizlerine kapı kapalı kalsın diye. `exceloku` hem ASCII hem Türkçe başlığı tanır.

| # | Sütun | Kaynak alan | Genişlik | Biçim |
|---:|---|---|---:|---|
| 1 | Ilan Basligi | `baslik` | 52 | — |
| 2 | Fiyat (TL) | `fiyat` | 14 | `#,##0` — **sayı** |
| 3 | m2 (Brut) | `m2_brut` | 10 | `0` — sayı |
| 4 | TL/m2 | *hesaplanır* | 12 | `#,##0` — sayı |
| 5 | Oda | `oda` | 8 | — |
| 6 | Ilce | `ilce` | 13 | — |
| 7 | Semt | `semt` | 14 | — |
| 8 | Ilan Tarihi | `tarih` | 13 | `DD.MM.YYYY`, ortalı |
| 9 | Ilan No | `ilan_no` | 14 | metin |
| 10 | Kaynak | *hesaplanır* | 22 | Birden çok siteyse virgülle |
| 11 | Link | `link` | 46 | köprü, mavi + altı çizili |

Veride dolu olduğunda eklenen isteğe bağlı sütunlar (boş sütun üretilmez):
**m2 (Net)** (m2 Brut'tan sonra), **Tapu Durumu** (Oda'dan sonra), **Bina Yasi** /
**Bina Yasi Bandi** / **Toplam Kat** / **Bulundugu Kat** / **Isitma** (Semt'ten sonra),
**Deprem Risk** + 6 bileşen + `Neden`, **Mesafe (km)**, **Açıklama** (her zaman en sonda —
uzun metin diğer sütunları itmesin).

> Bulunduğu kat sütununun adı **"Bulundugu Kat"tır, "Kat" değil** — "Kat" başlığı deprem
> bloğundaki kat bileşenine aittir; `exceloku` deprem bloğu varken o adı bilerek atlar.

Başlık satırı: dolgu `1F3864`, beyaz kalın yazı, ortalı, yükseklik 26.
`freeze_panes = "A2"`, `auto_filter` tüm tabloya.

### Sayfa "Özet"

- İlçe kırılımı: adet, ortalama fiyat, ortalama TL/m², en ucuz/en pahalı
- Fiyat ve TL/m² dağılımı (min, çeyrekler, medyan, maks)
- Kaynak site başına ilan sayısı + tekilleştirmede birleşen satır sayısı
- **Kapsam uyarıları:** atlanan ilan, blok yiyen site, "olası tekrar" işaretli çiftler
- Deprem skoru varsa: skor bandı dağılımı + **zorunlu uyarı metni** (`emlaktoplayici-r-deprem-risk-olcegi.md` §5)

### Sayfa "Künye"

`meta` bloğunun tamamı okunur biçimde: kaynak, filtre, arama URL'i, tarama zamanı, sitedeki ilan sayısı,
tabloya giren, atlanan, taranan sayfa, blok durumu, ortalama fiyat, ortalama TL/m², notlar; mesafe
sütunu ilçe merkezinden hesaplandıysa "yaklaşık" notu; deprem skoru varsa zorunlu uyarı metni.
A sütunu kalın, genişlik 26 / 96.

## 5. Tekilleştirme

Aynı daire birden çok sitede ilan edilmiş olabilir. Eşleşme anahtarı **hepsi birden** ve
**yalnız farklı siteler arasında** (aynı sitedeki iki ilan birleştirilmez — site zaten
ilan numarasıyla tekilleştirir):

```
site farklı  AND  ilce aynı  AND  |m² farkı| ≤ %3  AND  |fiyat farkı| ≤ %2  AND  oda aynı
```

- Eşleşenler tek satıra iner; `Kaynak` sütununda siteler listelenir. Birleşik satır **en yeni
  tarihli** kayıttan başlar (`link` de ondan gelir); eksik alanları diğer kayıtlardan tamamlanır.
- Alanlar birleştirilirken **dolu olan kazanır**; ikisi de doluysa daha yeni `tarih` kazanır.
  **İstisna — `deprem` sözlüğü:** skoru üretilmiş kayıt, daha yeni tarihli ama skorsuz kayda
  karşı kazanır (aksi hâlde hesaplanmış skor çöpe gider — 15.08.2026'da oldu, düzeltildi).
- **"Olası tekrar":** kimlik alanları (ilçe + oda + m²) tutup **yalnız fiyat** tutmuyorsa ve
  siteler farklıysa çift **birleştirilmez**, `Özet`'e "olası tekrar" olarak yazılır — "aynı
  daire, iki sitede farklı fiyat" adayı budur. Genel "3/4 tutuyor" kuralı bilerek kullanılmaz:
  dar fiyat aralıklı aramada oda/ilçe/fiyat kendiliğinden tutar ve bayrak yüzlerce kez yanıp
  değersizleşir (15.08.2026 koşusunda çift bazında ölçüldü: yalnız-fiyat-farklı 9'a karşı
  diğer kombinasyonlar 347).

Gerekçe: sessiz birleştirme veri kaybıdır; kullanıcı iki ayrı ilanı tek sanabilir. Şüphe raporlanır, silinmez.

## 6. Biçim kuralları

- **Sayılar sayı olarak yazılır**, metin olarak değil — Excel'de sıralama/filtre çalışsın
- Türkçe sayı biçimi çıktı metinlerinde geçerlidir (ondalık virgül, `%` sayının önünde);
  hücre değerleri ham sayıdır, biçimi `number_format` verir
- Dosya adı `<Ad> YYYYAAGG SSDD.xlsx`, konum `output/xlsx/`
- Açıklama hücresi Excel sınırı olan 32.767 karakteri aşamaz — 32.000'de kırpılır ve
  ` […kısaltıldı]` eklenir; kırpılan satır sayısı Künye'ye yazılır
