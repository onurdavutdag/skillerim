---
name: dhyuzmani
description: Bu skill, DHY (Devlet Hizmet Yükümlülüğü) kurasında beyin ve sinir cerrahisi uzman kadrosu açılan hastaneleri Hatay'a yakınlık temelinde analiz etmek için kullanılmalıdır. Her hastane için üç şeyi bir araya getirir: hâlen görevli beyin cerrahisi uzmanı sayısı (her çalıştırmada taze web taraması), yatak kapasitesi ve referans şehre karayolu mesafesi; sonucu filtrelenebilir bir Excel dosyası olarak verir. Tetikleyiciler; "DHY kadrolarını analiz et", "beyin cerrahisi kadroları", "hangi hastanede kaç beyin cerrahı var", "Hatay'a en yakın kadrolar", "kura sonuçlarını incele", "yeni dönem kurası çıktı", "atama için hastaneleri karşılaştır" gibi ifadeler. Kullanıcı "dhyuzmani" dediğinde de bu skill kullanılır. Yeni bir dönemin noter onaylı kura PDF'i verildiğinde önce OCR ile kadrolar çıkarılır, sonra analiz yapılır.
---

# dhyuzmani
*DHY Uzman Kadro Analisti*

DHY kurasında beyin ve sinir cerrahisi kadrosu açılan hastaneleri, kullanıcının referans şehrine
(varsayılan **Hatay/Antakya**) göre analiz eder. Tetiklenme koşulları yukarıdaki `description`'dadır.

## Ne üretir

Hastane başına tek satır, şu sütunlarla:

| Sütun | Kaynak | Tazelik |
|---|---|---|
| Karayolu mesafesi | KGM İller Arası Mesafe Cetveli (yerel) | sabit |
| Yatak kapasitesi | KHGM tesis listesi türevi (yerel) | sabit |
| **Uzman sayısı** | hastane siteleri + MHRS agregatörleri + haber | **her çalıştırmada taze** |
| **Ameliyathane sayısı** | resmî tanıtım sayfaları + açılış haberleri | **her çalıştırmada taze** |
| Dönem / kadro / genel kura | kura sonuç CSV'leri (yerel) | sabit |

Çıktı: `output/xlsx/` altına tarih-saat etiketli `.xlsx` — başlık dondurulmuş, otomatik filtreli,
referans şehrin satırları vurgulu, ikinci sayfada yöntem notları.

## Süreç

### Adım 1 — Kapsamı doğrula

Kullanıcıya sor (varsayılanları belirterek, cevap gelmeden ilerleme):

> 1. Referans şehir Hatay (Antakya) kalsın mı?
> 2. Yeni bir dönemin kura PDF'i var mı, yoksa mevcut 120–129. dönem verisiyle mi çalışayım?

Kullanıcı zaten belirtmişse sorma, doğrudan geç.

### Adım 2 — Kadro listesini çıkar

Yeni dönem PDF'i varsa **önce** OCR aşaması: proje klasöründeki `dhy_ocr_parse` mantığıyla
(Tesseract, `tur`, 300 DPI) yeni dönemin CSV'si üretilir ve diğerlerinin yanına konur.

Sonra:

```bash
python -B scripts/dhyuzmani_kadro.py "<proje>/output/csv" --json <tmp>/kadro.json
```

`<proje>` = `C:\Users\onurd\OneDrive\1) My Files\2) Kişisel\Mart 2027 atama` (bilinen konum;
taşınmışsa `1[0-9][0-9] DHY*` desenli dosyalar aranır ve `references/veri-kaynaklari.md` §5 güncellenir).

Beklenen (120–129. dönem, değişmediyse): **88 benzersiz birim / 127 kadro**.

> ⚠️ CSV'ler hekim ad-soyadı içerir. Script yalnız okur, hastane düzeyinde toplu çıktı üretir.
> Bu dosyalar hiçbir uzak depoya, artifact'e veya paylaşıma gitmez.

### Adım 3 — Mesafe ve yatak (yerel, anında)

```bash
python -B scripts/dhyuzmani_mesafe.py --json <tmp>/kadro.json --cikti <tmp>/mesafe.json [--referans HATAY]
python -B scripts/dhyuzmani_yatak.py  --json <tmp>/mesafe.json --cikti <tmp>/yatak.json
```

