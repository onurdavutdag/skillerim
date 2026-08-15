#!/usr/bin/env python3
"""Fotograflardan Instagram slayt videosu uretir (tek ffmpeg gecisi).

Ustteki video-processing-editing skill'inin ken-burns komutu Windows'ta
calismaz (sabit /tmp yollari) ve yatay/muziksiz/gecissiz uretir. Bu script
onun yerine gecer: dikey Reels orani, xfade gecisleri, arka plan muzigi,
germeyen en-boy uydurma. Ara dosya yazmaz -- tek filter_complex.

Kullanim:
    python instagram-icerik_slayt.py ./fotograflar --muzik muzik.mp3
    python instagram-icerik_slayt.py a.jpg b.jpg c.jpg --oran 4:5 --uydur blur
    python instagram-icerik_slayt.py ./fotograflar --sure 2.5 --gecis 0.75 --ken-burns
"""

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys

ORANLAR = {
    "9:16": (1080, 1920),   # Reels / Stories
    "3:4": (1080, 1440),    # feed dikey -- 2026 izgara standardi
    "4:5": (1080, 1350),    # feed dikey -- eski standart
    "1:1": (1080, 1080),    # feed kare
    "16:9": (1920, 1080),   # yatay
}

FOTO_UZANTILARI = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic")

# xfade gecis tipleri -- ffmpeg'in destekledigi tam liste daha uzun,
# bunlar Instagram slaytlarinda ise yarayanlar.
GECIS_TIPLERI = [
    "fade", "fadeblack", "fadewhite", "dissolve",
    "slideleft", "slideright", "slideup", "slidedown",
    "wipeleft", "wiperight", "circleopen", "circleclose",
    "smoothleft", "smoothright", "zoomin",
]


def fotograflari_bul(girdiler):
    """Klasor verilirse icindeki fotograflari sirali dondurur, dosya verilirse sirayi korur."""
    if len(girdiler) == 1 and os.path.isdir(girdiler[0]):
        klasor = girdiler[0]
        adlar = sorted(
            a for a in os.listdir(klasor)
            if a.lower().endswith(FOTO_UZANTILARI)
        )
        return [os.path.join(klasor, a) for a in adlar]

    eksik = [g for g in girdiler if not os.path.isfile(g)]
    if eksik:
        sys.exit(f"HATA: bulunamadi: {', '.join(eksik)}")
    return list(girdiler)


