# Deprem risk skoru (0-10) — ölçek ve kaynaklar

> **Bu skor bir ÖN ELEME aracıdır, mühendislik değerlendirmesi DEĞİLDİR.**
> Tam uyarı metni §5'tedir ve Excel'e **zorunlu olarak** basılır.

## 1. Bileşenler ve ağırlıklar

Toplam 0-10. Yüksek skor = yüksek risk.

| # | Bileşen | Ağırlık | Girdi |
|:--:|---|:---:|---|
| 1 | Yönetmelik + yapı denetim bandı | **0-3,5** | `bina_yasi` |
| 2 | İlçe hasar yoğunluğu | **0-2,5** | `ilce` |
| 3 | Diri faya uzaklık | **0-2** | koordinat |
| 4 | Sismik tehlike (PGA-475) | **0-1,5** | koordinat |
| 5 | Kat sayısı | **0-1** | `toplam_kat` |
| 6 | İlan metni beyanı | **-1,5 … +3** | `aciklama` + `baslik` |

Ağırlıklar `emlaktoplayici_depremskorla.py` içinde tek bir tablodan okunur; kullanıcı değiştirebilir.

### 1.1 Yönetmelik + yapı denetim bandı (0-3,5)

Bina yaşından yapım yılı çıkarılır, yürürlükteki deprem yönetmeliğine göre bantlanır:

| Yapım yılı | Puan | Gerekçe |
|---|:---:|---|
| ≤1975 | **3,5** | 1975 öncesi; modern deprem yönetmeliği yok |
| 1976-1997 | **3,0** | 1975 ABYYHY yürürlükte ama denetim zayıf |
| 1998-2000 | **2,0** | 1998 yönetmeliği; yapı denetim yasası henüz yok |
| 2001-2006 | **1,5** | **Hatay yapı denetim pilot ilidir** (4708 sayılı yasa, 2001) |
| 2007-2018 | **1,0** | 2007 DBYBHY |
| ≥2019 | **0,5** | 2018 TBDY (01.01.2019 yürürlük) — en güncel |
| bilinmiyor | **boş** | ortalamayla doldurulmaz |

> **2001 eşiği neden Hatay'a özel:** 4708 sayılı Yapı Denetimi Hakkında Kanun 2001'de **19 pilot ilde**
> başladı ve Hatay bu illerden biriydi. Türkiye genelinde zorunluluk 2011'i buldu. Hatay'da 2001 sonrası
> yapılan bina, çoğu ilden farklı olarak denetim kapsamındaydı.

#### Bant hâlinde gelen bina yaşı

sahibinden bina yaşını **tek sayı olarak vermez**, bant verir: `"11-15 arası"`, `"5-10 arası"`,
`"31 ve üzeri"`. Bant `bina_yasi_bant` alanında ham hâliyle saklanır ve skorlayıcı şöyle çözer:

| Durum | Davranış | Örnek (2026) |
|---|---|---|
| Bant tek yönetmelik aralığına tam oturuyor | **Kesin** puan | `11-15` → 2011-2015 → hepsi 2007-2018 → **1,0** |
| Bant iki aralığa yayılıyor | **Yüksek riskli** sınır alınır, `Neden`'e *"bant, üst sınır alındı"* düşer | `5-10` → 2016-2021 → 1,0 ile 0,5 arası → **1,0** |
| Bant ucu açık (`31 ve üzeri`) | En eski ihtimalin puanı | `31+` → ≤1995 → **3,5** |
| Düz sayı da varsa | Sayı bandı **ezer** | `bina_yasi=2` → 0,5 |

> **Neden ortalama değil üst sınır:** ortalama almak interpolasyondur, yani tahmindir — bu skillde yasak.
> İki uçtan birini seçmek gerekiyorsa **yüksek riskli** olan seçilir: bu bir **ön eleme** aracıdır, riski
> fazla göstermek insanı daha yakından bakmaya iter; eksik göstermek ise yanlış güven verir. Seçim
> `Neden` sütununda açıkça yazar, kullanıcı görebilir.

### 1.2 İlçe hasar yoğunluğu (0-2,5)

6 Şubat 2023 depremleri sonrası **kesin hasar tespiti** sayıları. İlçenin
`(yıkık + acil yıktırılacak + ağır)` toplamı, ilçenin **2022 nüfusuna** oranlanır
(bin kişi başına yoğunluk); oran 15 ilçe arasında min-maks ile 0-2,5 aralığına ölçeklenir.

> **Neden nüfus, neden bağımsız bölüm değil:** ilçe düzeyinde toplam bağımsız bölüm sayısı
> kamuya açık değil (bkz. §3). Nüfus, bina stoğunun kamuya açık tek tutarlı vekilidir;
> yoğunluk sıralamasını değiştirmediği ölçekleme min-maks olduğu için sonuç aynı banda oturur.

