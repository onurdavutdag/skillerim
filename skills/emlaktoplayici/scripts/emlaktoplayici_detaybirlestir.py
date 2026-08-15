# -*- coding: utf-8 -*-
"""Detay JSON'unu KAYIT JSON'una katar (detayekle.py'nin Excel yerine sema uzerinde calisani).

Neden ayri bir script: `detayekle.py` detay alanlarini dogrudan .xlsx'e yazar.
Ama deprem skoru kayit JSON'undan hesaplanir ve iki bilesenini detay alanlarindan
alir - `aciklama` (beyan) ve `toplam_kat` (kat). Detay yalniz Excel'e islenirse
skorlayici onlari HIC gormez; 15.08.2026 kosusunda tam olarak bu oldu ve tablo
hem aciklamasiz hem skorsuz cikti. Zincirin dogru sirasi sudur:

    tarama -> DETAY -> detaybirlestir -> depremskorla -> excelbas

Girdi : 1..n kayit JSON  +  1..n detay JSON  (sozluk ya da {"ilanlar": [...]} bicimi)
Cikti : her kayit JSON'u icin ayni adla bir cikti dosyasi (--cikti-dizin) ya da
        tek girdi verildiginde tek dosya (--cikti)

Kullanim:
    python -B emlaktoplayici_detaybirlestir.py --kayit a.json b.json \
        --detay "hepsiemlak detay.json" --cikti-dizin tmp/birlesik/

TEMEL KURAL: dolu alanin uzerine YAZILMAZ (--uzerine-yaz ile istenirse yazilir) -
`detayekle.py` ile ayni sozlesme. Cakisan degerler sessizce yutulmaz, sayilir ve
stderr'e "celiski" olarak bildirilir.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emlaktoplayici_detayekle import sozluge_cevir  # noqa: E402  (ayni klasor, tek dogru)

# Detay gecisinden gelen ve kayda katilan alanlar. Kimlik ve fiyat alanlari
# (ilan_no, site, baslik, fiyat, ilce, link) BILEREK disaridadir: onlar liste
# taramasinin sorumlulugudur, detay sayfasindan gelen bir fark tekillestirme
# anahtarini kaydirir.
BIRLESTIRILEN = ("tapu_durumu", "aciklama", "bina_yasi", "bina_yasi_bant",
                 "toplam_kat", "kat", "isitma", "m2_net")

BOS_SAYILAN = (None, "", "Belirtilmemis", "Belirtilmemiş")


def json_oku(yol):
    p = Path(yol)
    if not p.exists():
        sys.exit("Dosya yok: {}".format(p))
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("Bozuk JSON ({}): {}".format(p.name, e))


def detaylari_oku(yollar):
    """Birden cok detay JSON'unu tek sozlukte birlestirir. Sonraki dosya oncekini ezer."""
    toplu = {}
    for yol in yollar:
        toplu.update(sozluge_cevir(json_oku(yol)))
    return {str(k).strip(): v for k, v in toplu.items()}


def kayda_kat(kayit, detay_kaydi, uzerine_yaz, sayac):
    """Tek bir ilana detay alanlarini isler. Doner: True (bir sey yazildiysa)."""
    yazildi = False
    for alan in BIRLESTIRILEN:
        yeni = detay_kaydi.get(alan)
        if yeni in BOS_SAYILAN:
            continue
        eldeki = kayit.get(alan)
        if eldeki not in BOS_SAYILAN:
            if str(eldeki).strip() != str(yeni).strip():
                sayac["celiski"] += 1
                sayac["celiski_ornek"].append(
                    "{} · {}: liste={!r} detay={!r}".format(
                        kayit.get("ilan_no"), alan, eldeki, yeni))
            if not uzerine_yaz:
                sayac["korunan"] += 1
                continue
            sayac["uzerine"] += 1
        if alan == "aciklama":
            yeni = str(yeni).strip()
        kayit[alan] = yeni
        sayac["yazilan"] += 1
        yazildi = True
    return yazildi


