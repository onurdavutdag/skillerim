# Instagram ölçüleri ve sınırları

*Temmuz 2026 itibarıyla. Instagram bu sayıları haber vermeden değiştirir — kritik bir gönderim
öncesi teyit et.*

## Tablo

| Biçim | Çözünürlük | Oran | Süre | Dosya | Kare hızı |
|---|---|---|---|---|---|
| **Reels** | 1080x1920 | 9:16 | 20 dk'ya kadar, ama **3 dk üstü keşfette önerilmiyor** | 4 GB | 30 fps |
| **Stories** | 1080x1920 | 9:16 | 60 sn (uzunu 60 sn'lik parçalara bölünür) | 4 GB | 30 fps |
| **Feed video (yeni)** | 1080x1440 | 3:4 | 60 dk | 4 GB | 30 fps |
| **Feed video (eski)** | 1080x1350 | 4:5 | 60 dk | 4 GB | 30 fps |
| **Feed kare** | 1080x1080 | 1:1 | 60 dk | 4 GB | 30 fps |

**Codec:** video H.264 (`libx264`), ses AAC. Kapsayıcı MP4 veya MOV.

### Süre üzerine — sayıya değil davranışa bak

Reels'in teknik sınırı 20 dakika ama **algoritma 3 dakikadan uzun Reels'i takipçi olmayanlara
önermiyor.** Erişim isteniyorsa 90 saniyenin altı en güvenlisi. Uygulama içinden çekim yaparken
90 sn / 3 dk'da kesilir; galeriden yüklerken uzun sürelere izin verir.

### Oran üzerine — feed 3:4'e geçti

Instagram profil ızgarasını 4:5'ten **3:4'e** taşıdı. 4:5 hâlâ yüklenebiliyor ama ızgarada üstten
ve alttan kırpılarak görünüyor. Yeni işlerde `3:4` (1080x1440) kullan.

### Güvenli alan

Reels ve Stories'te arayüz görüntünün üstünü ve altını kapatır. Önemli hiçbir şey buralara denk
gelmemeli:

- **Alt ~250 px** — beğeni/yorum/paylaş, hesap adı, açıklama metni
- **Üst ~120 px** — durum çubuğu, kapat düğmesi

Yani 1080x1920'lik kadrajda güvenli alan yaklaşık **1080x1550**. Altyazı `MarginV`'si bu yüzden
120'den küçük olmamalı.

## Hazır export komutları

Aşağıdaki komutlar `-s WxH` **kullanmaz** — germe yerine `crop` uygular. Kaynak zaten hedef
orandaysa `-vf` kısmını tamamen çıkar.

### Reels (9:16)

```bash
ffmpeg -i girdi.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" \
  -c:v libx264 -crf 20 -preset medium -profile:v high -level 4.0 \
  -pix_fmt yuv420p -r 30 -g 60 \
  -c:a aac -b:a 192k -ar 44100 \
  -movflags +faststart \
  cikti.mp4
```

### Stories (9:16, 60 sn'de kes)

```bash
ffmpeg -i girdi.mp4 -t 60 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" \
  -c:v libx264 -crf 20 -preset medium \
  -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

60 saniyeden uzun bir videoyu elle parçalara bölmek için:

```bash
ffmpeg -i girdi.mp4 -c copy -map 0 -segment_time 60 -f segment -reset_timestamps 1 \
  "story_%02d.mp4"
```

### Feed dikey (3:4)

```bash
ffmpeg -i girdi.mp4 \
  -vf "scale=1080:1440:force_original_aspect_ratio=increase,crop=1080:1440,setsar=1" \
  -c:v libx264 -crf 20 -preset medium \
  -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

### Kapak fotoğrafı (thumbnail)

```bash
# 2. saniyeden kare al
ffmpeg -i cikti.mp4 -ss 2 -frames:v 1 -q:v 2 kapak.jpg
```

## Parametreler neden böyle

| Parametre | Gerekçe |
|---|---|
| `-movflags +faststart` | `moov` atomunu dosya başına taşır; yükleme sırasında Instagram'ın videoyu işlemesi hızlanır. **Atlanırsa yükleme takılabilir.** |
| `-pix_fmt yuv420p` | Evrensel uyumluluk. `yuv444p` veya `yuvj420p` bazı cihazlarda siyah ekran verir |
| `-crf 20` | Görsel olarak kayıpsıza yakın. Instagram zaten yeniden sıkıştırır; girdiyi fazla sıkıştırmak çift kayıp demektir |
| `-g 60` | Keyframe aralığı = 2 sn @30fps. Akış başlangıcını hızlandırır |
| `-ar 44100` | 48 kHz de kabul edilir ama 44,1 kHz her yerde sorunsuz |
| `-b:a 192k` | Instagram spesifikasyonu 128k der; 192k girdi yeniden kodlamadan sonra daha temiz kalır |

## Dosya boyutu sorun olursa

Sınır 4 GB — normal bir Reels'te asla ulaşılmaz. Yine de küçültmek gerekirse:

```bash
# 1. adım: crf'i yükselt (20 -> 23 gözle fark edilmez, dosya ~%35 küçülür)
-crf 23

# 2. adım: preset'i yavaşlat (aynı kalite, daha küçük dosya, daha uzun kodlama)
-preset slow

# 3. adım: hedef boyut için iki geçiş
ffmpeg -i girdi.mp4 -c:v libx264 -b:v 6M -pass 1 -an -f null /dev/null
ffmpeg -i girdi.mp4 -c:v libx264 -b:v 6M -pass 2 -c:a aac -b:a 192k cikti.mp4
```

Çözünürlüğü 1080'in altına **düşürme** — Instagram düşük çözünürlüklü videoyu daha agresif
sıkıştırır, sonuç daha kötü görünür.
