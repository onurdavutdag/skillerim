# -*- coding: utf-8 -*-
"""
dhyuzmani — öz-denetim.

Skill'de bir değişiklik yapıldığında elle koşturulan kontrolleri tek komutta toplar:
varlık dosyalarının bütünlüğü, KGM doğrulama değerleri, Türkçe büyük harf davranışı
ve (CSV klasörü verilirse) kadro sayıları. Hiçbir dosya yazmaz, web'e çıkmaz.

Kullanım:
    python -B dhyuzmani_dogrula.py                    # yalnız yerel varlık kontrolleri
    python -B dhyuzmani_dogrula.py <csv_klasoru>      # + kadro 88/127 kontrolü

Çıkış kodu: tüm kontroller geçerse 0, aksi hâlde 1.
"""
import sys
import json
import argparse

sys.stdout.reconfigure(encoding="utf-8")

from dhyuzmani_kadrocikar import kadrolari_topla
from dhyuzmani_mesafehesapla import kgm_yukle, ilce_yukle, mesafe_hesapla, ILCE_JSON
from dhyuzmani_yatakesle import yerel_harita

# Beklenen sabitler — kaynaklar değişirse burası da güncellenir
KADRO_BEKLENEN = (88, 127)          # 120-129. dönem: benzersiz birim / toplam kadro
KGM_DOGRULAMA = {                   # KGM cetveli, Hatay satırı (03.03.2026)
    "ADANA": 196, "GAZİANTEP": 194, "KAHRAMANMARAŞ": 176,
    "OSMANİYE": 127, "KİLİS": 146, "ŞANLIURFA": 333, "İSTANBUL": 1147,
}
# dhyuzmani-r-veri-kaynaklari.md §3'te kaynaklarıyla belgelenen dört web düzeltmesi.
# 12.08.2026'da haritanın bu değerlerden saptığı görüldü; sapma bir daha
# sessiz kalmasın diye burada denetlenir.
YATAK_DUZELTMELERI = {
    "HATAY DEFNE DEVLET HASTANESİ": 300,
    "GAZİANTEP ŞEHİR HASTANESİ": 1875,
    "ERZURUM ŞEHİR HASTANESİ": 1670,
    "KAHRAMANMARAŞ DEVLET HASTANESİ": 400,
}


def kontrol(ad, kosul, detay=""):
    isaret = "OK " if kosul else "HATA"
    print(f"  [{isaret}] {ad}" + (f" — {detay}" if detay else ""))
    return bool(kosul)


def main():
    ap = argparse.ArgumentParser(description="dhyuzmani öz-denetimi")
    ap.add_argument("csv_klasoru", nargs="?", help="verilirse kadro 88/127 de denetlenir")
    args = ap.parse_args()
    hepsi = True

    print("mesafe — KGM doğrulama değerleri (Hatay satırı):")
    kgm, ilce = kgm_yukle(), ilce_yukle()
    for il, beklenen in KGM_DOGRULAMA.items():
        km, _, _ = mesafe_hesapla("X", il, "HATAY", kgm, ilce)
        hepsi &= kontrol(f"HATAY-{il}", km == beklenen, f"{km} km (beklenen {beklenen})")
    # Türkçe büyük harf: küçük harfli il/referans da çözülmeli
    km, _, _ = mesafe_hesapla("X", "gaziantep", "hatay", kgm, ilce)
    hepsi &= kontrol("küçük harf il sorgusu (TR upper)", km == 194, f"{km} km")

    print("ilce_mesafe.json:")
    hepsi &= kontrol("46 ilçe kaydı", len(ilce) == 46, str(len(ilce)))
    eksik = [b for b, v in ilce.items() if v.get("hatay_km") is None]
    hepsi &= kontrol("hatay_km alanları dolu", not eksik, f"eksik: {eksik or 'yok'}")

    print("yatak_map.json:")
    harita = yerel_harita()
    hepsi &= kontrol("88 birim kaydı", len(harita) == 88, str(len(harita)))
    bos = [b for b, v in harita.items() if v is None]
    hepsi &= kontrol("null yatak yok", not bos, f"boş: {bos or 'yok'}")
    for birim, beklenen in YATAK_DUZELTMELERI.items():
        hepsi &= kontrol(f"web düzeltmesi: {birim}", harita.get(birim) == beklenen,
                         f"{harita.get(birim)} (beklenen {beklenen})")

    if args.csv_klasoru:
        print("kadro — kura CSV'leri:")
        kadrolar, n_donem = kadrolari_topla(args.csv_klasoru)
        toplam = sum(k["kadro"] for k in kadrolar)
        b_birim, b_kadro = KADRO_BEKLENEN
        hepsi &= kontrol("benzersiz birim", len(kadrolar) == b_birim,
                         f"{len(kadrolar)} (beklenen {b_birim}; yeni dönem eklendiyse sabiti güncelle)")
        hepsi &= kontrol("toplam kadro", toplam == b_kadro,
                         f"{toplam} (beklenen {b_kadro}; yeni dönem eklendiyse sabiti güncelle)")
        # harita ile kadro listesi aynı evreni mi anlatıyor?
        haritada_yok = [k["birim"] for k in kadrolar if k["birim"] not in harita]
        hepsi &= kontrol("tüm birimler yatak haritasında", not haritada_yok,
                         f"eksik: {haritada_yok or 'yok'}")
    else:
        print("kadro: atlandı (CSV klasörü verilmedi)")

    print("SONUÇ:", "tüm kontroller geçti" if hepsi else "HATA var — yukarıya bak")
    sys.exit(0 if hepsi else 1)


if __name__ == "__main__":
    main()