Veri: `assets/hatay_ilce_hasar.json`. Kaynak künyesi o dosyanın `_kaynak` alanındadır.

> Bu bileşen **bina** değil **bölge** ölçer. Az hasarlı bir ilçedeki kötü bina da, çok hasarlı bir
> ilçedeki sağlam bina da vardır — bu yüzden ağırlığı bina yaşından düşüktür.

### 1.3 Diri faya uzaklık (0-2)

GEM **Global Active Faults** veri setinin Türkiye kırpması (Emre vd. TR verisi, CC-BY).
İlçe/mahalle koordinatından en yakın diri fay hattına kuş uçuşu mesafe:

| Mesafe | Puan |
|---|:---:|
| <1 km | **2,0** |
| 1-3 km | **1,5** |
| 3-10 km | **1,0** |
| 10-25 km | **0,5** |
| >25 km | **0** |

GeoJSON depoda tutulmaz; ilk kullanımda indirilip `~/.claude/.cache/emlaktoplayici/` altına önbelleklenir.

### 1.4 Sismik tehlike, PGA-475 (0-1,5) — ⛔ HESAPLANAMIYOR

Puanlama tablosu tasarlandı ama **besleyecek veri kamuya açık yoldan alınamıyor**. Bileşen boş kalır.

| PGA (g) | Puan |
|---|:---:|
| ≥0,6 | **1,5** |
| 0,4-0,6 | **1,0** |
| 0,2-0,4 | **0,5** |
| <0,2 | **0** |

**14.08.2026'da ne denendi, ne çıktı** (tekrar denenmesin diye kayıtta):

1. TUCBS WMS endpoint'i bulundu: `https://tucbs-public-api.csb.gov.tr/trk_afad_tdth_wms`,
   katman **58 = `TSTH_PGA_475`**.
2. `GetFeatureInfo` **çalıştırıldı**. İki tuzağı var: parametre adları **BÜYÜK HARF** olmalı ve
   **`STYLES=` zorunlu** (boş değer yeterli) — yoksa HTTP 400 `Parameter "STYLES" is required!`.
   `INFO_FORMAT=application/json` çalışıyor, `text/plain` ServiceException veriyor.
   Tam çalışan istek şablonu `assets/tdth_renk_lut.json` → `_calisan_istek`'te.
3. **Ama dönen değer PGA değil, rasterin KIRMIZI KANAL baytı.** Cevaptaki `UNIT` alanı bunu
   açıkça söylüyor: `"RED]"`.
4. **Kanıt:** Antakya (yüksek tehlike) → **207,0**; Erzin (düşük tehlike) → **255,0**.
   Düşük tehlikeli ilçe daha yüksek değer döndürüyor. Tehlike renk rampasında düşük = parlak sarı
   (R=255), yüksek = koyu kırmızı (R<255). Yani tek kanal PGA ile **ters** ve tek başına
   **geri çevrilemez** — iki farklı PGA aynı R'yi verebilir. Servis G ve B bantlarını vermiyor.
5. `GetLegendGraphic` ile renk→etiket tablosu kurulmak istendi → **WAF "Request Rejected"**.
6. AFAD'ın koordinatla **kesin değer** veren resmî sorgusu (`tdth.afad.gov.tr`) **e-Devlet girişi**
   istiyor. Anonim sayısal API **yok**.

> **Sonuç:** bu bileşen boş bırakılır ve skor kalan bileşenlerin azamisine göre ölçeklenir;
> güven `(N/6)` bir eksik yazar. Renk okuyup PGA **uydurulmaz** — ters ve çok-değerli bir eşleme,
> hesaplanmamış bir değerden daha zararlıdır.

### 1.5 Kat sayısı (0-1)

| Toplam kat | Puan |
|---|:---:|
| ≥9 | **1,0** |
| 6-8 | **0,7** |
| 4-5 | **0,4** |
| ≤3 | **0,2** |

Yumuşak kat / ağır üst kat etkisi kabaca yakalanır. Zemin kat ticari kullanımı ayrıca ölçülmez —
ilan verisinde güvenilir biçimde yok.

### 1.6 İlan metni beyanı (-1,5 … +3)

İlan başlığı ve açıklamasında geçen hasar beyanı. Terimler
**22.06.2025 tarih ve 32934 sayılı Resmî Gazete'de yayımlanan yönetmelikte** tanımlıdır:

| Beyan | Puan |
|---|:---:|
| "ağır hasarlı" | **+3,0** |
| "orta hasarlı" | **+2,5** |
| "az hasarlı" | **+0,5** |
| "güçlendirilmiş" / "güçlendirme yapıldı" | **-1,0** |
| "hasarsız" / "hasarsız raporlu" | **-1,5** |
| beyan yok | **0** |

