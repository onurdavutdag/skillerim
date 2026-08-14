# Tarayıcı tekniği — ölçülmüş sınırlar

Buradaki her satır **14 Ağustos 2026'da canlı ölçüldü**. Tahmin yok; ölçülmemiş olan açıkça öyle yazar.
Bir sınır yeniden ölçülürse bu dosya güncellenir ve ölçüm tarihi değiştirilir.

## 1. Araç sınırları (site bağımsız)

| Sınır | Ölçüm | Sonuç |
|---|---|---|
| `javascript_tool` süresi | **45 sn** CDP timeout | Her çağrı <40 sn tasarlanır. Uzun toplama tek çağrıya sığdırılmaz, parçalanır |
| Tool çıktısı | ~**1.200 karakter** | Veri `return` ile dışarı taşınmaz — tarayıcıda biriktirilir, sonunda toplu aktarılır |
| Toplu aktarım | `clipboard.writeText` + PowerShell `Get-Clipboard -Raw` | Çalışır. **Panoyu ezer** — kullanıcıya önceden söylenir |
| İlerleme kalıcılığı | Sekme yenilenince `window` üzerindeki her şey uçar | Her partide `localStorage`'a yazılır; kaza sonrası kaldığı yerden sürer |

### Toplu aktarım kalıbı

```js
// biriktir (her partide)
localStorage.setItem('emlak_ilanlar', JSON.stringify(hepsi));
// aktar (sonunda)
navigator.clipboard.writeText(localStorage.getItem('emlak_ilanlar'));
```

```powershell
Get-Clipboard -Raw | Out-File -Encoding utf8 "output\json\<site> <YYYYAAGG SSDD>.json"
```

## 2. Site başına hız tavanı

| Site | İşlem | Ölçüm | Kural |
|---|---|---|---|
| **sahibinden** | liste sayfası | 3-5 sn arayla sorunsuz | ≥3 sn bekle, `pagingSize=50` ile sayfa sayısını azalt |
| **sahibinden** | detay sayfası | `fetch` ile **5. istekte HTTP 429**; ısrar edilince oturum `/olagan-disi-kullanim`'a düştü | **XHR/`fetch` kullanılmaz.** Gerçek gezinti, **≥12-15 sn** + rastgele sapma |
| **hepsiemlak** | liste | 14.08.2026'da engel görülmedi | sahibinden tavanı uygulanır (temkinli varsayılan) |
| **emlakjet** | liste | 14.08.2026'da engel görülmedi | aynı |

> **Neden `fetch` değil gerçek gezinti:** `fetch` ile atılan istek tarayıcının normal gezinti imzasını
> taşımaz ve arka arkaya çok hızlı gider. Ölçümde beşinci istekte 429 döndü; devam edilince site oturumu
> `/olagan-disi-kullanim` sayfasına kilitledi ve **liste taraması da** kullanılamaz hâle geldi.

### ⛔ iframe de kullanılmaz — 14.08.2026 21:50'de ölçüldü

Detay toplamayı hızlandırmak için gizli `<iframe>` denendi: aynı kaynak olduğu için `contentDocument`
okunabiliyor ve tek `javascript_tool` çağrısında birden çok ilan gezilebiliyordu. **Çalıştı, sonra bloklandı.**

| Deneme | Sonuç |
|---|---|
| Tek iframe ile bir ilan | ✅ 25 alan + açıklama okundu |
| Döngü hâlinde, 12-15 sn aralıkla | ❌ **2. ilanda** `/olagan-disi-kullanim` |

İki sebep birden vardı ve ikisi de ders:

1. **Eşzamanlılık hatası (bizim hatamız).** Çalışan döngü `window.__dur=true` ile durduruldu, 16 sn beklendi,
   sonra bayrak `false`'a çevrilip yeni döngü başlatıldı. Eski döngü o sırada `sleep` içindeydi; uyanınca
   bayrağı yine `false` gördü ve **devam etti**. İki döngü aynı anda istek attı, fiilî aralık yarıya indi.
   → **Durdurma bayrağı geri alınmaz.** Yeniden başlatmada yeni bir bayrak adı (`__dur2`) kullanılır ya da
   döngüye kimlik verilip `if (window.__kosuNo !== benimNo) break` ile eskisi kalıcı olarak susturulur.
2. **iframe'in kendi imzası (asıl sebep).** İlan sayfası `Sec-Fetch-Dest: iframe` ile istenmez — gerçek
   kullanıcı bir ilan detayını çerçeveye almaz. Bu tek başına otomasyon parmak izidir; aralık doğru olsa
   bile şüphelidir.

**Kural: detay sayfasına yalnız üst düzey gerçek gezintiyle girilir** (`navigate` aracı ya da kullanıcı
tıklaması gibi). `fetch` yok, XHR yok, **iframe yok**. Maliyeti ilan başına iki tool çağrısıdır ve bu
maliyet kabul edilir — kestirmenin bedeli saatlerce süren blok olmuştur.

## 3. Blok davranışı ve toparlanma

