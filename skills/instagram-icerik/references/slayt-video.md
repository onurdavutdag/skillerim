# Fotoğraflardan slayt video

## Neden kendi script'imiz var

Üstteki `video-processing-editing` skill'inde bir slayt komutu var
(`timelapse_creator.py ken-burns`) ama Instagram işine uymuyor:

| Sorun | Nerede |
|---|---|
| Sabit `/tmp/kenburns_0000.mp4` yolları — Windows'ta böyle bir dizin yok, çalışmaz | `scripts/timelapse_creator.py:222` |
| Varsayılan çıktı `1920x1080` yatay — Reels dikey | `scripts/timelapse_creator.py:38` |
| Arka plan müziği desteği yok | — |
| Geçiş yok; klipleri düz `concat` ile ekler, `xfade` kullanmaz | — |
| Her fotoğraf için ayrı ara dosya yazar, sonra birleştirir — yavaş | — |

`scripts/instagram-icerik_slayt.py` bunların hepsini tek ffmpeg geçişinde çözer, ara dosya yazmaz.

## Seçenekler

```
python scripts/instagram-icerik_slayt.py <klasör VEYA dosyalar> [seçenekler]
```

| Seçenek | Varsayılan | Ne yapar |
|---|---|---|
| `--oran` | `9:16` | `9:16` Reels/Stories, `4:5` feed dikey, `1:1` kare, `16:9` yatay |
| `--sure` | `3.0` | Fotoğraf başına saniye |
| `--gecis` | `0.5` | Geçiş süresi. `0` = sert kesme. `--sure`'den küçük olmalı |
| `--gecis-tipi` | `fade` | `fade fadeblack fadewhite dissolve slideleft slideright slideup slidedown wipeleft wiperight circleopen circleclose smoothleft smoothright zoomin` |
| `--uydur` | `crop` | `crop` / `pad` / `blur` — bkz. `enboy-uydurma.md` |
| `--muzik` | yok | Arka plan müziği (mp3/m4a/wav) |
| `--muzik-ses` | `1.0` | Seviye çarpanı. `0.5` yarıya indirir |
| `--fps` | `30` | Kare hızı |
| `--crf` | `20` | Kalite; düşük = daha iyi + daha büyük dosya |
| `--ken-burns` | kapalı | Yavaş yakınlaşma/uzaklaşma; tek/çift fotoğrafta yön değişir |
| `--ken-burns-guc` | `0.15` | Zoom miktarı (%15) |
| `-o` | `output/video/Slayt <oran> <tarih>.mp4` | Çıktı yolu |
| `--kuru` | — | ffmpeg komutunu yazdırır, çalıştırmaz |

**Sıra:** klasör verilirse dosya adına göre alfabetik sıralanır — `01.jpg, 02.jpg, 10.jpg`
şeklinde sıfır dolgulu adlandır, yoksa `10` `2`'den önce gelir. Belirli bir sıra isteniyorsa
dosyaları tek tek, istenen sırada yaz.

**Süre hesabı:** `toplam = n × sure − (n−1) × gecis`.
10 fotoğraf, 3 sn, 0,5 sn geçiş → `10×3 − 9×0,5 = 25,5` sn.

## Elle ffmpeg karşılığı

Script'in ürettiği komutun iki fotoğraflık hali (script'e `--kuru` verirsen tamamını görürsün):

```bash
ffmpeg -y -hide_banner \
  -loop 1 -t 3 -i 01.jpg \
  -loop 1 -t 3 -i 02.jpg \
  -i muzik.mp3 \
  -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p[v0];\
[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p[v1];\
[v0][v1]xfade=transition=fade:duration=0.5:offset=2.5[vson];\
[2:a]atrim=0:5.5,asetpts=N/SR/TB,volume=1.0,afade=t=out:st=4:d=1.5[a]" \
  -map "[vson]" -map "[a]" \
  -t 5.5 \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -movflags +faststart \
  cikti.mp4
```

Anahtar noktalar:

- **`-loop 1 -t <sure> -i foto.jpg`** — durağan görüntüyü video akışına çevirir. `-t` her girdinin
  önünde ayrı ayrı yazılır.
- **`xfade` offset formülü:** `i.` birleştirmenin offset'i `i × (sure − gecis)`.
  Yanlış offset, geçişin erken bitip son fotoğrafın donuk kalmasına yol açar.
- **`format=yuv420p` her girdide** — JPEG'ler `yuvj420p` gelir, xfade karışık piksel formatında
  hata verir.
- **`fps=<n>` xfade'den önce** — girdiler farklı kare hızındaysa geçiş kayar.
- **`-t <toplam>`** çıkışta — müzik videodan uzunsa fazlasını keser.

## Ken Burns (hareket) nasıl çalışır

`zoompan` filtresi durağan fotoğrafa kare kare zoom uygular. Doğrudan uygulanırsa görüntü zıplar;
o yüzden script önce 4 kat büyütür, sonra `zoompan` ile hedef çözünürlüğe indirir:

```
scale=4320:7680:force_original_aspect_ratio=increase,crop=4320:7680,
zoompan=z='min(zoom+0.0017,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=90:s=1080x1920:fps=30
```

- `d=90` — kare sayısı = `sure × fps`. Bu sayı yanlışsa hareket erken durur ya da kesilir.
- `z` ifadesi tek fotoğrafta yakınlaşır, çift fotoğrafta uzaklaşır — arka arkaya aynı yönde
  hareket monoton görünür.
- Yavaşlık: 4× büyütme bellek yer. 30'dan fazla fotoğrafta `--ken-burns` kullanma ya da
  `--ken-burns-guc 0.08` ile hafiflet.

## Süre kararı

Instagram'da fotoğraf slaytı izlenirken **3 saniye üstü sıkıcı** gelir. Pratik aralık:

| Fotoğraf sayısı | Öneri |
|---|---|
| 3-6 | `--sure 3 --gecis 0.5` |
| 7-15 | `--sure 2.5 --gecis 0.4` |
| 16+ | `--sure 1.8 --gecis 0.3`, müzik ritmine yakın |

Müzikle hizalamak için: şarkının vuruş aralığını ölç, `--sure` + `--gecis` toplamını ona eşitle.
Örn. 120 BPM'de bir vuruş 0,5 sn; `--sure 2.1 --gecis 0.4` her fotoğrafı 4 vuruşa denk getirir.
