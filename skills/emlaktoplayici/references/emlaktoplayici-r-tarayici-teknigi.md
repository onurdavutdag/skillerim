# Tarayıcı tekniği — ölçülmüş sınırlar

Buradaki her satır **14 Ağustos 2026'da canlı ölçüldü**. Tahmin yok; ölçülmemiş olan açıkça öyle yazar.
Bir sınır yeniden ölçülürse bu dosya güncellenir ve ölçüm tarihi değiştirilir.

## 1. Araç sınırları (site bağımsız)

| Sınır | Ölçüm | Sonuç |
|---|---|---|
| `javascript_tool` süresi | **45 sn** CDP timeout | Her çağrı <40 sn tasarlanır. Uzun toplama tek çağrıya sığdırılmaz, parçalanır |
| Tool çıktısı | ~**1.200 karakter** | Veri `return` ile dışarı taşınmaz — tarayıcıda biriktirilir, sonunda toplu aktarılır |
| Toplu aktarım | `clipboard.writeText` + PowerShell `Get-Clipboard -Raw` | ⛔ **15.08.2026'da çalışmadı** — aşağı bak |
| İlerleme kalıcılığı | Sekme yenilenince `window` üzerindeki her şey uçar | Her partide `localStorage`'a yazılır; kaza sonrası kaldığı yerden sürer |
| Bağlantı kopması | Uzantı bağlantısı koptuğunda çağrı **hata döner ama sayfada çalışmıştır** | Toplayıcı **idempotent** olmalı: kayıt `ilan_no` anahtarıyla eklenir, yeniden deneme çift yazmaz |

> **Neden idempotentlik pazarlık konusu değil:** 15.08.2026 emlakjet koşusunda uzantı bağlantısı 3.
> sayfada bir kez koptu; hata dönen çağrı sayfada **zaten çalışmıştı** ve masum görünen bir yeniden
> deneme 30 kaydı sessizce ikinci kez yazdı. Diziye `push` eden bir toplayıcı bunu fark etmez;
> `ilan_no` anahtarlı sözlüğe yazan toplayıcı için aynı kaza zararsızdır.

### ✅ Toplu aktarımın doğru yolu: `<pre>` + `get_page_text` — 15.08.2026'da ölçüldü

Üç kanalın ölçülmüş taşıma kapasitesi:

| Kanal | Ölçüm | Sonuç |
|---|---|---|
| `javascript_tool` dönüşü | ~**1.180 karakter**te kesiliyor | tek ilanlık kayıt taşır, toplu veri taşımaz |
| `read_page` | metin düğümlerini **100 karaktere** kırpıyor | uzun açıklama için kullanılamaz |
| **`<pre>` + `get_page_text`** | **33 KB tek çağrıda** çıktı | toplu aktarımın yolu budur |

Kalıp: toplanan veri sayfada bir `<pre>` düğümüne JSON olarak yazılır, sonra `get_page_text` çağrılır.
hepsiemlak koşusunda ~30 parçalı çıkarma turunu **1 çağrıya** indirdi.

```js
const el = document.createElement('pre');
el.id = 'emlak_dump';
el.textContent = JSON.stringify(Object.values(toplanan));
document.body.replaceChildren(el);   // sayfayi sadelestir, get_page_text yalniz bunu gorsun
```

### İki ek hız tekniği (aynı koşuda ölçüldü)

- **Uzun döngüyü `await` etmeden başlat, sonra yokla.** `javascript_tool`'un 45 sn CDP timeout'u
  böylece hiç devreye girmiyor: döngü `window.__durum` yazar, sonraki kısa çağrılar onu okur.
- **Aynı sekmede `fetch` + `DOMParser`** — hepsiemlak SSR HTML döndürdüğü için sayfa sayfa gezmeye
  gerek kalmadı. ⚠️ Bu **sahibinden'de yasaktır** (ölçülmüş blok sebebi, §2). hepsiemlak'ta da bedavaya
  gelmedi: 72 sayfanın 60. ve 70.'i **HTTP 429** döndü. Yani `fetch` yolu hızlıdır ama hız tavanını
  ortadan kaldırmaz — büyük envanterde araya duraklama konur.

### ⛔ Pano yolu güvenilmez — 15.08.2026'da ölçüldü

Detay taraması sırasında hem `navigator.clipboard.writeText(...)` hem de yedek olarak
`document.execCommand('copy')` **`Document is not focused`** ile düştü. Sekme arka planda olduğu için
sayfa panoya yazma iznini alamıyor; otomasyon sekmesi neredeyse her zaman arka plandadır. Yani bu yol
"bazen çalışan" değil, bu iş için **yapısal olarak yanlış**.

**Yerine: ilan başına küçük dönüş + ajanın kendi yazması.** Toplanan kayıt tarayıcıda biriktirilmez,
her ilanda `javascript_tool` dönüşüyle **tek ilanlık kompakt JSON** alınır (~1.200 karakter sınırının
altında kalır) ve ajan onu `Write`/`Bash` ile diskteki sözlüğe ekler. Ölçek sorunu yok: zaten ilan
başına 25-30 saniye bekleniyor, bir tool çağrısı daha maliyet değil.

