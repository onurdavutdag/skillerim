# -*- coding: utf-8 -*-
"""
dhyuzmani — karayolu mesafe hesaplayıcı.

Bir hastanenin referans şehre karayolu mesafesini verir:
  * İl merkezindeki hastane  -> KGM İller Arası Mesafe Cetveli'nden doğrudan (kesin)
  * İlçe hastanesi           -> il merkezi mesafesi + ilçe ofseti (yaklaşık, '~' ile işaretli)

Referans şehir varsayılan olarak HATAY'dır (Antakya). Hatay için ilçe ofsetleri
rota yönü gözetilerek doğrulanmıştır (`ofset_hatay`). Başka bir referans şehir
seçilirse yön bilgisi geçerliliğini yitirir; bu durumda ilçe-il merkezi uzaklığı
işaretsiz belirsizlik olarak raporlanır.

Kullanım:
    python dhyuzmani_mesafe.py --birim "SİİRT EĞİTİM VE ARAŞTIRMA HASTANESİ" --il SİİRT
    python dhyuzmani_mesafe.py --json kadrolar.json --cikti mesafeler.json [--referans HATAY]
"""
import os
import sys
import json
import argparse

sys.stdout.reconfigure(encoding="utf-8")

BURASI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BURASI, "..", "assets")
KGM_XLSX = os.path.join(ASSETS, "kgm_il_mesafe.xlsx")
ILCE_JSON = os.path.join(ASSETS, "ilce_mesafe.json")

VARSAYILAN_REFERANS = "HATAY"

# KGM cetvelindeki başlıklar bazı iller için parantezli yazılır
KGM_AD_ESLEME = {
    "KOCAELİ": "KOCAELİ (İZMİT)",
    "SAKARYA": "SAKARYA (ADAPAZARI)",
    "MERSİN": "MERSİN",
    "İÇEL": "MERSİN",
}


def kgm_yukle():
    """KGM cetvelini {il_a: {il_b: km}} sözlüğüne çevirir."""
    import openpyxl
    ws = openpyxl.load_workbook(KGM_XLSX, data_only=True)["Sayfa1"]
    satirlar = list(ws.iter_rows(values_only=True))
    basliklar = [c for c in satirlar[1][2:] if c]
    tablo = {}
    for satir in satirlar[2:]:
        if not satir[1]:
            continue
        il = str(satir[1]).strip().upper()
        tablo[il] = {}
        for j, hedef in enumerate(basliklar):
            deger = satir[2 + j]
            if isinstance(deger, (int, float)):
                tablo[il][str(hedef).strip().upper()] = int(deger)
    return tablo


def ilce_yukle():
    with open(ILCE_JSON, encoding="utf-8") as f:
        return json.load(f)


def il_kgm_adi(il):
    il = il.strip().upper()
    return KGM_AD_ESLEME.get(il, il)


def mesafe_hesapla(birim, il, referans=VARSAYILAN_REFERANS, kgm=None, ilce=None):
    """(km, yaklasik_mi, aciklama) döndürür. Bulunamazsa km None olur."""
    kgm = kgm if kgm is not None else kgm_yukle()
    ilce = ilce if ilce is not None else ilce_yukle()
    referans = il_kgm_adi(referans)
    il_adi = il_kgm_adi(il)

    if il_adi == referans:
        il_km = 0
    else:
        il_km = kgm.get(referans, {}).get(il_adi)
    if il_km is None:
        return None, True, f"KGM cetvelinde {referans}-{il_adi} bulunamadı"

    kayit = ilce.get(birim)
    if kayit is None:
        # il merkezi hastanesi varsayımı
        return il_km, False, "il merkezi (KGM resmî)"

    if referans == VARSAYILAN_REFERANS and kayit.get("hatay_km") is not None:
        return kayit["hatay_km"], True, f"ilçe, Hatay için doğrulanmış ofset ({kayit.get('not', '')})"

    # başka referans şehir: yön bilgisi geçersiz, işaretsiz belirsizlik bildirilir
    sapma = kayit.get("ilce_il_km")
    if sapma is None:
        return il_km, True, "ilçe ofseti bilinmiyor, il merkezi değeri kullanıldı"
    return il_km, True, f"ilçe, il merkezine ±{sapma} km (yön {referans} için doğrulanmadı)"


def main():
    ap = argparse.ArgumentParser(description="Hastanelerin referans şehre karayolu mesafesi")
    ap.add_argument("--birim", help="Tek hastane adı")
    ap.add_argument("--il", help="--birim ile birlikte hastanenin ili")
    ap.add_argument("--json", help="dhyuzmani_kadro.py çıktısı (toplu hesap)")
    ap.add_argument("--cikti", help="Toplu hesap sonucunun yazılacağı JSON")
    ap.add_argument("--referans", default=VARSAYILAN_REFERANS, help="Referans şehir (varsayılan HATAY)")
    args = ap.parse_args()

    kgm, ilce = kgm_yukle(), ilce_yukle()

    if args.birim:
        km, yak, aciklama = mesafe_hesapla(args.birim, args.il or "", args.referans, kgm, ilce)
        isaret = "~" if yak else ""
        print(f"{args.birim} -> {args.referans}: {isaret}{km} km  ({aciklama})")
        return

    if not args.json:
        raise SystemExit("--birim veya --json verilmeli")

    with open(args.json, encoding="utf-8") as f:
        kadrolar = json.load(f)

    sonuc, bulunamadi = [], 0
    for k in kadrolar:
        km, yak, aciklama = mesafe_hesapla(k["birim"], k["il"], args.referans, kgm, ilce)
        if km is None:
            bulunamadi += 1
        sonuc.append({**k, "km": km, "yaklasik": yak, "mesafe_notu": aciklama})
    sonuc.sort(key=lambda r: (r["km"] if r["km"] is not None else 10 ** 6, r["il"], r["birim"]))

    print(f"referans: {args.referans} | hesaplanan: {len(sonuc) - bulunamadi}/{len(sonuc)}")
    if args.cikti:
        os.makedirs(os.path.dirname(os.path.abspath(args.cikti)), exist_ok=True)
        with open(args.cikti, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=1)
        print("yazıldı:", args.cikti)


if __name__ == "__main__":
    main()
