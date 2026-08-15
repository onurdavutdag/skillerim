# instagram-icerik

Kullanıcının kendi çektiği video ve fotoğrafları Instagram'a yüklenebilir hale getiren skill.
Her şey yerelde `ffmpeg` ile yapılır — bulut servisi, ücretli API, hesap bağlama yok.

## Ne zaman tetiklenir

"Bu videoları birleştir", "Reels yap", "story için hazırla", "şu fotoğraflardan video yap",
"dikey yap", "müzik ekle", "altyazı göm", "Instagram'a yükleyeceğim", "boyutu küçült".
Kullanıcı "Instagram" demese de elindeki video/foto dosyalarını sosyal medya için hazırlamak
istediğinde devreye girer.

## Tek başına çalışmaz — üstüne bindiği skill

ffmpeg mekaniğinin tamamı (kesme, keyframe hizalama, birleştirme, codec seçimi, renk düzeltme,
toplu işleme) [`third-party/video-processing-editing/`](../../third-party/video-processing-editing/)
skill'indedir. `instagram-icerik` onu tekrar etmez; yalnız o skill'in Instagram tarafında
**eksik veya yanlış** bıraktığı dört şeyi kapatır:

| Boşluk | Üstteki skill'de durum |
|---|---|
| Fotoğraflardan slayt video | `ken-burns` komutu var ama sabit `/tmp` yolları yüzünden Windows'ta çalışmaz, yatay üretir, müzik ve geçiş koymaz |
| En-boy uydurma | Story/Reel komutları `-s 1080x1920` kullanır — kaynak 9:16 değilse görüntüyü **gerer** |
| Instagram ölçüleri | Reels süre sınırı güncelliğini yitirdi (90 sn yazıyor) |
| Müzik dengeleme + altyazı | Instagram'a özgü seviye ve punto kararları yok |

## İçerik

| Dosya | Ne yapar |
|---|---|
| `SKILL.md` | İş akışı, karar noktaları, slayt komutları |
| `references/instagram-icerik-r-enboy-uydurma.md` | crop / pad / blur karar tablosu ve tam komutlar |
| `references/instagram-icerik-r-slayt-video.md` | Slayt script'inin seçenekleri, elle ffmpeg karşılığı, süre kararı |
| `references/instagram-icerik-r-ses-ve-altyazi.md` | Müzik seviyesi, ducking, `.srt` gömme, Türkçe karakter |
| `references/instagram-icerik-r-platform-olculeri.md` | 2026 ölçü/süre/boyut sınırları, hazır export komutları |
| `scripts/instagramicerik_slayt.py` | Fotoğraflardan slayt video — tek ffmpeg geçişi, ara dosya yok |

## Ön koşul

```powershell
winget install --id Gyan.FFmpeg --exact
```

Kurulumdan sonra yeni bir kabuk gerekir. Doğrula: `ffmpeg -version`.

## Kurulum

`skillerim` reposu **kaynaktır**; skill'i fiilen kullanmak için bu klasörü
`~/.claude/skills/instagram-icerik/` altına kopyala.

## Kapsam dışı

- ffmpeg temelleri → `video-processing-editing`
- Instagram'a yükleme — skill dosya üretir, paylaşımı kullanıcı yapar
- Konuşmadan altyazı üretme — `.srt`'yi gömer, sıfırdan yazmaz (gerekirse yerel `whisper`)
- Telif taraması — kullanıcının verdiği müzik olduğu gibi kullanılır