Açıklama uzunsa dönüş sınırını aşabilir; o zaman açıklama tek başına ikinci bir çağrıyla, gerekiyorsa
parça parça alınır (`slice`).

```js
// ilan sayfasindayken: tek ilanlik kompakt kayit dondur
JSON.stringify({ilan_no, tapu_durumu, bina_yasi_bant, toplam_kat, isitma,
                aciklama: aciklama.slice(0, 900)})
```

`localStorage` yine de yazılır (sekme yenilenirse kaza kurtarma), ama **birincil kanal değildir** —
diske yazan taraf ajandır.

## 2. Site başına hız tavanı

| Site | İşlem | Ölçüm | Kural |
|---|---|---|---|
| **sahibinden** | liste sayfası | 3-5 sn arayla sorunsuz | ≥3 sn bekle, `pagingSize=50` ile sayfa sayısını azalt |
| **sahibinden** | detay sayfası | `fetch` ile **5. istekte HTTP 429**; ısrar edilince oturum `/olagan-disi-kullanim`'a düştü. 15.08.2026: gerçek gezinti + 12,5-16,5 sn aralıkla bile **10. ilanda blok** | **XHR/`fetch` kullanılmaz.** Gerçek gezinti, **≥25-30 sn** + rastgele sapma |
| **hepsiemlak** | liste | 3 sn aralıkla 72 sayfada **sayfa 60 ve 70'te HTTP 429** (15.08.2026); aynı iki sayfa ertesi geçişte 5 sn aralıkla temiz | 40+ sayfalık işlerde araya duraklama koy |
| **hepsiemlak** | **detay** | 15.08.2026: **80 ilan**, 8-10 sn aralık + her 20 ilanda ~30 sn durak, **hiç blok işareti yok** | 8-10 sn; blok işaretinde 25-30 sn'ye çık |
| **emlakjet** | liste | 14.08 ve 15.08.2026'da engel görülmedi | ≥3 sn yeterli |
| **emlakjet** | **detay** | 15.08.2026: 16 ilan, sondaj 8-10 sn → kalanı 10-12 sn, **hiç blok işareti yok** | Sondajla başla, temizse hızlan |

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

### 15.08.2026 koşusu — 12-15 sn tavanı yetmedi

14.08 akşamı blok yendikten ~11 saat sonra, kuralına harfiyen uyan bir geçiş denendi: yalnız `navigate`
ile üst düzey gezinti, iframe yok, fetch yok, tek ajan, ölçülen aralık 12,5-16,5 sn. **10. ilanda
(`1291619981`) yine `/olagan-disi-kullanim`.** İlk 9 ilan eksiksiz toplandı (altı alanın altısı da dolu).

Çıkarım: 12-15 sn tavanı **detay sayfası için yeterli değil** — 14.08'de ölçülen o değer liste
sayfasından türetilmişti ve detay tarafında iki kez sınandı, ikisinde de blok geldi. Sayaç ayrıca
oturumlar arasında sıfırlanmıyor olabilir (bir gün önceki blok izi taşınıyor).

**Sonraki geçişin kuralı:** aralık **25-30 sn** + rastgele sapma, her 10 ilanda bir ~60 sn ek duraklama,
blok gelirse **en az 2 saat** beklenir (30 dk yetmedi — 11 saat sonra bile 10 ilanda düştü, yani asıl
değişken bekleme değil **hız** olabilir). 141 ilan bu tempoda ~70-80 dakikadır; süre kullanıcıya baştan
söylenir ve bölünerek koşulabilir.

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

### hepsiemlak — ✅ liste + detay ölçüldü

```
https://www.hepsiemlak.com/<konum>-satilik/daire?page=<N>
```

- Hatay: **72 sayfa / 1.707 ilan / ~24 kart** per sayfa (15.08.2026; envanter günden güne oynar,
  sayıyı ajan kendisi sayar)
- Kart `article`; alanlar `.listingCard__title`, `.listingCard__price`, `.listingCard__date`,
  `.listingCard__location` (`"Hatay / Arsuz / Karaağaç Şarkonak Mah."`)
- Nitelikler `.listingCard__spec-item` + `.listingCard__spec-label`:
  `Kategori · Oda Sayısı · Brüt m² · Bina Yaşı · Kat`
- **Bina yaşı KESİN gelir**: `"20 Yaşında"`, `"Sıfır Bina"` — sahibinden'in bandının aksine tam sayı.
  Deprem skoru amaçsa bu site birinci tercihtir.
- ⛔ **Fiyat filtresi URL'den uygulanamıyor.** `priceMin`/`priceMax` input adları var; URL parametresi
  olarak verilince **kabul edilip yok sayılıyor** (toplam değişmiyor). Sentetik `input`/`change`
  olayı + "Ara" tıklaması da URL'i değiştirmedi.
  → **Çözüm:** filtreyi siteye uygulatma; tüm sayfaları çek, elemeyi yerelde yap (72 sayfa ≈ 4-5 dk).
