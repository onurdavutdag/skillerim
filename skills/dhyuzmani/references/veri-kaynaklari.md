# Veri Kaynakları ve Bilinen Tuzaklar

11 Ağustos 2026'da 88 hastane taranırken öğrenilenler. Yeniden keşfi pahalı olduğu için burada tutulur.

---

## 1. Beyin cerrahisi uzman sayısı

### Kaynak öncelik sırası

| Sıra | Kaynak | Nasıl |
|:---:|---|---|
| 1 | **Hastane resmî sitesi** | `<hastane>.saglik.gov.tr` → "Hekimlerimiz" / "Doktorlarımız" / branşa özel sayfa. WebFetch ile açılıp **isimler tek tek sayılır** |
| 2 | **MHRS agregatörleri** | `trhastane.com`, `doktortakvimi.com`, `doktorsitesi.com` — hastane + branş doktor listesi |
| 3 | **Güncel haber** | Yerel basın atama haberleri, ameliyat haberleri (ekip adlarıyla) |

Resmî site adresi genellikle şu kalıpta: ilçe/hastane adının sadeleşmiş hâli + `dh` veya `eah` + `.saglik.gov.tr`
(`golcukdh`, `bodrumdh`, `kastamonueah`, `vaneah`, `mehmetakifinaneah`).

### Tuzaklar

- **Agregatör listeleri bayat olabilir.** Geçmişte görev yapan hekimler listede kalır. Örnek: Ağrı EAH için `doktorsitesi` üç isim veriyordu, üçü de artık Sakarya/Manisa/Ankara'da. Mardin Nusaybin için 7 isim listeleniyordu, güncel sayı 1.
- **Resmî site de eski olabilir.** Sayfa güncelleme tarihine bakılır. Karabük EAH listesi 2023, Hatay Defne listesi 24.11.2023 tarihliydi.
- **Resmî site ile haber çelişirse tarihi yeni olan esas alınır ve nota yazılır.** Emsal: Ağrı EAH — resmî site 1 hekim, Nisan 2026 haberi 4 kişilik ekibi adlarıyla veriyordu; 4 alındı, çelişki not sütununa geçti.
- **Aynı hekim iki hastanede görünebilir** (görevlendirme). Hatay EAH ve Defne DH listelerinde ortak isim vardı — ayrı ayrı sayılır, nota düşülür.
- **Özel hastaneyle karıştırma.** Yalnız Sağlık Bakanlığı devlet hastaneleri sayılır (ör. Karabük'te Özel Medikar, Çaycuma'da Özel Sevgi Tıp Merkezi kapsam dışı).
- **Sıfır meşru bir cevaptır.** Kadro açılmış ama uzman göreve başlamamış olabilir: Şanlıurfa Birecik, Şırnak İdil, Tokat Zile, Adıyaman Kahta bu durumdaydı. `0` ile `null` farklıdır — `0` = "baktım, yok", `null` = "doğrulanabilir kaynak bulamadım".
- Bazı resmî siteler hekim listesini **yalnız kurum içi ağdan** verir (Erzurum ŞH) veya HTTP 500 döner (Şanlıurfa EAH). O zaman 2. ve 3. kaynağa inilir, nota yazılır.

---

## 2. Ameliyathane (salon) sayısı

"Ameliyat masası" ayrı bir veri olarak yayımlanmaz; hastaneler **"X ameliyathane / ameliyat salonu / ameliyat odası"** bildirir. Aranan budur.

### Kaynaklar

- Resmî site "Hastanemiz" / "Hakkımızda" / "Ameliyathane" sayfası (en güvenilir)
- Şehir hastaneleri için **KHGM resmî künyesi**: `khgm.saglik.gov.tr` ve `khgmsehirhastaneleridb.saglik.gov.tr` hastane sayfaları
- Yeni bina açılış haberleri (AA, valilik, belediye), yüklenici firma proje sayfaları

### Tuzaklar

- **Yapımı süren hastane projesinin salon sayısı mevcut binaya yazılmaz.** Bu hata en sık yapılan hatadır. 11.08.2026 itibarıyla açılmamış projeler:

  | Yer | Projedeki salon | Durum |
  |---|:---:|---|
  | Rize (900 yataklı yeni hastane) | 45 | 2027 hedefi |
  | Şırnak (500 yataklı bölge hastanesi) | 22 | inşaat |
  | Iğdır (600 yataklı) | 15 | inşaat |
  | Çankırı (400 yataklı) | 12 | inşaat |
  | Kırklareli EAH ek bina | +11 (6→17) | inşaat %33 |
  | Hakkari (100 yataklı, Biçer Mah.) | 6 | yıl sonu hedefi |

- **Aktif ve toplam salon farklı olabilir.** Van EAH: 32 toplam ameliyat odası, 26'sı aktif. Aktif sayı yazılır, toplam nota geçer.
- **Açılış tanıtımı eski kalabilir.** Erciş (2018), Kastamonu (~2017), Gediz (~2017) rakamları bina açılışı dönemine ait; resmî sitede güncel teyit yoksa nota yazılır.
- İlçe hastaneleri salon sayısını çoğunlukla **hiç yayımlamaz** — 88 hastanede 58 dolu, 30 `null` kaldı. Bu normaldir, uydurulmaz.

---

## 3. Yatak kapasitesi (yerel, taranmaz)

