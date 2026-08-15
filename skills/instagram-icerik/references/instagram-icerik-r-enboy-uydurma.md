# En-boy uydurma — görüntüyü germeden

## Neden bu dosya var

Üstteki `video-processing-editing` skill'i Story ve Reel için şunu önerir:

```bash
ffmpeg -i input.mp4 -s 1080x1920 ... instagram_reel.mp4    # ❌ KULLANMA
```

`-s WxH` kaynağın en-boy oranını **yok sayar ve görüntüyü gerer.** Yatay (16:9) bir klip bu
komutla dikeye çevrildiğinde insanlar uzar, yüzler incelir. Kaynak zaten 9:16 ise zararsızdır ama
o durumda da gereksizdir.

Doğrusu her zaman `force_original_aspect_ratio` ile birlikte `crop` veya `pad` kullanmaktır.

## Hangi modu seçmeli

| Mod | Ne yapar | Ne zaman |
|---|---|---|
| **crop** | Kenarlardan kırpar, kadrajı doldurur. Siyah bant yok, kayıp var. | Kaynak hedefe yakın oranda (ör. 4:5 → 9:16). Özne ortadaysa. **Varsayılan.** |
| **pad** | Küçültüp ortalar, boşluğu siyahla doldurur. Kayıp yok, bant var. | Kadrajın tamamı önemliyse (manzara, yazı, grup fotoğrafı). |
| **blur** | Ortada tam kadraj, arkada aynı görüntünün bulanık büyütülmüşü. | Yatay kaynağı dikeye taşırken. Reels'te en iyi görüneni. |
| **dokunma** | — | Kaynak zaten hedef orandaysa. Yeniden ölçekleme kalite kaybıdır. |

Karar vermeden önce kaynağı ölç:

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 girdi.mp4
```

## Komutlar

Aşağıda `1080:1920` (9:16 Reels) kullanılıyor. Feed dikey için `1080:1350`, kare için
`1080:1080` yaz.

### crop — kenarlardan kırp

```bash
ffmpeg -i girdi.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

`increase` = kısa kenar hedefi doldurana kadar büyüt; `crop` taşan kısmı atar.
Kırpma varsayılan olarak **ortadan** yapılır. Özne ortada değilse kaydır:

```bash
# Özne solda: kırpmayı sola çek (x=0 en sol, x=(iw-ow) en sağ)
crop=1080:1920:0:(ih-oh)/2

# Özne üstte (portre kaynağı kareye alırken)
crop=1080:1080:(iw-ow)/2:0
```

### pad — siyah bantla ortala

```bash
ffmpeg -i girdi.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

`decrease` = tamamı sığana kadar küçült; `pad` kalan boşluğu doldurur.
`color=black` yerine `color=white` veya `color=0x1a1a1a` yazılabilir.

### blur — bulanık arka planlı dolgu

```bash
ffmpeg -i girdi.mp4 -filter_complex \
  "[0:v]split[bg][fg];\
   [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:3[bgb];\
   [fg]scale=1080:1920:force_original_aspect_ratio=decrease[fgs];\
   [bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" \
  -map "[v]" -map 0:a? \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

`boxblur=40:3` — ilk sayı bulanıklık yarıçapı, ikincisi geçiş sayısı. 20 hafif, 40 dengeli,
60+ tamamen dağılmış. `-map 0:a?` sondaki `?` sayesinde sessiz kaynakta komut hata vermez.

## Farklı oranlardaki klipleri tek Reels'te birleştirme

En sık gerçek durum: telefonda kimi klip yatay, kimi dikey çekilmiş, hepsi tek Reels olacak.
Üstteki `video-processing-editing` skill'inin anlattığı `concat` **demuxer**'ı bu işi yapamaz —
o yöntem tüm girdilerin aynı çözünürlük, kare hızı ve codec'te olmasını şart koşar.

Doğrusu `concat` **filtresi**: her klip önce ortak orana getirilir, sonra birleştirilir.

```bash
ffmpeg -i klip1.mp4 -i klip2.mp4 -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v0];\
[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v1];\
[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

- **`n=2`** girdi sayısıdır — klip ekledikçe artır, `[vN][N:a]` çiftlerini de ekle.
- **`fps=30` her klipte** — farklı kare hızındaki kaynaklar birleşince ses kayar.
- **`setsar=1` her klipte** — biri kare olmayan piksel taşıyorsa `concat` hata verir.
- Kliplerden biri **sessizse** bu komut çalışmaz. Önce sessiz olana boş ses akışı ekle:
  ```bash
  ffmpeg -i sessiz.mp4 -f lavfi -i anullsrc=cl=stereo:r=44100 \
    -map 0:v -map 1:a -shortest -c:v copy -c:a aac sesli.mp4
  ```
- Klipler arasına geçiş isteniyorsa `concat` yerine `xfade` kullanılır — kalıp
  `instagram-icerik-r-slayt-video.md` içindeki offset formülünün aynısıdır.

## Sık yapılan hatalar

**`setsar=1` unutmak.** Bazı telefon kayıtlarında piksel kare değildir; `setsar=1` yazılmazsa
çıktı doğru çözünürlükte olduğu halde oynatıcıda basık görünür. Her uydurma zincirinin sonuna ekle.

**Tek sayı çözünürlük.** `libx264` + `yuv420p` çift sayı genişlik/yükseklik ister. Hedefi elle
hesaplarken `scale=720:-1` yerine `scale=720:-2` kullan — `-2` en yakın çift sayıya yuvarlar.

**Önce kırpıp sonra ölçeklemek.** Ters sıra kalite kaybettirir: önce `scale`, sonra `crop`.

**Dikey videoyu ikinci kez dikeye çevirmek.** Kaynak 1080x1920 ise hiçbir şey yapma. Gereksiz
yeniden kodlama her seferinde biraz daha kalite yer.
