---
name: bilim-klasoredit
description: >-
  Bir "Bilim ..." proje klasöründeki (ör. Bilim Fare Tümör, Bilim Tez C2) tüm
  dosya ve alt klasörleri 6 üst kategoriye indirger: Introduction,
  Materyal-Method, Result, Discussion-Conclusion, (projeye özgü 5. kategori),
  Diğer. Kullanıcı "6'lar kuralını uygula", "bu şekilde sınıflandır", "proje
  klasörünü düzenle/sınıflandır", "dosyaları kategorilere ayır", "diğer bilim
  dosyalarına da uygula" dediğinde bu skill'i kullan. İşlem sonunda kök dizin
  tam olarak bu 6 klasör + output/ + desktop.ini (varsa) içerir, başka loose
  dosya kalmaz. İlk kullanımda yalnızca 5. kategori ismi ve kategori dilleri
  netleştirilir; sonraki her "Bilim ..." projesinde tekrar sorulmadan doğrudan
  uygulanır.
---

# Bilim Proje Klasörü Sınıflandırma — 6'lar Kuralı

Sunumlarda kullanılan "en fazla 6 madde" kuralının klasör yapısına uyarlanmış
hali. Kaynak: kullanıcı, Bilim Tez C2 emsali Bilim Fare Tümör projesine
uygulanırken, 21 Temmuz 2026.

## 6 kategori

Klasör adının önüne **sıra numarası** eklenir: `1) Introduction`, `2)
Materyal-Method` ... `6) Diğer` — sıra hep bu 1-6 sıralaması, kategori dili
ne olursa olsun. Kaynak: kullanıcı, 21 Temmuz 2026.

1. **Introduction** — saf literatür/arka plan: okunacak/okunan makaleler,
   Bibtex/EndNote referans klasörleri.
2. **Materyal-Method** — yöntem, protokoller, ölçüm/deney görselleri, etik
   kurul başvurusu ve idari belgeler, ilaç/ekipman bilgisi. Derlemeler ve
   format referansı diğer tez/örnek klasörleri de buraya girer (Introduction'a
   değil) — "nasıl yapılacağına ışık tutan" materyal sayılır.
3. **Result** — bulgular/sonuçlar: analiz çıktıları (istatistik çıktıları,
   işlenmiş veri setleri) VE tamamlanmış pilot/ön çalışmaların sonuçları
   (rapor, foto/video, histopatoloji). Proje bu aşamada değilse boş bırakılır.
4. **Discussion-Conclusion** — henüz yazılmadıysa boş bırakılır.
5. **(projeye özgü isim)** — projenin evresine adapte edilir: yazım
   aşamasındaysa "Tez Metni-Sunum" (ana metin, dergi hazırlığı, sunum); veri
   toplama/erken aşamadaysa "Proje Yönetimi-Fon Başvuruları" (BAP, Tübitak,
   masraf/satın alma) gibi. İsim proje için bir kez netleştirilir, aynı
   projede tekrar sorulmaz.
6. **Diğer** — kalıntı/eskimiş/tekrarlanan/dokunulmaması istenen içerik, kökte
   kalan kısayollar.

