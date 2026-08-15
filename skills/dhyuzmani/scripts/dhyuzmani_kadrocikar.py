# -*- coding: utf-8 -*-
"""
dhyuzmani — kadro listesi çıkarıcı.

DHY kura sonuç CSV'lerinden belirtilen branşın kadrolarını okur ve birim düzeyinde
gruplar. CSV'ler hekim ad-soyadı içerdiği için bu script onları YALNIZ okur;
çıktısına ad-soyad yazmaz (hastane düzeyinde toplu veri üretir).

Kullanım:
    python dhyuzmani_kadrocikar.py <csv_klasoru> [--brans "BEYİN VE SİNİR CERRAHİSİ"] [--json cikti.json]

CSV şeması (dhy_ocr_parse üretimi):
    sira_no, basvuru_no, ad_soyad, unvan, brans, birim_kodu, birim_adi, il, genel_kura, _sayfa, _uyari
"""
import os
import sys
import csv
import json
import glob
import argparse
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

VARSAYILAN_BRANS = "BEYİN VE SİNİR CERRAHİSİ"

# Türkçe büyük harf: ASCII upper() 'i'yi 'I' yapar, "beyin" -> "BEYIN" tutmaz
TR_BUYUK = str.maketrans("iıüöçşğ", "İIÜÖÇŞĞ")


def buyuk(s):
    return s.translate(TR_BUYUK).upper()

# OCR kuyruk artıklarını temizlemek için bilinen birim son ekleri
SON_EKLER = (
    "DEVLET HASTANESİ", "ARAŞTIRMA HASTANESİ", "ŞEHİR HASTANESİ",
    "NUMUNE HASTANESİ", "HASTALIKLARI HASTANESİ", "İLÇE SAĞLIK MÜDÜRLÜĞÜ",
    "İL SAĞLIK MÜDÜRLÜĞÜ", "TOPLUM SAĞLIĞI MERKEZİ", "ÜNİVERSİTESİ",
)


def birim_normalize(ad):
    """OCR'ın satır sonuna eklediği imza/kaşe artıklarını at, kanonik ada indir."""
    ad = " ".join(ad.split())
    for ek in SON_EKLER:
        i = ad.find(ek)
        if i >= 0:
            ad = ad[: i + len(ek)]
            break
    duzelt = {
        "HASTANE NN!": "HASTANESİ",
        "HASTAN!": "HASTANESİ",
        "VAN ERCİŞ ŞEHİT RIDVAN ÇEVİK oonarfusın ESİ":
            "VAN ERCİŞ ŞEHİT RIDVAN ÇEVİK DEVLET HASTANESİ",
    }
    for yanlis, dogru in duzelt.items():
        ad = ad.replace(yanlis, dogru)
    return ad.strip()


def kadrolari_topla(csv_klasoru, brans=VARSAYILAN_BRANS):
    """CSV'leri tarar, branşa uyan satırları birim düzeyinde gruplar."""
    desen = os.path.join(csv_klasoru, "* DHY Sonuclar*.csv")
    dosyalar = sorted(glob.glob(desen))
    if not dosyalar:
        raise SystemExit(f"CSV bulunamadı: {desen}")

    birimler = defaultdict(lambda: {"il": "", "donemler": [], "genel_kura": 0, "birim_kodu": ""})
    for yol in dosyalar:
        donem = os.path.basename(yol).split(" ")[0]
        with open(yol, encoding="utf-8-sig") as f:
            for satir in csv.DictReader(f):
                if buyuk(satir.get("brans", "").strip()) != buyuk(brans):
                    continue
                birim = birim_normalize(satir["birim_adi"])
                kayit = birimler[birim]
                kayit["il"] = satir.get("il", "").strip()
                kayit["donemler"].append(donem)
                if satir.get("birim_kodu"):
                    kayit["birim_kodu"] = satir["birim_kodu"]
                if satir.get("genel_kura"):
                    kayit["genel_kura"] += 1

    sonuc = []
    for birim, v in birimler.items():
        sonuc.append({
            "birim": birim,
            "il": v["il"],
            "birim_kodu": v["birim_kodu"],
            "donemler": sorted(v["donemler"]),
            "kadro": len(v["donemler"]),
            "genel_kura": v["genel_kura"],
        })
    sonuc.sort(key=lambda r: (r["il"], r["birim"]))
    return sonuc, len(dosyalar)


def main():
    ap = argparse.ArgumentParser(description="DHY kura CSV'lerinden branş kadro listesi çıkarır")
    ap.add_argument("csv_klasoru", help="1XX DHY Sonuclar*.csv dosyalarının bulunduğu klasör")
    ap.add_argument("--brans", default=VARSAYILAN_BRANS, help="Aranacak uzmanlık branşı")
    ap.add_argument("--json", help="Çıktının yazılacağı JSON dosyası")
    args = ap.parse_args()

    kadrolar, n_donem = kadrolari_topla(args.csv_klasoru, args.brans)
    toplam = sum(k["kadro"] for k in kadrolar)
    print(f"branş: {args.brans}")
    print(f"dönem dosyası: {n_donem} | benzersiz birim: {len(kadrolar)} | toplam kadro: {toplam}")

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(kadrolar, f, ensure_ascii=False, indent=1)
        print("yazıldı:", args.json)
    else:
        for k in kadrolar:
            print(f"  {k['il']:15s} | {k['birim'][:60]:60s} | {','.join(k['donemler'])}")


if __name__ == "__main__":
    main()