def main():
    ap = argparse.ArgumentParser(description="Detay JSON'unu kayit JSON'una katar.")
    ap.add_argument("--kayit", nargs="+", required=True, help="1..n tarama (kayit) JSON'u")
    ap.add_argument("--detay", nargs="+", required=True, help="1..n detay JSON'u")
    ap.add_argument("--cikti", default=None, help="Tek kayit dosyasi verildiyse hedef yol")
    ap.add_argument("--cikti-dizin", default=None,
                    help="Her kayit dosyasi ayni adla buraya yazilir")
    ap.add_argument("--uzerine-yaz", action="store_true",
                    help="Dolu alanlarin uzerine de yazar (varsayilan: dolu alan KORUNUR)")
    a = ap.parse_args()

    if not a.cikti and not a.cikti_dizin:
        sys.exit("--cikti ya da --cikti-dizin verilmeli.")
    if a.cikti and len(a.kayit) > 1:
        sys.exit("Birden cok kayit dosyasi icin --cikti-dizin kullan.")

    detay = detaylari_oku(a.detay)
    if not detay:
        sys.exit("Detay JSON'larinda kayit yok - yapacak bir sey yok.")

    sayac = {"yazilan": 0, "korunan": 0, "uzerine": 0, "celiski": 0, "celiski_ornek": []}
    eslesen_toplam = detaysiz_toplam = 0
    kullanilan = set()

    for yol in a.kayit:
        veri = json_oku(yol)
        ilanlar = veri.get("ilanlar")
        if not isinstance(ilanlar, list):
            sys.exit("{}: 'ilanlar' listesi yok - bu bir kayit JSON'u mu?".format(Path(yol).name))

        eslesen = detaysiz = 0
        for kayit in ilanlar:
            no = str(kayit.get("ilan_no") or "").strip()
            detay_kaydi = detay.get(no)
            if not isinstance(detay_kaydi, dict):
                detaysiz += 1
                continue
            kullanilan.add(no)
            eslesen += 1
            kayda_kat(kayit, detay_kaydi, a.uzerine_yaz, sayac)

        # Sema sozlesmesi: alan silinmez, bulunamayan null kalir (0 != null).
        for kayit in ilanlar:
            for alan in BIRLESTIRILEN:
                kayit.setdefault(alan, None)

        meta = veri.setdefault("meta", {})
        not_metni = "detay birlestirildi ({}/{} ilan)".format(eslesen, len(ilanlar))
        meta["notlar"] = "{} · {}".format(meta["notlar"], not_metni) if meta.get("notlar") else not_metni

        hedef = Path(a.cikti) if a.cikti else Path(a.cikti_dizin) / Path(yol).name
        hedef.parent.mkdir(parents=True, exist_ok=True)
        hedef.write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")

        dolu = lambda alan: sum(1 for k in ilanlar if k.get(alan) not in BOS_SAYILAN)
        print("{}: {} ilan | detayi eslesen {} | detaysiz {} | aciklama dolu {} | "
              "toplam_kat dolu {} -> {}".format(
                  Path(yol).name, len(ilanlar), eslesen, detaysiz,
                  dolu("aciklama"), dolu("toplam_kat"), hedef))
        eslesen_toplam += eslesen
        detaysiz_toplam += detaysiz

    artan = [no for no in detay if no not in kullanilan]
    print("TOPLAM: detay kaydi {} | eslesen {} | detaysiz kalan satir {} | yazilan alan {} | "
          "korunan dolu alan {} | uzerine yazilan {}".format(
              len(detay), eslesen_toplam, detaysiz_toplam,
              sayac["yazilan"], sayac["korunan"], sayac["uzerine"]), file=sys.stderr)
    if artan:
        print("UYARI: {} detay kaydi hicbir kayitla eslesmedi (ornek: {})".format(
            len(artan), ", ".join(artan[:5])), file=sys.stderr)
    if sayac["celiski"]:
        print("CELISKI: {} alanda liste ile detay ayni degil{}".format(
            sayac["celiski"], " (dolu alan korundu)" if not a.uzerine_yaz else " (uzerine yazildi)"),
            file=sys.stderr)
        for satir in sayac["celiski_ornek"][:10]:
            print("  " + satir, file=sys.stderr)


if __name__ == "__main__":
    main()
