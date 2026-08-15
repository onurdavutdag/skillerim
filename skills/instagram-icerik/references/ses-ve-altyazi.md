# Ses ve altyazı

## Müzik ekleme

### Sessiz videoya müzik

```bash
ffmpeg -i video.mp4 -i muzik.mp3 \
  -map 0:v -map 1:a -shortest \
  -c:v copy -c:a aac -b:a 192k \
  -movflags +faststart cikti.mp4
```

`-c:v copy` görüntüyü yeniden kodlamaz — hızlı ve kayıpsız. `-shortest` müzik videodan uzunsa
fazlasını keser.

### Videonun kendi sesi + müzik birlikte

```bash
ffmpeg -i video.mp4 -i muzik.mp3 -filter_complex \
  "[1:a]volume=0.25[muz];[0:a][muz]amix=inputs=2:duration=first:dropout_transition=0[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -movflags +faststart cikti.mp4
```

`duration=first` — karışım videonun sesi bitince biter. `dropout_transition=0` olmazsa bir kanal
sustuğunda `amix` diğerinin sesini kendiliğinden yükseltir, ses dalgalanır.

### Konuşma varken müziği kısma (ducking)

Konuşma duyulurken müzik kendiliğinden geri çekilir, sustuğunda geri gelir:

```bash
ffmpeg -i video.mp4 -i muzik.mp3 -filter_complex \
  "[1:a]volume=0.4[muz];\
   [muz][0:a]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];\
   [duck][0:a]amix=inputs=2:duration=first:dropout_transition=0[a]" \
  -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -movflags +faststart cikti.mp4
```

- `threshold` — düşürürsen daha erken kısar (0.02-0.05 arası dene)
- `ratio` — ne kadar kısacağı; 8 belirgin, 4 hafif
- `release=400` — konuşma bittikten 400 ms sonra müzik geri gelir. Çok kısa olursa müzik
  cümle aralarında zıplar.

### Seviye dengeleme

Farklı kaynaklardan gelen klipler farklı yükseklikte olur. Instagram'ın kendi normalizasyonu
vardır ama girdiyi düzeltmek daha iyi sonuç verir:

```bash
ffmpeg -i girdi.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:v copy -c:a aac -b:a 192k cikti.mp4
```

`I=-14 LUFS` sosyal medya için yaygın hedeftir. **Tek geçişte tam isabetli değildir**; kritik
işlerde iki geçiş gerekir (ilk geçiş `print_format=json` ile ölçer, ikinci geçiş ölçülen değerleri
`measured_I` vb. olarak geri verir).

### Müziği sonda söndürme

```bash
# Videonun toplam süresini öğren
ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4
# Çıktı 28.5 ise son 2 saniyede söndür:
ffmpeg -i video.mp4 -af "afade=t=out:st=26.5:d=2" -c:v copy -c:a aac -b:a 192k cikti.mp4
```

Başta yumuşak giriş için `afade=t=in:st=0:d=1`.

## Altyazı

### Gömülü (hardcoded) — Instagram için doğrusu

Instagram yumuşak altyazı akışını (`mov_text`) göstermez. Metin görüntünün içine yakılmalı:

1080x1920 Reels için doğrulanmış değerler:

```bash
ffmpeg -i video.mp4 \
  -vf "subtitles=altyazi.srt:force_style='FontName=Arial,Fontsize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=50'" \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p \
  -c:a copy -movflags +faststart cikti.mp4
```

### `Fontsize` ve `MarginV` piksel DEĞİLDİR

En sık yapılan hata bu. `.srt` dosyasında çözünürlük bilgisi yoktur; ffmpeg altyazıyı
**384x288'lik sanal bir tuvale** yerleştirir, libass da onu video yüksekliğine göre büyütür.
Yani her iki değer de şu kat sayıyla çarpılır:

```
kat sayı = video yüksekliği / 288
```

