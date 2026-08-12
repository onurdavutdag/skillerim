# -*- coding: utf-8 -*-
"""
dhyuzmani — yatak kapasitesi eşleştirici.

Önce yerel `assets/yatak_map.json` haritasına bakar (anında, çevrimdışı).
Haritada olmayan bir hastane çıkarsa KHGM "2. ve 3. Basamak Kamu Sağlık Tesisleri
Listesi"ni indirip önbelleğe alır ve bulanık ad eşleşmesiyle tescilli yatak sayısını
bulur. Önbellek: ~/.claude/.cache/dhyuzmani/khgm_tesisler.xls

UYARI: KHGM listesi 02.02.2023 tarihlidir — 6 Şubat 2023 depreminden önce.
Hatay ve Kahramanmaraş hastanelerinin fiilî kapasitesi tescilden farklı olabilir.

Kullanım:
    python dhyuzmani_yatak.py --json mesafeler.json --cikti yataklar.json
    python dhyuzmani_yatak.py --birim "SİİRT EĞİTİM VE ARAŞTIRMA HASTANESİ" --il SİİRT
"""
import os
import sys
import json
import difflib
import argparse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BURASI = os.path.dirname(os.path.abspath(__file__))
YATAK_JSON = os.path.join(BURASI, "..", "assets", "yatak_map.json")
ONBELLEK = os.path.join(os.path.expanduser("~"), ".claude", ".cache", "dhyuzmani")
KHGM_XLS = os.path.join(ONBELLEK, "khgm_tesisler.xls")
KHGM_URL = "https://dosyamerkez.saglik.gov.tr/Eklenti/45020/0/saglik-tesisleri-listesi-02022023xls.xls"

TR_BUYUK = str.maketrans("iıüöçşğ", "İIÜÖÇŞĞ")
GEREKSIZ = ("T.C. SAĞLIK BAKANLIĞI", "SAĞLIK BİLİMLERİ ÜNİVERSİTESİ", "T.C.", "SBÜ")


def buyuk(s):
    return s.translate(TR_BUYUK).upper()


def ad_normalize(s):
    s = buyuk(s)
    for parca in GEREKSIZ:
        s = s.replace(buyuk(parca), " ")
    s = s.replace(".", " ").replace("-", " ")
    return " ".join(s.split())


def yerel_harita():
    with open(YATAK_JSON, encoding="utf-8") as f:
        return json.load(f)


def khgm_indir():
    """KHGM tesis listesini önbelleğe indirir (yalnız gerektiğinde)."""
    if os.path.exists(KHGM_XLS):
        return KHGM_XLS
    os.makedirs(ONBELLEK, exist_ok=True)
    print("KHGM tesis listesi indiriliyor (~5 MB)...")
    urllib.request.urlretrieve(KHGM_URL, KHGM_XLS)
    return KHGM_XLS


def khgm_yukle():
    """[(il, ilce, normalize_ad, yatak, ham_ad)] listesi döndürür."""
    import xlrd
    ws = xlrd.open_workbook(khgm_indir()).sheet_by_index(0)
    kayitlar = []
    for i in range(1, ws.nrows):
        satir = ws.row(i)
        try:
            yatak = int(float(satir[9].value))
        except (ValueError, TypeError):
            continue
        kayitlar.append((
            buyuk(str(satir[2].value)), buyuk(str(satir[3].value)),
            ad_normalize(str(satir[4].value)), yatak, str(satir[4].value).strip(),
        ))
    return kayitlar


def khgm_esle(birim, il, kayitlar):
    """Aynı ildeki tesisler içinde en yakın adı bulur. (yatak, ham_ad, oran)."""
    hedef = ad_normalize(birim)
    adaylar = [k for k in kayitlar if k[0] == buyuk(il)]
    en_iyi, en_oran = None, 0.0
    for k in adaylar:
        oran = difflib.SequenceMatcher(None, hedef, k[2]).ratio()
        if k[1] and k[1] in hedef:      # ilçe adı birimde geçiyorsa güçlü ipucu
            oran += 0.15
        if oran > en_oran:
            en_iyi, en_oran = k, oran
    if en_iyi and en_oran >= 0.60:
        return en_iyi[3], en_iyi[4], round(en_oran, 2)
    return None, None, round(en_oran, 2)


def main():
    ap = argparse.ArgumentParser(description="Hastanelerin tescilli yatak kapasitesi")
    ap.add_argument("--birim")
    ap.add_argument("--il")
    ap.add_argument("--json", help="dhyuzmani_mesafe.py çıktısı")
    ap.add_argument("--cikti")
    args = ap.parse_args()

    harita = yerel_harita()
    khgm = None   # yalnız gerekirse yüklenir

    def yatak_bul(birim, il):
        nonlocal khgm
        if birim in harita and harita[birim] is not None:
            return harita[birim], "yerel harita (KHGM 02.02.2023 türevi)"
        if khgm is None:
            khgm = khgm_yukle()
        yatak, ham, oran = khgm_esle(birim, il or "", khgm)
        if yatak is None:
            return None, f"KHGM'de eşleşme yok (en iyi oran {oran})"
        return yatak, f"KHGM listesi, eşleşen kayıt: {ham} (oran {oran})"

    if args.birim:
        yatak, kaynak = yatak_bul(args.birim, args.il)
        print(f"{args.birim}: {yatak if yatak is not None else '?'} yatak  ({kaynak})")
        return

    if not args.json:
        raise SystemExit("--birim veya --json verilmeli")

    with open(args.json, encoding="utf-8") as f:
        kayitlar = json.load(f)

    sonuc, bos = [], 0
    for k in kayitlar:
        yatak, kaynak = yatak_bul(k["birim"], k.get("il"))
        if yatak is None:
            bos += 1
        sonuc.append({**k, "yatak": yatak, "yatak_kaynagi": kaynak})

    print(f"yatak dolu: {len(sonuc) - bos}/{len(sonuc)}")
    if args.cikti:
        os.makedirs(os.path.dirname(os.path.abspath(args.cikti)), exist_ok=True)
        with open(args.cikti, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=1)
        print("yazıldı:", args.cikti)


if __name__ == "__main__":
    main()