- ✅ **Detay sayfası ölçüldü (15.08.2026):** spec tablosu `table.property-spec-table tr.spec-item`
  (`th` = etiket, `td` = değer; `İlan no` / `Tapu Durumu` / `Kat Sayısı` / `Bulunduğu Kat` /
  `Bina Yaşı` / `Isınma Tipi`), açıklama `.description-content` (`innerText` tam metni verir).
  Detay hız tavanı: **80 ilan, 8-10 sn + her 20 ilanda ~30 sn durak, hiç blok işareti yok**.
  Detay yalnız açıklama + toplam kat için gerekir — bina yaşı zaten listede.

### emlakjet — ✅ liste + detay ölçüldü

```
https://www.emlakjet.com/satilik-daire/<konum>?sayfa=<N>
```

- Hatay: **169 ilan** (üç site içinde en küçük envanter), sayfa başına 30 kart
- Kart sarmalayıcı `.listing-row-card-media` — **30/30 ayrışıyor** (doğru okuma yöntemiyle)
- ⛔ **`innerText` kullanılmaz — 30 karttan 20'sinde boş döner.** `textContent` 30/30 dolu.
  Kartlar görünür (`display:flex`, `offsetHeight:168`) ve sayfayı sona kaydırmak hiçbir şeyi
  değiştirmiyor — **tembel yükleme değil**. İlk ölçümde "10/30 ayrıştı" sanılmasının sebebi buydu;
  sarmalayıcı baştan beri doğruymuş.
- `textContent` de satır sonu vermez, alanlar yapışır. Çözüm **metin bölmek değil, eleman okumak**:
  başlık = `a[href*="/ilan/"]` bağları içinde metni **en uzun** olan (ilki rozet olabiliyor),
  konum = karttaki `p`, nitelikler = `span`'ler (`·` atılır, kalanlar **kalıba göre** eşlenir:
  `^\d+(\.\d+)?\+\d+$` oda — `1.5+1` de gelir, `m²` alan, `Kat` kat, `\d{2}\.\d{2}\.\d{4}` tarih,
  `₺` fiyat).
  Kalıp eşleme sırayla eşlemeden güvenlidir — bir alan eksikse diğerleri kaymaz.
- **Bina yaşı genel olarak YOK**; yalnız `"SIFIR BİNA"` rozeti varsa yaş = 0
- ⛔ **Fiyat filtresi URL'den uygulanamıyor — 15.08.2026'da ölçüldü.** `?min_fiyat=&max_fiyat=` sessizce
  yok sayılıyor (toplam 169'da kalıyor, 1.850.000 ve 3.550.000 TL'lik ilanlar listede duruyor); sayfada
  min/max fiyat girdisi de yok, yalnız `ad-type-group-price_trend` kutucukları var.
  → **Çözüm hepsiemlak'takiyle aynı:** tüm sayfalar çekilir, eleme yerelde yapılır. Envanter küçük
  (6 sayfa ≈ 2 dk). 15.08 koşusunda 169 ilandan **16'sı** 2.800.000-3.000.000 aralığındaydı.
- `?sayfa=1` temel URL'e yönlenir — ilk sayfa için parametre eklemeye gerek yok
- Kart metnindeki `"4. Kat"` sayıya çevrilir (`Zemin` = 0, `Bodrum` = -1); çevrilemiyorsa `null`
- ✅ **Detay sayfası ölçüldü (15.08.2026):** ayrı bir DOM seçicisine gerek yok — `get_page_text`
  tek çağrıda "İlan Bilgileri" gridini, alt listeyi (Tapu / Isıtma / Kat Sayısı) ve açıklamayı
  **temiz düz metin** olarak veriyor. Liste kartlarındaki `innerText` tuzağı detay sayfasında **yok**.
  Yedek DOM yolu: `ul.grid.grid-cols-1 > li > span` çifti, `div.mb-5.grid.grid-cols-2 > div.flex`,
  açıklama için `h2` "Açıklaması" + `nextElementSibling`. Ayrıntı ajan promptunda.
- Detay hız tavanı: 16 ilan **9-10 sn** aralıkla, blok yok

> **Kural:** ⚠️ etiketli hiçbir alan üretimde varsayılmaz. Ajan önce ölçer, ölçtüğünü kendi prompt
> dosyasına geri yazar, sonra kullanır. Ölçemezse o siteyi "taslak" işaretler ve kısmi teslim eder.

## 5. Neden bu maliyet — detay taramasının matematiği

Liste sayfası ilan başına ~0,1 sn'ye mal olur (50 ilan tek sayfada). Detay sayfası site başına
çok farklıdır (üçü de ölçüldü): **sahibinden ≥25-30 sn** (blok riski gerçek, iki denemede de blok),
**hepsiemlak 8-10 sn**, **emlakjet 9-10 sn** — yani en iyi durumda ~100 kat, sahibinden'de
~300 kat pahalı.

Sonuç: **detay alanları yalnız gerçekten isteniyorsa toplanır** ve kullanıcıya süresi baştan söylenir.
hepsiemlak'ta bina yaşı listede geldiği için, deprem skoru asıl amaçsa **önce hepsiemlak taranır** ve
sahibinden detayına hiç inilmeyebilir.
