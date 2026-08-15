# Paralel Tarama Ajanı Şablonu

Uzman ve ameliyathane sayıları her çalıştırmada web'den taze toplanır. Tek tek aramak
88 hastane için çok yavaş olduğundan iş **10'arlı partilere** bölünüp paralel ajanlara verilir.

> ⚠️ **Bu dosyayı ajanın kendisi okur.** Ana thread aşağıdaki görev metnini prompta kopyalamaz —
> ajana yalnızca kısa bir yönerge verir (bkz. "Ana thread ne yapar"), ajan bu dosyayı `Read` ile
> açıp kurallara uyar. Böylece şablon parti sayısı kadar tekrar yazılmaz.

## Ana thread ne yapar

- Partiler mesafe sırasına göre kesilir (yakın hastaneler ilk partilerde) — ilk sonuçlar en çok işe yarayanlar olur.
- Tüm ajanlar **tek mesajda**, birden çok `Agent` tool çağrısıyla başlatılır; arka planda çalışırlar.
- Ajan tipi: `general-purpose` — `WebSearch`, `WebFetch`, `Read` ve `Write` erişimi gerekir.
- Her ajana verilen prompt yalnızca şudur:

```
C:\Users\onurd\.claude\skills\dhyuzmani\references\dhyuzmani-r-ajan-sablonu.md dosyasını oku ve
"Ajan görevi" bölümündeki kurallara birebir uy.

Parti: 03/09
Bugün: {{BUGUN}}
Branş: {{BRANS}}
Çıktı dosyası: <tmp>/parti_03.json
Hastaneler:
{{HASTANE_LISTESI}}
```

- Bir ajan API/oturum limiti nedeniyle düşerse **yeniden başlatılmaz** — `SendMessage` ile kaldığı
  yerden sürdürülür; yarım yazılmış parti dosyası korunur, ajana "dosyadaki kayıtları koru, eksik
  hastaneleri tamamla" denir.
- **Ana thread parti JSON'larını sohbete basmaz ve elle diske yazmaz** — dosyayı ajan yazar,
  birleştirmeyi `dhyuzmani_excelbas.py --tarama <klasör>` yapar.

---

## Ajan görevi

*(Aşağısı ajana hitap eder. Ajan bu bölümü okuduktan sonra doğrudan uygular.)*

**Adım 0 — tuzakları oku.** Bu dosyayla aynı klasördeki `dhyuzmani-r-veri-kaynaklari.md` dosyasının
**§1 (uzman sayısı)** ve **§2 (ameliyathane)** bölümlerini `Read` ile aç. Kaynak öncelik sırası,
bayat agregatör emsalleri ve **yapımı süren (henüz açılmamış) hastane projelerinin tam listesi**
oradadır — tek doğru kaynak odur, buraya kopyalanmaz.

Sonra prompttaki her hastane için iki bilgiyi web'den bul (bugünün tarihi prompttadır):

**A) `bc_uzman`** — Hâlen görevli, prompttaki branşın uzmanı sayısı. Kaynak önceliği:
1. Hastanenin resmî sitesi (genellikle `<hastane>.saglik.gov.tr`) "Hekimlerimiz" / "Doktorlarımız" / branşa özel sayfası — WebFetch ile açıp hekimleri **tek tek say**
2. `trhastane.com`, `doktortakvimi.com`, `doktorsitesi.com` gibi MHRS agregatörlerinde hastane + branş listesi
3. Güncel haber (atama/ameliyat haberleri)

**B) `ameliyathane`** — Hastane genelinin toplam ameliyathane/ameliyat salonu sayısı. Kaynak: resmî
"Hastanemiz"/"Ameliyathane" sayfası, KHGM künyesi, açılış haberleri ("X ameliyathane").

**KURALLAR:**
- Bulamadığın alanı `null` bırak — **TAHMİN ETME**, başka hastanenin verisini yazma.
- Uzman sayısı için `0` ile `null` farklıdır: `0` = kaynağa baktım, o branşta hekim yok; `null` = doğrulanabilir kaynak bulamadım.
- Yalnız Sağlık Bakanlığı devlet hastanesi; **özel hastaneyle karıştırma**.
- **Yapımı süren yeni hastane projesinin salon sayısını mevcut binaya yazma** — açılmamış projeler `dhyuzmani-r-veri-kaynaklari.md` §2'deki tablodadır.
- Aktif ve toplam salon farklıysa **aktif** olanı yaz, toplamı nota geçir.
- Resmî site ile haber çelişirse **tarihi yeni olanı** al ve çelişkiyi nota yaz.
- Agregatör listeleri bayat olabilir; resmî site varsa o önceliklidir.
- Sayfa güncelleme tarihini gördüysen nota yaz.

**Çıktı — iki parça:**

1. Kayıtları `Write` ile prompttaki **çıktı dosyasına** yaz (UTF-8, tek JSON dizisi, başka metin yok).
   `birim` alanı prompttaki adın **birebir** aynısı olsun:

```json
[{"birim": "<tam ad yukarıdaki gibi>", "bc_uzman": null, "bc_kaynak": null,
  "ameliyathane": null, "am_kaynak": null, "not": null}]
```

2. Sohbete dönen final cevabın **yalnız tek satırlık özet** olsun — JSON'u tekrarlama:

```
parti_03.json yazıldı — 10 kayıt | uzman 8 dolu / 2 null | ameliyathane 6 dolu / 4 null | çelişki: Ağrı EAH
```

Çelişki yoksa son alan `çelişki: yok` yazılır. Dosyayı yazamadıysan bunu açıkça bildir.

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

Parti dosyaları `dhyuzmani_excelbas.py --tarama <parti klasörü>` ile birleştirilir; script birleşik
JSON'u `output/json/` altına yazar ve eşleşme sayısını basar. Ana thread sonra kullanıcıya bildirir:

- Kaç hastanede uzman sayısı dolu / `null`
- Kaç hastanede ameliyathane dolu / `null`
- Çelişki notu taşıyan kayıtlar (ajan özet satırlarından toplanır)
- Önceki tarama dosyası varsa değişen değerler (`önceki: X → şimdi: Y`)
