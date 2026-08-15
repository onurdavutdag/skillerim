# dhyuzmani — Kullanım Kılavuzu

> ## ⚠️ BAKIM KURALI (önce oku)
> **Bu yaşayan bir belgedir.** `SKILL.md`, `references/` veya `scripts/` içinde bir kural
> eklendiğinde, değiştiğinde veya kaldırıldığında bu dosya **aynı değişiklikle** güncellenir.
>
> **Bu skill'e özgü ikinci kural:** `SKILL.md` süreç akışının tek doğru kaynağıdır;
> `references/dhyuzmani-r-veri-kaynaklari.md` veri kaynakları ve tuzakların, `references/dhyuzmani-r-ajan-sablonu.md`
> ise tarama ajanı promptunun tek doğru kaynağıdır. Biri değişince diğerleriyle çelişmediği
> doğrulanır.
>
> _Son güncelleme: 2026-08-15 — tarama ajanı artık şablonu kendi okuyup parti JSON'unu kendi
> yazıyor (sohbete yalnız özet döner), parti birleştirme `dhyuzmani_excelbas.py --tarama <klasör>`
> içine indi, tuzak listesi tek kaynağa (`dhyuzmani-r-veri-kaynaklari.md`) toplandı. Ayrıca script
> ve referans adları N12/N13'e uyduruldu: `_kadrocikar`, `_mesafehesapla`, `_yatakesle`, `_excelbas`
> ve `references/dhyuzmani-r-*.md` (rol artık dosyanın işini söylüyor, referans sahibini taşıyor)._
>
> _2026-08-12 — yatak_map 4 web düzeltmesiyle eşitlendi, TR büyük harf düzeltmesi
> (kadro/mesafe/excel), KHGM indirmesi güvenli hale getirildi, `dhyuzmani_dogrula.py` eklendi._

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
| `dhyuzmani_kadrocikar.py` | Kura CSV klasörü | `kadro.json` | Branşa uyan satırları birim düzeyinde gruplar; OCR kaynaklı ad bozukluklarını normalize eder |
| `dhyuzmani_mesafehesapla.py` | `kadro.json` | `mesafe.json` | İl merkezleri için KGM değeri, ilçeler için doğrulanmış ofset; `~` ile yaklaşıklık işareti |
| `dhyuzmani_yatakesle.py` | `mesafe.json` | `yatak.json` | Yerel haritadan okur; eksik hastane varsa KHGM listesini indirip bulanık eşleşmeyle bulur |
| `dhyuzmani_excelbas.py` | `yatak.json` + tarama JSON **ya da parti klasörü** | `.xlsx` (+ birleşik tarama JSON) | `--tarama` klasör alırsa `parti_*.json`'ları birleştirir (dolu değer null'a yeğlenir, çakışma nota yazılır), sonra hepsini harmanlayıp biçimli Excel üretir (dondurulmuş başlık, filtre, vurgu, Notlar sayfası) |
| `dhyuzmani_dogrula.py` | (isteğe bağlı CSV klasörü) | stdout + çıkış kodu | Öz-denetim: KGM doğrulama değerleri, TR büyük harf, varlık bütünlüğü, 4 web düzeltmesi, kadro 88/127 |

Hepsi bağımsız çalıştırılabilir; `--birim` ile tek hastane sorgusu da yapılabilir.
Kadro, mesafe ve excel scriptleri Türkçe büyük harf çevirisi (`TR_BUYUK`) kullanır —
ASCII `upper()` 'i'yi 'I' yaptığı için "gaziantep" gibi küçük harfli girdiler KGM'deki
"GAZİANTEP" ile eşleşmezdi. KHGM indirmesi geçici ada yapılıp bitince taşınır; yarım
indirme önbelleğe yerleşmez, bozuk önbellek kendini silip yeniden indirme ister.

### Referanslar

| Dosya | İçerik |
|---|---|
| `references/dhyuzmani-r-veri-kaynaklari.md` | Kaynak öncelik sırası, 11.08.2026 taramasında öğrenilen tuzaklar, KGM/KHGM şemaları, doğrulama değerleri |
| `references/dhyuzmani-r-ajan-sablonu.md` | Tarama ajanının görev metni — **ajanın kendisi okur**; ana thread'in vereceği kısa yönerge, çıktı JSON şeması, partileme ve düşen ajanı sürdürme kuralları |

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
kullanılır. Görev metni `references/dhyuzmani-r-ajan-sablonu.md`'dedir ve **ajan onu kendi okur** — ana thread
şablonu 9 kez prompta kopyalamaz.

