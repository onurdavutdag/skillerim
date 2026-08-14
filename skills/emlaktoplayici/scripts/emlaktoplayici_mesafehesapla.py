# -*- coding: utf-8 -*-
"""Her ilana referans noktaya KUS UCUSU mesafe ekler (km).

Girdi : kayit JSON        Cikti : ayni JSON + her ilanda "mesafe_km"

Kullanim:
    python -B emlaktoplayici_mesafehesapla.py --kayit skorlu.json --cikti mesafeli.json --referans Antakya
    python -B emlaktoplayici_mesafehesapla.py --kayit k.json --cikti m.json --lat 36.2023 --lon 36.1613

UYARI: bu KARAYOLU mesafesi DEGILDIR. Ilanin kendi adresi yoksa ilce merkezi
kullanilir (assets/ilce_koordinat.json, hassasiyet ~2 km) ve bu, ciktida
"mesafe_yaklasik": true ile isaretlenir. Yaklasik deger kesinmis gibi sunulmaz.
"""
import argparse
import json
import math
import sys
import unicodedata
from pathlib import Path

VARLIK = Path(__file__).resolve().parent.parent / "assets"


def sadelestir(metin):
    if not metin:
        return ""
    esle = str.maketrans("çğıöşüÇĞİIÖŞÜ", "cgiosuCGIIOSU")
    d = str(metin).translate(esle)
    return unicodedata.normalize("NFKD", d).encode("ascii", "ignore").decode("ascii").lower()


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def main():
    ap = argparse.ArgumentParser(description="Referans noktaya kus ucusu mesafe ekler.")
    ap.add_argument("--kayit", required=True)
    ap.add_argument("--cikti", required=True)
    ap.add_argument("--referans", help="Ilce adi (assets/ilce_koordinat.json icinden)")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    a = ap.parse_args()

    merkezler = (json.loads((VARLIK / "ilce_koordinat.json").read_text(encoding="utf-8"))
                 .get("ilceler") or {})
    indeks = {sadelestir(k): v for k, v in merkezler.items()}

    if a.lat is not None and a.lon is not None:
        hedef, etiket = (a.lat, a.lon), "{:.4f},{:.4f}".format(a.lat, a.lon)
    elif a.referans:
        m = indeks.get(sadelestir(a.referans))
        if not m:
            sys.exit("Referans bulunamadi: {} (bilinenler: {})".format(
                a.referans, ", ".join(sorted(merkezler))))
        hedef, etiket = (m["lat"], m["lon"]), a.referans
    else:
        sys.exit("--referans ya da --lat/--lon vermelisin.")

    veri = json.loads(Path(a.kayit).read_text(encoding="utf-8"))
    ilanlar = veri.get("ilanlar") or []

    hesaplanan = yaklasik = 0
    for k in ilanlar:
        lat, lon, yak = k.get("lat"), k.get("lon"), False
        if lat is None or lon is None:
            m = indeks.get(sadelestir(k.get("ilce") or ""))
            if not m:
                k["mesafe_km"] = None
                continue
            lat, lon, yak = m["lat"], m["lon"], True
        k["mesafe_km"] = round(haversine(lat, lon, hedef[0], hedef[1]), 1)
        k["mesafe_yaklasik"] = yak
        hesaplanan += 1
        yaklasik += 1 if yak else 0

    veri.setdefault("meta", {})["mesafe_referansi"] = etiket
    Path(a.cikti).parent.mkdir(parents=True, exist_ok=True)
    Path(a.cikti).write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")

    print("{} ilan | mesafe hesaplanan: {} ({} tanesi ilce merkezinden, YAKLASIK) | referans: {}".format(
        len(ilanlar), hesaplanan, yaklasik, etiket))
    print("yazildi:", a.cikti)


if __name__ == "__main__":
    main()