**Kaynak:** KHGM "Kamu Hastaneleri Genel Müdürlüğüne Bağlı 2. ve 3. Basamak Kamu Sağlık Tesisleri Güncel Listesi", **02.02.2023** tarihli.
İndirme: `https://dosyamerkez.saglik.gov.tr/Eklenti/45020/0/saglik-tesisleri-listesi-02022023xls.xls`
Sayfa: `GÜNCEL TABLO ` — sütunlar: SIRA NO, KURUM KODU, İL, İLÇE, KURUM ADI, E.A.H, KURUM TÜRÜ, Ünite, Rol, **Tescil Edilen Yatak Sayısı** (10. sütun, indeks 9). `.xls` olduğu için `xlrd` gerekir.

Türetilmiş 88 birimlik eşleşme `assets/yatak_map.json` içindedir; script önce oraya bakar, indirme yalnız yeni hastane çıkarsa yapılır.

### Tuzaklar

- **Liste 6 Şubat 2023 depreminden öncedir.** Hatay ve Kahramanmaraş'ta fiilî kapasite tescilden sapar. Kahramanmaraş Necip Fazıl ŞH'nin 600 yataklı yeni binası Haziran 2025'te açıldı.
- Listede olmayan, sonradan açılan hastaneler web'den doğrulanıp haritaya eklendi:

  | Hastane | Yatak | Kaynak |
  |---|:---:|---|
  | Hatay Defne DH | 300 | AA, Mayıs 2023 açılış |
  | Gaziantep Şehir H. | 1875 | resmî site, 2024 |
  | Erzurum Şehir H. | 1670 | AA, 2020 |
  | Kahramanmaraş DH | 400 | Valilik, Şubat 2025 |

  ⚠️ **12.08.2026 mutabakatı:** haritanın bu dört değerden saptığı görüldü (Defne 50,
  Gaziantep ŞH 365, Erzurum ŞH 1570, K.Maraş DH 1055 — sonuncusu Necip Fazıl tescilinin
  bulanık-eşleşme kopyası). Değerler bu tabloya eşitlendi; sapma bir daha sessiz kalmasın
  diye `dhyuzmani_dogrula.py` bu dört kaydı her koşuda denetler.

- Kurum adları listede "T.C. Sağlık Bakanlığı ..." önekiyle ve **ilçe adıyla** geçer ("Kahta Devlet Hastanesi"), kura listesinde ise il önekiyle ("ADIYAMAN KAHTA DEVLET HASTANESİ"). Eşleştirme bu yüzden bulanık (fuzzy) + ilçe ipucu ile yapılır.

---

## 4. Karayolu mesafesi (yerel, taranmaz)

**Kaynak:** KGM "İller Arası Mesafe Cetveli", 03.03.2026 tarihli resmî Excel.
İndirme: `https://www.kgm.gov.tr/SiteCollectionDocuments/KGMdocuments/Root/Uzakliklar/ilmesafe.xlsx`
Kopyası `assets/kgm_il_mesafe.xlsx` içindedir. Sayfa `Sayfa1`; satır 2 başlıklar, sütun B il adı, C'den itibaren mesafe matrisi.

Hatay satırından doğrulama değerleri: **Adana 196, Gaziantep 194, Kahramanmaraş 176, Osmaniye 127, Kilis 146, Şanlıurfa 333, İstanbul 1147.**

### İlçe hastaneleri

KGM yalnız il merkezleri arası mesafe verir. İlçe hastaneleri için il değeri çapa alınıp ilçe-il merkezi yol farkı **rota yönüne göre** eklenir/çıkarılır:
- İlçe referans şehre doğruysa çıkarılır (Şanlıurfa Birecik: Urfa 333 − 82 = 251)
- Ters yöndeyse eklenir (Kahramanmaraş Elbistan: Maraş 176 + 158 = 334)

Bu ofsetler `assets/ilce_mesafe.json` içinde **Hatay için doğrulanmıştır** (46 ilçe). Referans şehir değişirse yön bilgisi geçersizleşir; script o durumda il merkezi değerini verip "±N km, yön doğrulanmadı" notu düşer.

İlçe değerleri yaklaşıktır (±%10) ve çıktıda `~` ile işaretlenir.

### İl adı tuzakları

KGM cetvelinde bazı iller parantezli: `KOCAELİ (İZMİT)`, `SAKARYA (ADAPAZARI)`. Script bunları eşler.

---

## 5. Kadro verisi (yerel)

120–129. dönem kura sonuçları `Mart 2027 atama/output/csv/1XX DHY Sonuclar *.csv` içindedir (noter onaylı taramaların OCR çıktısı). Beyin ve Sinir Cerrahisi: **127 kadro / 88 benzersiz birim**.

Projenin bilinen tam yolu (her çalıştırmada aranmasın diye):
`C:\Users\onurd\OneDrive\1) My Files\2) Kişisel\Mart 2027 atama\output\csv`
Taşınmışsa `1[0-9][0-9] DHY*` desenli dosyalar aranarak yeniden bulunur ve bu satır güncellenir.

⚠️ **Bu CSV'ler binlerce hekimin ad-soyadını içerir.** Skill deposuna kopyalanmaz, uzak depoya gönderilmez, artifact'e basılmaz. `dhyuzmani_kadro.py` onları yalnız okur ve hastane düzeyinde toplu çıktı üretir.

OCR kaynaklı birim adı bozuklukları vardır (satır sonuna kaşe/imza artığı eklenmesi). `dhyuzmani_kadro.py` bilinen son eklerden sonrasını keserek normalize eder.