| Özellik | Değer |
|---|---|
| Ajan tipi | `general-purpose` (WebSearch + WebFetch + Read + Write) |
| Sayı | Hastane sayısı ÷ 10 (88 hastane → 9 ajan) |
| Başlatma | Hepsi tek mesajda, arka planda |
| Girdi | Şablon yolu + parti no + bugün + branş + çıktı dosyası + 10 hastane adı |
| Çıktı (diske) | `parti_NN.json` — `birim, bc_uzman, bc_kaynak, ameliyathane, am_kaynak, not` |
| Çıktı (sohbete) | Tek satır özet: dosya, kayıt sayısı, dolu/null sayıları, çelişki |
| Kısıt | Tahmin yasak; bulunamayan alan `null`; `0` ≠ `null`; tuzaklar `dhyuzmani-r-veri-kaynaklari.md` §1-§2'den okunur |
| Hata | Düşen ajan yeniden başlatılmaz, `SendMessage` ile sürdürülür; yarım parti dosyası korunur |

**Neden adlandırılmış alt ajan yok:** bu kurulumda `skills/<skill>/agents/*.md` dosyaları kayıtlı
ajan tipi değildir (çağıran yine `general-purpose`), `~/.claude/agents/` boştur. Kayıtlı ajan ancak
plugin'e çevirmekle gelirdi; tek kazancı ajana ucuz model atamak olur, karşılığında her oturumun
bağlamına açıklama yazılır ve üç katmanlı senkron yeniden kurulur. 15.08.2026'da bu takas
reddedildi; tasarruf bunun yerine relay'i kesmekten sağlandı.

## 6. Gizlilik ve telif

⚠️ **Kura CSV'leri binlerce hekimin ad-soyadını içerir.** Bu dosyalar:
- Skill deposuna **kopyalanmaz** — scriptler kullanıcının proje klasöründen okur
- Hiçbir uzak depoya, artifact'e veya dış servise **gönderilmez**
- Skill çıktısına yalnız **hastane düzeyinde toplu veri** girer (ad-soyad asla)

`assets/` altındaki KGM ve KHGM verileri kamuya açık resmî veridir; telif riski taşımaz.

## 7. Doğrulama

Skill'de bir değişiklik yapıldığında tek komut yeter:

```bash
cd scripts
python -B dhyuzmani_dogrula.py "<proje>/output/csv"   # CSV klasörü verilmezse yerel kontroller koşar
```

Denetlenenler: KGM doğrulama değerleri (Adana 196, Gaziantep 194, K.Maraş 176, Osmaniye 127,
Kilis 146, Urfa 333, İstanbul 1147), küçük harfli il sorgusu (TR upper), ilçe ofsetlerinin
bütünlüğü (46 kayıt), yatak haritası (88 kayıt, null yok, **4 web düzeltmesi yerinde**),
kadro 88/127 ve kadro↔harita evren eşitliği. Çıkış kodu 0 = hepsi geçti.

Zincirin uçtan uca testi (Excel dahil) hâlâ elle yapılabilir — dört script sırayla
scratchpad'e koşturulur; 88 satırlı, Türkçe karakterleri bozulmamış `.xlsx` beklenir.

Parti birleştirme ayrıca elle sınanır: bir klasöre iki `parti_*.json` konup
`--tarama <klasör>` verilir; mükerrer birimde dolu değerin null'a yeğlendiği ve çakışmanın
`Not` sütununa düştüğü görülür. Tek dosya veren eski kullanım da çalışmaya devam etmelidir.

## 8. Senkron

Bu skill üç katmanda durur (senkron kuralı):

| Katman | Yol |
|---|---|
| Yerel (kaynak) | `Desktop\claude working\skillerim\skills\dhyuzmani\` |
| Global (çalışan) | `~/.claude/skills/dhyuzmani/` — hook aynalar, elle kopyalanmaz |
| GitHub | `github.com/onurdavutdag/skillerim` — içerik aynı oturumda commit + push |