1080x1920 videoda kat sayı **6,67**. `MarginV=250` yazarsan metin alttan 250 px değil
**1667 px** yukarı çıkar — ekranın üst yarısına gider. (Bu değer denendi, metin gerçekten
tepeye çıktı.)

Doğru değeri hesapla:

```
Fontsize = istenen_punto × 288 / video_yüksekliği
MarginV  = istenen_boşluk × 288 / video_yüksekliği
```

| Hedef | Kat sayı | `Fontsize` (~120 px metin) | `MarginV` (~350 px boşluk) |
|---|---|---|---|
| 1080x1920 (9:16) | 6,67 | **18** | **50** |
| 1080x1440 (3:4) | 5,00 | 24 | 70 |
| 1080x1350 (4:5) | 4,69 | 26 | 53 (~250 px yeter) |
| 1080x1080 (1:1) | 3,75 | 32 | 40 |

**`original_size=` seçeneğini kullanma.** İşe yarayacak gibi durur ama tuvali düzeltmez,
metni daha da büyütüp kadraj dışına taşır — denendi, sonuç bozuk.

### Diğer `force_style` alanları

| Alan | Anlamı | Instagram için |
|---|---|---|
| `Alignment` | 2 = alt orta, 8 = üst orta | 2 (alt), `MarginV` ile arayüzün üstüne çek |
| `Outline` | Kenar kalınlığı | 2-3. Kontursuz beyaz metin açık arka planda kaybolur |
| `BorderStyle` | 1 = kontur+gölge, 3 = dolu kutu | 1 genelde yeterli; çok karışık arka planda 3 |
| `PrimaryColour` | Metin rengi, **`&HAABBGGRR`** (ters sıra, AA=00 opak) | `&H00FFFFFF` beyaz |
| `Bold` | 1 = kalın | 1. Telefonda ince font okunmuyor |

### Sonucu gözle doğrula

Tahmin etme, kare al ve bak:

```bash
ffmpeg -y -ss 1 -i cikti.mp4 -frames:v 1 kontrol.png
```

Metin alttan en az 250 px yukarıda mı — değilse Instagram arayüzü üstünü kapatır.

**Windows'ta yol tuzağı:** `subtitles=` filtresi içindeki `:` ve `\` ffmpeg tarafından filtre
sözdizimi sanılır. `C:\yol\altyazi.srt` çalışmaz. Çözüm: `.srt` dosyasının bulunduğu dizine geç ve
yalnız dosya adını yaz, ya da kaçır: `subtitles='C\:/yol/altyazi.srt'`.

### Türkçe karakter

`.srt` dosyası **UTF-8** kaydedilmeli. Ş/Ğ/İ/ı kutu çıkıyorsa dosya Windows-1254'tür:

```bash
ffmpeg -i video.mp4 -vf "subtitles=altyazi.srt:charenc=CP1254:force_style='...'" ...
```

Kalıcı çözüm dosyayı UTF-8'e çevirmektir.

### .srt biçimi

```
1
00:00:00,000 --> 00:00:02,500
İlk satır burada

2
00:00:02,500 --> 00:00:05,000
İkinci satır
```

Ondalık ayıracı **virgül** (nokta değil). Satır numarası 1'den başlar ve boş satırla ayrılır.

### Sabit metin (altyazı dosyası olmadan)

Tek bir başlık için `.srt` yazmaya gerek yok:

```bash
ffmpeg -i video.mp4 -vf \
  "drawtext=text='Kapadokya 2026':fontfile='C\:/Windows/Fonts/arialbd.ttf':fontsize=64:fontcolor=white:borderw=3:bordercolor=black:x=(w-tw)/2:y=h-400:enable='between(t,1,5)'" \
  -c:v libx264 -crf 20 -c:a copy cikti.mp4
```

`enable='between(t,1,5)'` — metin yalnız 1-5. saniyeler arasında görünür.
`fontfile` **zorunludur** (Windows ffmpeg derlemesinde fontconfig varsayılan yapılandırması yoktur;
yol verilmezse `Cannot load default config file` hatası alınır).