**Blok işaretleri:** HTTP 429; `/olagan-disi-kullanim` yönlendirmesi; boş dönen kart listesi;
beklenmedik CAPTCHA sayfası.

**Blok görülünce sırasıyla:**

1. **Dur.** Yeniden deneme yapılmaz — ısrar bloğu uzatır.
2. Kaldığın indeksi `localStorage`'a yaz.
3. O ana kadar toplananı diske yaz. Yarım veri de veridir; `atlanan` sayısıyla birlikte teslim edilir.
4. `blok_yedi_mi: true` ve `atlanan: <sayı>` ile geri dön.
5. **~30 dakika** sonra devam edilebilir (ölçülmedi, temkinli tahmin — bunu kullanıcıya böyle söyle).

**CAPTCHA çözülmez.** Hesaba girilmez. Blok aşmak için proxy/UA hilesi denenmez.

## 4. Sayfalama ve seçiciler

### sahibinden — ✅ tam ölçüldü

```
https://www.sahibinden.com/<kategori>/<konum>?price_min=<n>&price_max=<n>&pagingSize=50&pagingOffset=<N>
```

- `pagingOffset` 0, 50, 100 … şeklinde ilerler; `pagingSize=50` en büyük değer
- Kart seçici: `tr.searchResultsItem[data-id]`
- Listede hazır gelen alanlar: **başlık, m², oda, fiyat, ilan tarihi, ilçe/semt** — hepsi liste sayfasından
- Fiyat filtresi URL parametresiyle çalışır ✓
- **Bina yaşı listede YOK** → detay gerekir (150 ilan ≈ 40 dk)

### hepsiemlak — ✅ liste tarafı tam ölçüldü (22:0x)

```
https://www.hepsiemlak.com/<konum>-satilik/daire?page=<N>
```

- Hatay: **71 sayfa / 1.704 ilan / 25 kart** per sayfa
- Kart `article`; alanlar `.listingCard__title`, `.listingCard__price`, `.listingCard__date`,
  `.listingCard__location` (`"Hatay / Arsuz / Karaağaç Şarkonak Mah."`)
- Nitelikler `.listingCard__spec-item` + `.listingCard__spec-label`:
  `Kategori · Oda Sayısı · Brüt m² · Bina Yaşı · Kat`
- **Bina yaşı KESİN gelir**: `"20 Yaşında"`, `"Sıfır Bina"` — sahibinden'in bandının aksine tam sayı.
  Deprem skoru amaçsa bu site birinci tercihtir.
- ⛔ **Fiyat filtresi URL'den uygulanamıyor.** `priceMin`/`priceMax` input adları var; URL parametresi
  olarak verilince **kabul edilip yok sayılıyor** (toplam 1.704'te kalıyor). Sentetik `input`/`change`
  olayı + "Ara" tıklaması da URL'i değiştirmedi.
  → **Çözüm:** filtreyi siteye uygulatma; tüm sayfaları çek, elemeyi yerelde yap (71 sayfa ≈ 4 dk).
- ⚠️ **ÖLÇÜLMEDİ:** detay sayfası seçicileri (bu site için gerekmiyor), hız tavanı

### emlakjet — kısmen ölçüldü (22:0x)

```
https://www.emlakjet.com/satilik-daire/<konum>?sayfa=<N>
```

- Hatay: **169 ilan** (üç site içinde en küçük envanter)
- Kart sarmalayıcı `.listing-row-card-media` — sayfada 30 adet, ama **ayrıştırma 10'unda çalıştı**.
  Sebep doğrulanmadı: ya yanlış katman (metin kardeş elemanda) ya tembel yükleme.
  Ajanın ilk işi sayfayı sona kaydırıp yeniden ölçmek.
- Alanlar tek satırda `·` ile ayrık: `3+1 · 110 m² · 4. Kat · 14.08.2026`; konum `"Hatay, Arsuz"`;
  fiyat `₺` içeren satır; ilan kimliği `a[href*="/ilan/"]` yolunun sonundaki sayı
- **Bina yaşı listede YOK** (doğrulandı)
- ⚠️ **ÖLÇÜLMEDİ:** fiyat filtresi şeması, detay seçicileri, hız tavanı

> **Kural:** ⚠️ etiketli hiçbir alan üretimde varsayılmaz. Ajan önce ölçer, ölçtüğünü kendi prompt
> dosyasına geri yazar, sonra kullanır. Ölçemezse o siteyi "taslak" işaretler ve kısmi teslim eder.

## 5. Neden bu maliyet — detay taramasının matematiği

Liste sayfası ilan başına ~0,1 sn'ye mal olur (50 ilan tek sayfada). Detay sayfası ilan başına
**≥12-15 sn**'dir — 120-150 kat pahalı.

Sonuç: **detay alanları yalnız gerçekten isteniyorsa toplanır** ve kullanıcıya süresi baştan söylenir.
hepsiemlak'ta bina yaşı listede geldiği için, deprem skoru asıl amaçsa **önce hepsiemlak taranır** ve
sahibinden detayına hiç inilmeyebilir.