Web'e gidilmez. Yatak haritasında olmayan yeni bir hastane çıkarsa `dhyuzmani_yatak.py`
KHGM listesini indirip `~/.claude/.cache/dhyuzmani/` altına önbellekler.

### Adım 4 — Taze web taraması (işin uzun kısmı)

Listedeki **tüm** hastaneler taranır — kısmi tarama yapılmaz.

1. Hastaneler mesafe sırasına göre **10'arlı partilere** bölünür (88 hastane → 9 parti)
2. Her parti için bir `general-purpose` ajanı, **hepsi tek mesajda**, arka planda başlatılır
3. Ajan promptu `references/ajan-sablonu.md` içindedir — birebir kullanılır, "TAHMİN ETME / null bırak" kuralı korunur
4. Dönen her partinin JSON'u **geldiği anda diske yazılır**
5. Bir ajan oturum limiti veya API hatasıyla düşerse yeniden başlatılmaz — `SendMessage` ile kaldığı yerden sürdürülür

Süre: ~10–15 dakika. Kullanıcıya baştan söylenir.

### Adım 5 — Birleştir ve sakla

Parti JSON'ları tek dosyada toplanır, birim adlarına birebir (tutmazsa bulanık) eşlenir:

```
output/json/dhyuzmani_tarama YYYYAAGG SSDD.json
```

Kaynak URL'lerle birlikte saklanır — sonraki taramada değişim karşılaştırması yapılabilsin diye.
Önceki tarama dosyası varsa değişen değerler (`önceki: X → şimdi: Y`) raporlanır.

### Adım 6 — Excel üret

```bash
python -B scripts/dhyuzmani_excel.py --json <tmp>/yatak.json \
  --tarama "output/json/dhyuzmani_tarama YYYYAAGG SSDD.json" \
  --cikti "output/xlsx/DHY Beyin Cerrahisi <REFERANS> YYYYAAGG SSDD.xlsx" --referans HATAY
```

Sonra kullanıcıya **kapsam raporu** verilir: kaç alan dolu/boş, hangi hastanelerde çelişki var,
en yakın birkaç hastane ve dikkat çeken bulgular.

## Kurallar

- **Tahmin yasak.** Bulunamayan alan `?` (Excel'de) / `null` (JSON'da) kalır. `0` ile `null` farklıdır: `0` = baktım, uzman yok; `null` = doğrulayamadım.
- **Yapımı süren hastane projelerinin salon sayısı mevcut binaya yazılmaz** — `references/veri-kaynaklari.md`'deki listeye bakılır.
- Sayı biçimi Türkçe kuralına uyar (ondalık virgül, `%` sayının önünde).
- Dosya adlandırma: `<Ad> YYYYAAGG SSDD.<uzantı>`, hepsi proje kökündeki `output/` altında, türe göre alt klasörde.
- Scriptler `python -B` ile çalıştırılır (`__pycache__` üretilmesin).

## Dosya haritası

| Yol | İş |
|---|---|
| `scripts/dhyuzmani_kadro.py` | Kura CSV'lerinden branş kadrolarını birim düzeyinde çıkarır |
| `scripts/dhyuzmani_mesafe.py` | KGM cetveli + ilçe ofsetlerinden referans şehre mesafe |
| `scripts/dhyuzmani_yatak.py` | Yerel yatak haritası; eksikse KHGM listesini indirip eşler |
| `scripts/dhyuzmani_excel.py` | Tüm veriyi birleştirip biçimli Excel üretir |
| `scripts/dhyuzmani_dogrula.py` | Öz-denetim: KGM değerleri, varlık bütünlüğü, 4 web düzeltmesi, kadro 88/127 |
| `references/veri-kaynaklari.md` | Kaynak öncelikleri, bilinen tuzaklar, doğrulama değerleri |
| `references/ajan-sablonu.md` | Paralel tarama ajanı promptu ve çıktı şeması |
| `assets/kgm_il_mesafe.xlsx` | KGM İller Arası Mesafe Cetveli (03.03.2026) |
| `assets/ilce_mesafe.json` | 46 ilçe hastanesi için Hatay'a doğrulanmış mesafe ofsetleri |
| `assets/yatak_map.json` | 88 birimin tescilli yatak sayısı (KHGM türevi + 4 web düzeltmesi) |