def uydurma_zinciri(mod, g, y):
    """En-boy uydurma filtresi. Hicbiri goruntuyu GERMEZ (-s WxH yapmaz)."""
    if mod == "crop":
        # Kenarlardan kirpar, siyah bant yok. Portre foto + dikey videoda en iyisi.
        return f"scale={g}:{y}:force_original_aspect_ratio=increase,crop={g}:{y}"
    if mod == "pad":
        # Tam kadraj korunur, ustte/altta siyah bant olusur.
        return (f"scale={g}:{y}:force_original_aspect_ratio=decrease,"
                f"pad={g}:{y}:(ow-iw)/2:(oh-ih)/2:color=black")
    if mod == "blur":
        # Bulanik arka plan + ortada tam kadraj. Yatay fotoyu dikeye tasirken en iyi goruneni.
        return (f"split[bg][fg];"
                f"[bg]scale={g}:{y}:force_original_aspect_ratio=increase,"
                f"crop={g}:{y},boxblur=40:3[bgb];"
                f"[fg]scale={g}:{y}:force_original_aspect_ratio=decrease[fgs];"
                f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2")
    sys.exit(f"HATA: bilinmeyen uydurma modu: {mod}")


def ken_burns_zinciri(i, g, y, kare_sayisi, fps, guc):
    """zoompan ile yavas yakinlasma/uzaklasma. Tek/cift fotoda yon degisir.

    zoompan girdiyi once buyutmek gerekir, yoksa piksel zipliyor.
    """
    ust = 1.0 + guc
    if i % 2 == 0:
        z = f"min(zoom+{guc / kare_sayisi:.6f},{ust:.3f})"
    else:
        z = f"if(lte(zoom,1.0),{ust:.3f},max(1.0,zoom-{guc / kare_sayisi:.6f}))"
    return (f"scale={g * 4}:{y * 4}:force_original_aspect_ratio=increase,crop={g * 4}:{y * 4},"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={kare_sayisi}:s={g}x{y}:fps={fps}")


def filtre_kur(foto_sayisi, g, y, sure, gecis, gecis_tipi, uydur, fps, ken_burns, kb_guc):
    """filter_complex dizesini ve son video etiketini uretir."""
    parcalar = []
    kare_sayisi = max(1, int(round(sure * fps)))

    for i in range(foto_sayisi):
        if ken_burns:
            zincir = ken_burns_zinciri(i, g, y, kare_sayisi, fps, kb_guc)
        else:
            zincir = f"{uydurma_zinciri(uydur, g, y)},fps={fps}"
        parcalar.append(f"[{i}:v]{zincir},setsar=1,format=yuv420p[v{i}]")

    if foto_sayisi == 1:
        return ";".join(parcalar), "[v0]"

    # xfade zinciri. i. birlestirmenin offset'i = i * (sure - gecis).
    # Toplam sure = n*sure - (n-1)*gecis.
    onceki = "[v0]"
    for i in range(1, foto_sayisi):
        offset = i * (sure - gecis)
        cikti = f"[x{i}]" if i < foto_sayisi - 1 else "[vson]"
        parcalar.append(
            f"{onceki}[v{i}]xfade=transition={gecis_tipi}"
            f":duration={gecis}:offset={offset:.4f}{cikti}"
        )
        onceki = cikti
    return ";".join(parcalar), "[vson]"


def cikti_yolu_uret(oran):
    """Global adlandirma kurali: output/ altinda, 'Ad YYYYAAGG SSDD.mp4'."""
    damga = dt.datetime.now().strftime("%Y%m%d %H%M")
    etiket = oran.replace(":", "-")
    klasor = os.path.join("output", "video")
    os.makedirs(klasor, exist_ok=True)
    return os.path.join(klasor, f"Slayt {etiket} {damga}.mp4")


def main():
    ap = argparse.ArgumentParser(
        description="Fotograflardan Instagram slayt videosu uretir.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("girdi", nargs="+", help="Fotograf klasoru VEYA sirali fotograf dosyalari")
    ap.add_argument("-o", "--cikti", help="Cikti dosyasi (varsayilan: output/video/Slayt <oran> <tarih>.mp4)")
    ap.add_argument("--oran", default="9:16", choices=sorted(ORANLAR), help="En-boy orani (varsayilan 9:16 Reels)")
    ap.add_argument("--sure", type=float, default=3.0, help="Fotograf basina sure, saniye (varsayilan 3)")
    ap.add_argument("--gecis", type=float, default=0.5, help="Gecis suresi, saniye (varsayilan 0.5; 0 = sert kesme)")
    ap.add_argument("--gecis-tipi", default="fade", choices=GECIS_TIPLERI, help="xfade gecis tipi")
    ap.add_argument("--uydur", default="crop", choices=["crop", "pad", "blur"],
                    help="En-boy uydurma: crop=kirp, pad=siyah bant, blur=bulanik arka plan")
    ap.add_argument("--muzik", help="Arka plan muzigi (mp3/m4a/wav)")
    ap.add_argument("--muzik-ses", type=float, default=1.0, help="Muzik seviyesi carpani (varsayilan 1.0)")
    ap.add_argument("--fps", type=int, default=30, help="Kare hizi (varsayilan 30)")
    ap.add_argument("--crf", type=int, default=20, help="Kalite; dusuk=daha iyi (varsayilan 20)")
    ap.add_argument("--ken-burns", action="store_true", help="Yavas yakinlasma/uzaklasma hareketi ekler")
    ap.add_argument("--ken-burns-guc", type=float, default=0.15, help="Ken Burns zoom miktari (varsayilan 0.15 = %%15)")
    ap.add_argument("--kuru", action="store_true", help="Komutu yazdirir, calistirmaz")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("HATA: ffmpeg PATH'te yok. Windows: winget install --id Gyan.FFmpeg")

    fotograflar = fotograflari_bul(args.girdi)
    if not fotograflar:
        sys.exit("HATA: hic fotograf bulunamadi")
    if args.gecis >= args.sure:
        sys.exit(f"HATA: --gecis ({args.gecis}) --sure'den ({args.sure}) kucuk olmali")

    g, y = ORANLAR[args.oran]
    cikti = args.cikti or cikti_yolu_uret(args.oran)
    n = len(fotograflar)
    toplam = n * args.sure - (n - 1) * args.gecis

    filtre, son_etiket = filtre_kur(
        n, g, y, args.sure, args.gecis, args.gecis_tipi,
        args.uydur, args.fps, args.ken_burns, args.ken_burns_guc,
    )

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-stats"]
    for f in fotograflar:
        cmd += ["-loop", "1", "-t", str(args.sure), "-i", f]
    if args.muzik:
        cmd += ["-i", args.muzik]
        # Muzik videodan uzunsa kirp, kisaysa sessizlikle uzat; sonda 1.5 sn kis.
        filtre += (f";[{n}:a]atrim=0:{toplam:.4f},asetpts=N/SR/TB,"
                   f"volume={args.muzik_ses},"
                   f"afade=t=out:st={max(0.0, toplam - 1.5):.4f}:d=1.5[a]")

    cmd += ["-filter_complex", filtre, "-map", son_etiket]
    if args.muzik:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
    cmd += [
        "-t", f"{toplam:.4f}",
        "-c:v", "libx264", "-crf", str(args.crf), "-preset", "medium",
        "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-movflags", "+faststart",
        cikti,
    ]

    print(f"{n} fotograf, {args.oran} ({g}x{y}), toplam {toplam:.1f} sn -> {cikti}")
    if args.kuru:
        print(" ".join(f'"{c}"' if " " in c else c for c in cmd))
        return 0

    sonuc = subprocess.run(cmd)
    if sonuc.returncode != 0:
        return sonuc.returncode
    print(f"Bitti: {cikti}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
