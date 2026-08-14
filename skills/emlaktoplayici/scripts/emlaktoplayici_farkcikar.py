# -*- coding: utf-8 -*-
"""Iki taramayi karsilastirir: YENI / FIYATI DEGISEN / KALKAN ilanlar.

Girdi : iki kayit JSON (onceki ve simdiki)
Cikti : fark JSON + okunur ozet

Kullanim:
    python -B emlaktoplayici_farkcikar.py --onceki eski.json --simdiki yeni.json --cikti fark.json

Eslesme anahtari (site, ilan_no) ciftidir - ayni ilan numarasi farkli sitelerde
farkli ilanlara ait olabilir, tek basina ilan_no yeterli degildir.
"""
import argparse
import json
import sys
from pathlib import Path


def yukle(yol):
    p = Path(yol)
    if not p.exists():
        sys.exit("Dosya yok: {}".format(p))
    veri = json.loads(p.read_text(encoding="utf-8"))
    indeks = {}
    for k in veri.get("ilanlar") or []:
        indeks[(k.get("site"), str(k.get("ilan_no")))] = k
    return veri, indeks


def main():
    ap = argparse.ArgumentParser(description="Iki taramayi karsilastirir.")
    ap.add_argument("--onceki", required=True)
    ap.add_argument("--simdiki", required=True)
    ap.add_argument("--cikti", required=True)
    a = ap.parse_args()

    _, eski = yukle(a.onceki)
    _, yeni = yukle(a.simdiki)

    yeni_ilanlar = [yeni[k] for k in yeni.keys() - eski.keys()]
    kalkanlar = [eski[k] for k in eski.keys() - yeni.keys()]

    degisenler = []
    for anahtar in eski.keys() & yeni.keys():
        e, y = eski[anahtar], yeni[anahtar]
        if e.get("fiyat") != y.get("fiyat") and e.get("fiyat") and y.get("fiyat"):
            degisenler.append({
                "site": y.get("site"), "ilan_no": y.get("ilan_no"), "baslik": y.get("baslik"),
                "ilce": y.get("ilce"), "link": y.get("link"),
                "onceki_fiyat": e["fiyat"], "simdiki_fiyat": y["fiyat"],
                "degisim": y["fiyat"] - e["fiyat"],
                "degisim_yuzde": round((y["fiyat"] - e["fiyat"]) / e["fiyat"] * 100, 1),
            })

    sadelestir = lambda liste: [
        {alan: k.get(alan) for alan in ("site", "ilan_no", "baslik", "fiyat", "ilce", "link")}
        for k in liste
    ]
    fark = {
        "onceki_dosya": a.onceki, "simdiki_dosya": a.simdiki,
        "ozet": {"yeni": len(yeni_ilanlar), "fiyati_degisen": len(degisenler),
                 "kalkan": len(kalkanlar), "degismeden_duran":
                     len(eski.keys() & yeni.keys()) - len(degisenler)},
        "yeni": sadelestir(yeni_ilanlar),
        "fiyati_degisen": sorted(degisenler, key=lambda x: x["degisim"]),
        "kalkan": sadelestir(kalkanlar),
    }

    Path(a.cikti).parent.mkdir(parents=True, exist_ok=True)
    Path(a.cikti).write_text(json.dumps(fark, ensure_ascii=False, indent=1), encoding="utf-8")

    o = fark["ozet"]
    print("{} yeni, {} fiyati degisen, {} kalkan, {} degismeden duruyor".format(
        o["yeni"], o["fiyati_degisen"], o["kalkan"], o["degismeden_duran"]))
    for d in fark["fiyati_degisen"][:10]:
        print("  {:>+12,} TL ({:+.1f}%)  {}  [{}]".format(
            d["degisim"], d["degisim_yuzde"], (d["baslik"] or "")[:48], d["ilan_no"]))
    print("yazildi:", a.cikti)


if __name__ == "__main__":
    main()