Eşleşme kelime köküne göre yapılır, Türkçe ekler tolere edilir. Birden çok beyan varsa **en ağırı** alınır.

**Olumsuzlama beyanı geçersiz kılar:** "ağır hasar **almamıştır**", "hasar kaydı **yoktur**",
"orta hasarlı **değildir**" beyan sayılmaz ve sert kuralı tetiklemez. Olumsuzlama yalnız
**aynı cümlecikte** (virgül/nokta öncesi, ~25 karakter) aranır — "orta hasarlı, güçlendirme
yapılmadı" ilanında "yapılmadı" güçlendirmeyi olumsuzlar, hasar beyanı ayakta kalır ve sert
kural çalışır. "hasarsız" sözcüğü hasar kalıplarına yakalanmaz (`hasar(?!sız)`).

> **SERT KURAL — beyan skoru ezer:** ilan "orta hasarlı" ya da "ağır hasarlı" diyorsa toplam skor
> **en az 8'e sabitlenir**, diğer bileşenler ne derse desin.
> Gerekçe: orta hasarlı bina yasal olarak **güçlendirilmeden oturulamaz**; ağır hasarlıda satılan şey
> bina değil **arsa payıdır**. Bunlar derece farkı değil, tür farkıdır.

## 2. Eksik veri — sahte kesinlik üretilmez

- Hesaplanamayan bileşen **boş** kalır. Ortalamayla, medyanla veya "tipik değerle" doldurulmaz.
- **Yıl/yaş karışması koruması:** `bina_yasi > 150` ise (ilana yaş yerine yapım yılı yazılmış
  olmalı, ör. `2026`) bileşen hesaplanmaz ve `Neden`'e şüphe notu düşer — 2026 yaşındaki "bina"
  sessizce azami risk almaz.
- `toplam_kat ≤ 0` anlamsız veridir; kat bileşeni hesaplanmaz (alçak bina puanı verilmez).
- Skorun yanına kaç bileşenin hesaplandığı yazılır: **`(4/6 bileşen)`**.
- 3'ten az bileşen hesaplanabiliyorsa skor **hiç üretilmez** — `Yetersiz veri` yazılır.
- Excel'de her bileşen **ayrı sütundur**; kullanıcı hangi bileşenin skoru sürüklediğini görebilir.
- `Neden` sütunu skoru en çok etkileyen 2-3 etkeni düz Türkçeyle yazar
  (ör. *"1994 yapımı (3,0) · Antakya yüksek hasar (2,2) · faya 1,8 km (1,5)"*).

## 3. Kullanılamayan kaynaklar — uydurulmayacak

Bunlar arandı ve **bulunamadı**. Yerlerine tahmin konmaz:

| İstenen | Durum | Sonuç |
|---|---|---|
| Mahalle düzeyinde açık hasar verisi | **Yok.** Yalnız bina düzeyi askı PDF'leri var (ayrı bir ayrıştırma işi) | İlçe düzeyi kullanılır |
| Hatay mikrobölgeleme / sıvılaşma haritası | Kamuya açık **değil** | Bileşen yok |
| `hasartespit.csb.gov.tr` sorgusu | **API'si yok** | Her satıra **adresle sorgulama linki** konur, otomatik sorgulanmaz |
| Binanın gerçek yapı denetim dosyası | Kamuya kapalı | Yapım yılı bandı vekil olarak kullanılır |

## 4. Skor bantları

| Skor | Etiket | Anlam |
|---|---|---|
| 0,0-2,5 | Düşük | Yeni yönetmelik + düşük hasarlı bölge |
| 2,6-4,5 | Orta-düşük | — |
| 4,6-6,5 | Orta | — |
| 6,6-8,0 | Yüksek | — |
| 8,1-10,0 | Çok yüksek | Hasar beyanı olan her ilan burada |

## 5. Zorunlu uyarı metni

Excel'in **Özet** ve **Künye** sayfalarına, kullanıcıya verilen özete ve bu skorun geçtiği her rapora
aynen basılır:

> **Deprem risk skoru bir ön eleme aracıdır, mühendislik değerlendirmesi değildir.**
> Kamuya açık ilan verisi ve bölgesel verilerden hesaplanır; binanın kendisi incelenmemiştir.
> Satın alma öncesi şunlar **şarttır**: adresle hasar tespit sorgusu, tapuda "riskli yapı" şerhi kontrolü,
> ruhsat ve iskân yılının belgeyle doğrulanması, yapı denetim dosyasının incelenmesi ve gerekirse
> bir inşaat mühendisinden yapısal değerlendirme alınması.
> **Skorun 0 olması binanın güvenli olduğu anlamına gelmez.**
