---
name: instagram-icerik
description: Bu skill, kullanıcının kendi çektiği video ve fotoğrafları Instagram'da paylaşılmaya hazır hale getirmek için kullanılmalıdır: klipleri birleştirme/kırpma, fotoğraflardan müzikli slayt video üretme, Reels/Stories/feed en-boy oranına görüntüyü GERMEDEN uydurma, arka plan müziği dengeleme ve altyazı gömme. Tetikleyiciler; "bu videoları birleştir", "Reels yap", "story için hazırla", "şu fotoğraflardan video yap", "dikey yap", "müzik ekle", "altyazı göm", "Instagram'a yükleyeceğim", "post için hazırla", "boyutu küçült" gibi ifadeler. Kullanıcı "Instagram" kelimesini söylemese de elindeki video/foto dosyalarını sosyal medya için hazırlamak istediğinde tetiklenir. ffmpeg mekaniğinin tamamı (kesme, keyframe hizalama, codec seçimi, batch) `video-processing-editing` skill'ine devredilir; bu skill onun Instagram boşluklarını kapatır.
version: 1.0
---

# instagram-icerik

Kullanıcının telefonuyla çektiği ham video ve fotoğrafları Instagram'a yüklenebilir hale getirir.
Tetikleme koşulları yukarıdaki `description` alanındadır.

## Bu skill neyi kapsar, neyi devreder

Bu skill **tek başına bir ffmpeg rehberi değildir.** Kesme, birleştirme, keyframe hizalama,
codec/bitrate seçimi, renk düzeltme, toplu işleme gibi ffmpeg temelleri
`video-processing-editing` skill'indedir — o yükleyip kullanılır, buraya kopyalanmaz.

Bu skill yalnız o skill'in Instagram tarafında **eksik veya yanlış** bıraktığı dört şeyi kapatır:

| Konu | Neden burada |
|---|---|
| Fotoğraflardan slayt video | Üstteki skill'in `ken-burns` komutu Windows'ta çalışmaz (sabit `/tmp` yolları), yatay üretir, müzik ve geçiş koymaz |
| En-boy uydurma | Üstteki skill'in Story/Reel komutları `-s 1080x1920` kullanır — kaynak 9:16 değilse **görüntüyü gerer** |
| Instagram ölçüleri | Üstteki skill'in Reels süre sınırı (90 sn) güncelliğini yitirdi |
| Müzik dengeleme + altyazı | Instagram'a özgü seviye ve punto kararları |

## Ön koşul

`ffmpeg` ve `ffprobe` PATH'te olmalı. Yoksa:

```powershell
winget install --id Gyan.FFmpeg --exact
```

Kurulumdan sonra **yeni bir kabuk** gerekir. Doğrula: `ffmpeg -version`.

## İş akışı

1. **Kaynağı ölç.** Ne yapılacağına karar vermeden önce elde ne olduğuna bak:
   ```bash
   ffprobe -v error -select_streams v:0 \
     -show_entries stream=width,height,r_frame_rate,codec_name \
     -show_entries format=duration,size -of default=nw=1 girdi.mp4
   ```
   En-boy oranı, süre ve ses akışının varlığı buradan okunur.

2. **Hedefi seç.** Kullanıcı söylemediyse sor — Reels (9:16), feed dikey (4:5), kare (1:1).
   Ölçüler: `references/instagram-icerik-r-platform-olculeri.md`.

3. **En-boy uydurma modunu seç.** Kaynak zaten hedef orandaysa dokunma. Değilse `crop` / `pad` /
   `blur` arasından seç — karar tablosu ve komutlar: `references/instagram-icerik-r-enboy-uydurma.md`.
   **Asla `-s 1080x1920` yazma**, görüntüyü gerer.

4. **İşi yap.** Fotoğraf slaytı için aşağıdaki script; video birleştirme/kesme için
   `video-processing-editing`.

5. **Sesi ve altyazıyı ekle.** `references/instagram-icerik-r-ses-ve-altyazi.md`.

6. **Çıktıyı doğrula.** Üretilen dosyayı `ffprobe` ile ölç: çözünürlük, süre ve dosya boyutu
   platform sınırının altında mı.

## Fotoğraflardan slayt video

```bash
python scripts/instagramicerik_slayt.py ./fotograflar --muzik muzik.mp3
```

Varsayılan: 9:16 Reels, fotoğraf başına 3 sn, 0,5 sn `fade` geçiş, `crop` uydurma, 30 fps.
Tek ffmpeg geçişi — ara dosya yazmaz.

Sık kullanılanlar:

```bash
# Yatay fotoğraflar dikey Reels'e: bulanık arka planlı
python scripts/instagramicerik_slayt.py ./fotograflar --uydur blur --muzik muzik.mp3

# Hareketli slayt (yavaş yakınlaşma/uzaklaşma)
python scripts/instagramicerik_slayt.py ./fotograflar --ken-burns --sure 2.5

# Feed dikey, kaydırmalı geçiş, belirli sırada
python scripts/instagramicerik_slayt.py a.jpg b.jpg c.jpg --oran 4:5 --gecis-tipi slideleft

# Komutu çalıştırmadan gör
python scripts/instagramicerik_slayt.py ./fotograflar --kuru
```

Toplam süre = `n × --sure − (n−1) × --gecis`. Ayrıntı ve elle ffmpeg karşılığı:
`references/instagram-icerik-r-slayt-video.md`.

## Çıktı kuralları

- Üretilen her dosya proje kökündeki **`output/`** altına yazılır (`output/video/`).
- Dosya adının sonuna oluşturma tarih-saati eklenir: `Ad YYYYAAGG SSDD.mp4`
  (örn. `Slayt 9-16 20260730 1816.mp4`). Script bunu kendiliğinden yapar; elle ffmpeg
  çalıştırırken sen uygula.
- Kullanıcının ham video/fotoğrafları **taşınmaz, üzerine yazılmaz** — kaynak hep yerinde kalır.

## Referanslar

| Dosya | İçerik |
|---|---|
| `references/instagram-icerik-r-enboy-uydurma.md` | crop / pad / blur karar tablosu, video ve foto için tam komutlar |
| `references/instagram-icerik-r-slayt-video.md` | Slayt script'inin tüm seçenekleri, elle ffmpeg karşılığı, geçiş tipleri |
| `references/instagram-icerik-r-ses-ve-altyazi.md` | Müzik seviyesi, konuşma varken ducking, `.srt` gömme, Instagram'da okunur punto |
| `references/instagram-icerik-r-platform-olculeri.md` | 2026 Instagram ölçü/süre/boyut sınırları ve hazır export komutları |

## Kapsam dışı

- **ffmpeg temelleri** → `video-processing-editing` skill'i.
- **Instagram'a yükleme** — bu skill dosya üretir; paylaşımı kullanıcı yapar.
- **Konuşmadan altyazı üretme** — `.srt` dosyasını videoya gömer, sıfırdan yazmaz.
  Gerekirse yerel `whisper` ayrıca kurulur.
- **Telifli müzik.** Kullanıcının verdiği ses dosyası olduğu gibi kullanılır; telif taraması
  yapılmaz. Instagram'ın kendi müzik kütüphanesi yalnız uygulama içinden eklenebilir —
  ffmpeg ile gömülen müzik telifliyse gönderi sessizleştirilebilir. Şüpheliyse kullanıcıyı uyar.