İşlem bitince kök **tam olarak** bu 6 klasör (numaralı: `1) ...` – `6) ...`)
+ `output/` (ayrı proje kuralı, CLAUDE.md'de, numarasız) + `desktop.ini`
(varsa) içerir.

## İşlem kuralları

- **Kategori dili karışık olabilir.** Kullanıcı proje bazında hangi
  kategorinin hangi dilde olacağını belirtir (ör. Bilim Fare Tümör: 1-4
  İngilizce, 5-6 Türkçe). Kullanıcı aksini belirtmedikçe sonraki "bilim"
  projesinde de aynı dil tercihi varsayılan kabul edilir.
- **Karma içerikli klasörler** (ör. "Diğerleri") içerik türüne göre parçalanır,
  ilgili kategoriye dağıtılır; boşalan klasör silinir.
- **Taşıma = rename/move, kopyala-sil DEĞİL** — aynı birim (aynı disk/OneDrive
  senkron klasörü) içinde yapılır. Özellikle büyük foto/video dosyalarında
  OneDrive'ın yeniden yüklemesini önler.
- **Eski üst-düzey numaralandırma önekleri** (ör. `1) `, `2) `) yeni
  kategoriye taşınırken düşürülür; alt klasörlerin kendi iç numaralandırması
  korunur.
- Başka bir "Bilim ..." proje klasörü için istendiğinde bu kural doğrudan
  uygulanır, yeniden sorulmaz — yalnızca projeye özgü 5. kategori ismi,
  kategori dilleri ve karma klasör parçalama detayı için gerekirse kısa
  netleştirme sorulur.

## Uygulama adımları

1. **Envanter çıkar.** Kök dizini listele (`Get-ChildItem` / `ls`), tüm
   loose dosya ve klasörleri gör.
2. **İlk kullanımdaysa netleştir** (`AskUserQuestion`): 5. kategorinin ismi
   ne olacak, kategori isimleri hangi dil(ler)de olacak. Zaten daha önce bu
   projede netleşmişse (CLAUDE.md/hafızada varsa) tekrar sorma.
3. **Her öğeyi kategoriye ata** — yukarıdaki 6 tanıma göre. Karma klasörleri
   önce aç, içeriğini tek tek dağıt.
4. **Taşıma planını göster** (kaynak → hedef listesi) — özellikle ilk kez
   uygulanan büyük bir projede kullanıcı bir bakışta neyin nereye gittiğini
   görsün. Bilinen/tekrar projelerde bu adım kısa tutulabilir.
5. **Taşı.** Hedef kategori klasörleri numaralı adla oluşturulur (`1)
   Introduction`, `2) Materyal-Method` ...). PowerShell'de aynı birim içi
   taşıma için `Move-Item`:
   ```powershell
   New-Item -ItemType Directory -Force -Path "1) Introduction"
   Move-Item -Path "<kaynak>" -Destination "<numaralı-hedef-kategori>\<yeni-ad>" -Confirm:$false
   ```
   OneDrive "Files On-Demand" ile dehydrate (yalnız bulutta) dosyalarda da
   `Move-Item` içerik indirmeden metadata taşır — sorun çıkarmaz.
6. **Boşalan klasörleri sil**, kökte numaralı 6 kategori + `output/` +
   `desktop.ini` dışında bir şey kalmadığını doğrula.
7. **Opsiyonel envanter notu** — `output/md/İnceleme ... .md` olarak
   sınıflandırmayı belgeleyebilirsin (emsal: Bilim Tez C2); zorunlu değil.

## Emsal projeler

Bilim Tez C2 (önce uygulandı) → Bilim Fare Tümör (Introduction/
Materyal-Method/Result/Discussion-Conclusion İngilizce; 5. ve 6. kategori
Türkçe).

## PDF adlandırma alt-görevi — `bilim-s-pdf` subagent'ı

Introduction veya Materyal-Method'a giren makale PDF'lerinin adı standart
değilse (yazar/yıl/dergi bilgisi adında yoksa), `bilim-s-pdf`
subagent'ı çağrılarak Vancouver-tarzı bir kalıba çevrilebilir:

```
YYYY Soyad. Dergi Adı. Başlık.pdf
```

Bu adım **otomatik/zorunlu değildir** — sınıflandırma sırasında kullanıcı
ayrıca isterse veya kullanıcı doğrudan "PDF'leri adlandır"/"vancouver
stilinde adlandır" dediğinde devreye girer. Kural detayları (dergi adı
tam yazılır — kısaltılmaz, ":"/em dash → ".", 120 karakter sınırı,
uydurma yasağı, "+" işareti konum koruması) subagent tanımında
(`~/.claude/agents/bilim-s-pdf.md`) yer alır. Detaylı tanıtım: bu
skill'in `README.md`'si.
