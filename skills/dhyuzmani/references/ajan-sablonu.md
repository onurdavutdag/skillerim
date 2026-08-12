# Paralel Tarama Ajanı Şablonu

Uzman ve ameliyathane sayıları her çalıştırmada web'den taze toplanır. Tek tek aramak
88 hastane için çok yavaş olduğundan iş **10'arlı partilere** bölünüp paralel ajanlara verilir.

## Kurallar

- Partiler mesafe sırasına göre kesilir (yakın hastaneler ilk partilerde) — ilk sonuçlar en çok işe yarayanlar olur.
- Tüm ajanlar **tek mesajda**, birden çok `Agent` tool çağrısıyla başlatılır; arka planda çalışırlar.
- Ajan tipi: `general-purpose` (WebSearch + WebFetch erişimi olan).
- Bir ajan API/oturum limiti nedeniyle düşerse **yeniden başlatılmaz** — `SendMessage` ile kaldığı yerden sürdürülür; toplanmış veri korunur.
- Her partinin dönen JSON'u geldiği anda diske yazılır (oturum kesilirse kaybolmasın).
- Ajan çıktısı sohbete basılmadan önce diske alınır; birleştirme `birim` adı üzerinden birebir, tutmazsa bulanık eşleşmeyle yapılır.

## Prompt şablonu

Aşağıdaki metin, `{{HASTANE_LISTESI}}` ve `{{BUGUN}}` doldurularak her ajana verilir.

---

Türkiye'deki şu {{N}} devlet hastanesi için iki bilgiyi web'den bul (bugün: {{BUGUN}}):

{{HASTANE_LISTESI}}

Her hastane için:

**A) `bc_uzman`** — Hâlen görevli {{BRANS}} uzmanı sayısı. Kaynak önceliği:
1. Hastanenin resmî sitesi (genellikle `<hastane>.saglik.gov.tr`) "Hekimlerimiz" / "Doktorlarımız" / branşa özel sayfası — WebFetch ile açıp hekimleri **tek tek say**
2. `trhastane.com`, `doktortakvimi.com`, `doktorsitesi.com` gibi MHRS agregatörlerinde hastane + branş listesi
3. Güncel haber (atama/ameliyat haberleri)

**B) `ameliyathane`** — Hastane genelinin toplam ameliyathane/ameliyat salonu sayısı. Kaynak: resmî "Hastanemiz"/"Ameliyathane" sayfası, KHGM künyesi, açılış haberleri ("X ameliyathane").

**KURALLAR:**
- Bulamadığın alanı `null` bırak — **TAHMİN ETME**, başka hastanenin verisini yazma.
- Uzman sayısı için `0` ile `null` farklıdır: `0` = kaynağa baktım, o branşta hekim yok; `null` = doğrulanabilir kaynak bulamadım.
- Yalnız Sağlık Bakanlığı devlet hastanesi; **özel hastaneyle karıştırma**.
- **Yapımı süren yeni hastane projesinin salon sayısını mevcut binaya yazma.** (Rize 45, Şırnak 22, Iğdır 15, Çankırı 12 — hiçbiri açılmadı.)
- Aktif ve toplam salon farklıysa **aktif** olanı yaz, toplamı nota geçir.
- Resmî site ile haber çelişirse **tarihi yeni olanı** al ve çelişkiyi nota yaz.
- Agregatör listeleri bayat olabilir; resmî site varsa o önceliklidir.
- Sayfa güncelleme tarihini gördüysen nota yaz.

Final cevabın **SADECE** şu JSON dizisi olsun (başka metin, yorum, başlık ekleme):

```json
[{"birim": "<tam ad yukarıdaki gibi>", "bc_uzman": null, "bc_kaynak": null,
  "ameliyathane": null, "am_kaynak": null, "not": null}]
```

---

## Çıktı şeması

| Alan | Tip | Anlam |
|---|---|---|
| `birim` | string | Hastane adı — verilen listedeki hâliyle, değiştirilmeden |
| `bc_uzman` | int \| null | Hâlen görevli uzman sayısı (`0` meşru bir değer) |
| `bc_kaynak` | url \| null | Sayının okunduğu sayfa |
| `ameliyathane` | int \| null | Toplam salon sayısı |
| `am_kaynak` | url \| null | Sayının okunduğu sayfa |
| `not` | string \| null | Tarih, çelişki, aktif/toplam farkı, güvenilirlik uyarısı |

## Birleştirme sonrası kapsam raporu

Tüm partiler döndükten sonra kullanıcıya bildirilir:
- Kaç hastanede uzman sayısı dolu / `null`
- Kaç hastanede ameliyathane dolu / `null`
- Çelişki notu taşıyan kayıtlar
- Önceki tarama dosyası varsa değişen değerler (`önceki: X → şimdi: Y`)
