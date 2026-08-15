# -*- coding: utf-8 -*-
"""Her ilana 0-10 deprem risk skoru ve 6 bilesen sutunu ekler.

Olcek, agirliklar, kaynak kunyesi ve ZORUNLU uyari metni:
    references/emlaktoplayici-r-deprem-risk-olcegi.md

Girdi : kayit JSON (emlaktoplayici-r-excel-sozlesmesi.md §1)
Cikti : ayni kayit JSON + her ilanda "deprem": {skor, guven, bilesenler, neden}

Kullanim:
    python -B emlaktoplayici_depremskorla.py --kayit birlesik.json --cikti skorlu.json

TEMEL KURAL: hesaplanamayan bilesen BOS kalir. Ortalamayla, medyanla veya
"tipik degerle" DOLDURULMAZ - uydurulmus bir deger, hesaplanmamis bir degerden
daha zararlidir. Skorun yanina kac bilesenin hesaplandigi yazilir.
"""
import argparse
import json
import math
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

VARLIK = Path(__file__).resolve().parent.parent / "assets"
ONBELLEK = Path.home() / ".claude" / ".cache" / "emlaktoplayici"

GEM_URL = ("https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults"
           "/master/geojson/gem_active_faults_harmonized.geojson")
TR_BBOX = (25.0, 35.0, 45.0, 43.0)  # lon_min, lat_min, lon_max, lat_max

# Bilesen adi -> azami puan. Beyan ayri: additif duzeltici, normalize edilmez.
AZAMI = {"yonetmelik": 3.5, "ilce_hasar": 2.5, "fay": 2.0, "pga": 1.5, "kat": 1.0}
EN_AZ_BILESEN = 3          # bunun altinda skor URETILMEZ
SERT_KURAL_TABAN = 8.0     # orta/agir hasar beyani skoru buraya sabitler

YONETMELIK_BANTLARI = [  # (yapim yili ust siniri, puan, etiket)
    (1975, 3.5, "1975 oncesi"),
    (1997, 3.0, "1976-1997"),
    (2000, 2.0, "1998-2000"),
    (2006, 1.5, "2001-2006 (Hatay yapi denetim pilot ili)"),
    (2018, 1.0, "2007-2018"),
    (9999, 0.5, "2019 ve sonrasi (TBDY)"),
]

FAY_BANTLARI = [(1, 2.0), (3, 1.5), (10, 1.0), (25, 0.5), (float("inf"), 0.0)]
PGA_BANTLARI = [(0.2, 0.0), (0.4, 0.5), (0.6, 1.0), (float("inf"), 1.5)]
KAT_BANTLARI = [(3, 0.2), (5, 0.4), (8, 0.7), (float("inf"), 1.0)]

# En agir once - ilk eslesen kazanir.
BEYAN_KALIPLARI = [
    (r"agir\s*hasar", 3.0, "agir hasarli beyani", True),
    (r"orta\s*hasar", 2.5, "orta hasarli beyani", True),
    (r"az\s*hasar", 0.5, "az hasarli beyani", False),
    (r"guclendir", -1.0, "guclendirilmis beyani", False),
    (r"hasarsiz", -1.5, "hasarsiz beyani", False),
]


def sadelestir(metin):
    """TR harfleri ASCII'ye indirger, kucuk harfe cevirir - kalip eslesmesi icin."""
    if not metin:
        return ""
    esle = str.maketrans("çğıöşüÇĞİIÖŞÜ", "cgiosuCGIIOSU")
    d = str(metin).translate(esle)
    d = unicodedata.normalize("NFKD", d).encode("ascii", "ignore").decode("ascii")
    return d.lower()


def json_oku(yol):
    p = Path(yol)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


# ------------------------------------------------------------- bilesen 1: yonetmelik

def _yonetmelik_bandi(yapim_yili):
    for ust, puan, etiket in YONETMELIK_BANTLARI:
        if yapim_yili <= ust:
            return puan, etiket
    return None, None


def _yas_araligi(metin):
    """sahibinden bina yasini BANT olarak verir. Ornekler:
    '11-15 arası' -> (11, 15) · '31 ve üzeri' -> (31, None) · '4' -> (4, 4)
    """
    s = sadelestir(metin)
    sayilar = [int(x) for x in re.findall(r"\d+", s)]
    if not sayilar:
        return None
    if "uzeri" in s or "ustu" in s or "fazla" in s:
        return (sayilar[0], None)          # ust sinir yok: daha da eski olabilir
    if len(sayilar) >= 2:
        return (min(sayilar), max(sayilar))
    return (sayilar[0], sayilar[0])


def bilesen_yonetmelik(kayit, bu_yil):
    """Yasin kendisi ya da BANDI kullanilir.

    Bant tek bir yonetmelik araligina tam oturuyorsa deger kesindir. Iki aralige
    yayiliyorsa YUKSEK RISKLI olan alinir ve `Neden` metnine "bant, ust sinir"
    notu duser. Gerekce: bu bir ON ELEME aracidir; riski fazla gostermek insani
    daha yakindan bakmaya iter, eksik gostermek ise yanlis guven verir. Ortalama
    almak (interpolasyon) tahmindir, yapilmaz.
    """
    yas = kayit.get("bina_yasi")
    aralik = None
    if yas is not None:
        try:
            aralik = (int(yas), int(yas))
        except (TypeError, ValueError):
            aralik = None
    if aralik is None and kayit.get("bina_yasi_bant"):
        aralik = _yas_araligi(kayit["bina_yasi_bant"])
    if aralik is None:
        return None, None

    alt, ust = aralik
    yapim_yeni = bu_yil - alt                                  # olabilecek en yeni
    puan_yeni, etiket_yeni = _yonetmelik_bandi(yapim_yeni)
    if ust is None:
        puan_eski, etiket_eski = YONETMELIK_BANTLARI[0][1], YONETMELIK_BANTLARI[0][2]
        yapim_eski = None
    else:
        yapim_eski = bu_yil - ust                              # olabilecek en eski
        puan_eski, etiket_eski = _yonetmelik_bandi(yapim_eski)
    if puan_yeni is None or puan_eski is None:
        return None, None

    if puan_yeni == puan_eski:
        if alt == ust:
            return puan_yeni, "{} yapimi ({})".format(yapim_yeni, etiket_yeni)
        return puan_yeni, "{}-{} yapimi ({})".format(yapim_eski, yapim_yeni, etiket_yeni)

    puan = max(puan_yeni, puan_eski)
    etiket = etiket_eski if puan_eski >= puan_yeni else etiket_yeni
    eski_metin = yapim_eski if yapim_eski is not None else "?"
    return puan, "{}-{} yapimi, bant iki yonetmelige yayiliyor - ust sinir alindi ({})".format(
        eski_metin, yapim_yeni, etiket)


# ------------------------------------------------------------ bilesen 2: ilce hasar

class HasarTablosu:
    """Ham sayiyi degil YOGUNLUGU kullanir; 15 ilce arasinda min-maks olceklenir."""

    def __init__(self):
        self.yogunluk = {}
        self.alt = self.ust = None
        veri = json_oku(VARLIK / "hatay_ilce_hasar.json")
        if not veri:
            return
        for ilce, d in (veri.get("ilceler") or {}).items():
            nufus = d.get("nufus_2022")
            if not nufus:
                continue
            toplam = (d.get("yikik") or 0) + (d.get("acil") or 0) + (d.get("agir") or 0)
            self.yogunluk[sadelestir(ilce)] = (toplam / nufus) * 1000.0
        if self.yogunluk:
            self.alt, self.ust = min(self.yogunluk.values()), max(self.yogunluk.values())

    def puan(self, ilce):
        if not self.yogunluk or self.ust is None:
            return None, None
        y = self.yogunluk.get(sadelestir(ilce))
        if y is None:
            return None, None
        if self.ust == self.alt:
            oran = 0.0
        else:
            oran = (y - self.alt) / (self.ust - self.alt)
        puan = round(oran * AZAMI["ilce_hasar"], 2)
        return puan, "{} hasar yogunlugu {:.0f}/1000".format(ilce, y)


# --------------------------------------------------------------- bilesen 3: diri fay

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _nokta_parca_km(plat, plon, alat, alon, blat, blon):
    """Noktanin AB dogru parcasina uzakligi. Yerel duzlem yaklasimi - bu
    olceklerde (<100 km) hatasi ihmal edilebilir."""
    k = math.cos(math.radians(plat))
    px, py = plon * k, plat
    ax, ay = alon * k, alat
    bx, by = blon * k, blat
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return _haversine(plat, plon, alat, alon)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    qx, qy = ax + t * dx, ay + t * dy
    return _haversine(plat, plon, qy, qx / k if k else qx)


class FayHatlari:
    """GEM Global Active Faults (CC-BY). Depoda TUTULMAZ; ilk kullanimda indirilip
    ~/.claude/.cache/emlaktoplayici/ altina onbelleklenir. Inemezse bilesen BOS."""

    def __init__(self, indir=True):
        self.parcalar = []
        self.durum = "yok"
        yerel = VARLIK / "gem_diri_fay_tr.geojson"
        onbellek = ONBELLEK / "gem_diri_fay_tr.geojson"
        kaynak = yerel if yerel.exists() else (onbellek if onbellek.exists() else None)

        if kaynak is None and indir:
            kaynak = self._indir(onbellek)
        if kaynak is None:
            return

        veri = json_oku(kaynak)
        if not veri:
            self.durum = "bozuk onbellek"
            try:
                kaynak.unlink()  # bozuk onbellek kendini silsin, sonraki kosu tazelesin
            except OSError:
                pass
            return
        self._yukle(veri)
        self.durum = "hazir ({} parca)".format(len(self.parcalar))

    def _indir(self, hedef):
        import urllib.request
        try:
            hedef.parent.mkdir(parents=True, exist_ok=True)
            gecici = hedef.with_suffix(".indiriliyor")  # yarim indirme onbellege yerlesmesin
            with urllib.request.urlopen(GEM_URL, timeout=60) as cevap:
                ham = cevap.read().decode("utf-8")
            veri = json.loads(ham)
            kirpik = self._kirp(veri)
            gecici.write_text(json.dumps(kirpik), encoding="utf-8")
            gecici.replace(hedef)
            return hedef
        except Exception as e:  # ag yok, GEM tasindi, JSON bozuk - hepsi ayni sonuc
            self.durum = "indirilemedi ({})".format(type(e).__name__)
            return None

    @staticmethod
    def _kirp(veri):
        lon0, lat0, lon1, lat1 = TR_BBOX
        icinde = []
        for f in veri.get("features", []):
            g = f.get("geometry") or {}
            if g.get("type") not in ("LineString", "MultiLineString"):
                continue
            hatlar = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
            tutulan = [h for h in hatlar
                       if any(lon0 <= c[0] <= lon1 and lat0 <= c[1] <= lat1 for c in h)]
            if tutulan:
                icinde.append({"type": "Feature", "properties": {},
                               "geometry": {"type": "MultiLineString", "coordinates": tutulan}})
        return {"type": "FeatureCollection", "features": icinde}

    def _yukle(self, veri):
        for f in veri.get("features", []):
            g = f.get("geometry") or {}
            hatlar = [g["coordinates"]] if g.get("type") == "LineString" else g.get("coordinates", [])
            for hat in hatlar:
                for i in range(len(hat) - 1):
                    (x1, y1), (x2, y2) = hat[i][:2], hat[i + 1][:2]
                    self.parcalar.append((y1, x1, y2, x2))

    def puan(self, lat, lon):
        if not self.parcalar or lat is None or lon is None:
            return None, None
        en_yakin = min(_nokta_parca_km(lat, lon, *p) for p in self.parcalar)
        for ust, puan in FAY_BANTLARI:
            if en_yakin < ust:
                return puan, "faya {:.1f} km".format(en_yakin)
        return 0.0, "faya {:.1f} km".format(en_yakin)


# --------------------------------------------------------------------- bilesen 4: PGA

class PgaTablosu:
    """TUCBS WMS raster RENK dondurur, sayi degil. Renk->PGA cevrimi LUT'tan gelir.
    LUT bosken bilesen BOS kalir - sifir yazilmaz (bkz. tdth_renk_lut.json)."""

    def __init__(self):
        veri = json_oku(VARLIK / "tdth_renk_lut.json") or {}
        self.tablo = veri.get("tablo") or []
        self.hazir = bool(self.tablo)

    def puan(self, lat, lon):
        if not self.hazir:
            return None, None
        return None, None  # LUT kurulunca WMS sorgusu buraya gelir


# --------------------------------------------------------------------- bilesen 5: kat

def bilesen_kat(kayit):
    kat = kayit.get("toplam_kat")
    if kat is None:
        return None, None
    try:
        kat = int(kat)
    except (TypeError, ValueError):
        return None, None
    for ust, puan in KAT_BANTLARI:
        if kat <= ust:
            return puan, "{} katli bina".format(kat)
    return None, None


# ------------------------------------------------------------------- bilesen 6: beyan

def bilesen_beyan(kayit):
    """Doner: (puan, aciklama, sert_kural_mi)"""
    metin = sadelestir("{} {}".format(kayit.get("baslik") or "", kayit.get("aciklama") or ""))
    for kalip, puan, etiket, sert in BEYAN_KALIPLARI:
        if re.search(kalip, metin):
            return puan, etiket, sert
    return 0.0, None, False


# -------------------------------------------------------------------------- skorlama

def skorla(kayit, tablolar, bu_yil):
    hasar, fay, pga, merkezler = tablolar
    koordinat = kayit.get("lat"), kayit.get("lon")
    if koordinat[0] is None:
        merkez = (merkezler or {}).get(sadelestir(kayit.get("ilce") or ""))
        koordinat = (merkez["lat"], merkez["lon"]) if merkez else (None, None)
        merkezden = bool(merkez)
    else:
        merkezden = False

    bilesenler, nedenler = {}, []

    for ad, (puan, neden) in {
        "yonetmelik": bilesen_yonetmelik(kayit, bu_yil),
        "ilce_hasar": hasar.puan(kayit.get("ilce") or ""),
        "fay": fay.puan(*koordinat),
        "pga": pga.puan(*koordinat),
        "kat": bilesen_kat(kayit),
    }.items():
        bilesenler[ad] = puan
        if puan is not None and neden:
            nedenler.append((puan, "{} ({:.1f})".format(neden, puan)))

    beyan_puan, beyan_neden, sert = bilesen_beyan(kayit)
    bilesenler["beyan"] = beyan_puan
    if beyan_neden:
        nedenler.append((abs(beyan_puan), "{} ({:+.1f})".format(beyan_neden, beyan_puan)))

    hesaplanan = [a for a in AZAMI if bilesenler[a] is not None]
    toplam_bilesen = len(hesaplanan) + 1  # beyan daima hesaplanir

    if len(hesaplanan) < EN_AZ_BILESEN:
        return {"skor": None, "guven": "({}/6)".format(toplam_bilesen),
                "bilesenler": bilesenler, "neden": "Yetersiz veri"}

    # Eksik bilesen ortalamayla DOLDURULMAZ; var olanlarin azamisine gore olceklenir.
    ham = sum(bilesenler[a] for a in hesaplanan)
    azami = sum(AZAMI[a] for a in hesaplanan)
    skor = (ham / azami) * 10.0 + beyan_puan
    skor = max(0.0, min(10.0, skor))

    if sert:
        skor = max(skor, SERT_KURAL_TABAN)

    nedenler.sort(key=lambda x: -x[0])
    metin = " · ".join(n for _, n in nedenler[:3])
    if merkezden and (bilesenler["fay"] is not None or bilesenler["pga"] is not None):
        metin += " · [ilce merkezinden]"
    if sert:
        metin = "HASAR BEYANI - skor >= {:.0f}'e sabitlendi · ".format(SERT_KURAL_TABAN) + metin

    return {"skor": round(skor, 1), "guven": "({}/6)".format(toplam_bilesen),
            "bilesenler": bilesenler, "neden": metin}


def main():
    ap = argparse.ArgumentParser(description="Ilanlara deprem risk skoru ekler.")
    ap.add_argument("--kayit", required=True)
    ap.add_argument("--cikti", required=True)
    ap.add_argument("--yil", type=int, default=datetime.now().year,
                    help="Bina yasinin cikarilacagi referans yil")
    ap.add_argument("--fay-indirme-yok", action="store_true",
                    help="GEM verisini indirmeyi dener degil - fay bileseni bos kalir")
    a = ap.parse_args()

    veri = json_oku(a.kayit)
    if veri is None:
        sys.exit("Kayit JSON okunamadi: {}".format(a.kayit))

    hasar = HasarTablosu()
    fay = FayHatlari(indir=not a.fay_indirme_yok)
    pga = PgaTablosu()
    merkezler = {sadelestir(k): v for k, v in
                 ((json_oku(VARLIK / "ilce_koordinat.json") or {}).get("ilceler") or {}).items()}
    tablolar = (hasar, fay, pga, merkezler)

    ilanlar = veri.get("ilanlar") or []
    for k in ilanlar:
        k["deprem"] = skorla(k, tablolar, a.yil)

    Path(a.cikti).parent.mkdir(parents=True, exist_ok=True)
    Path(a.cikti).write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")

    skorlu = [k for k in ilanlar if k["deprem"]["skor"] is not None]
    print("{} ilan | skor uretilen: {} | yetersiz veri: {}".format(
        len(ilanlar), len(skorlu), len(ilanlar) - len(skorlu)))
    print("bilesen durumu: ilce_hasar={} | fay={} | pga={}".format(
        "hazir" if hasar.yogunluk else "YOK",
        fay.durum,
        "hazir" if pga.hazir else "LUT BOS - bilesen bos birakildi"))
    if skorlu:
        s = sorted(k["deprem"]["skor"] for k in skorlu)
        print("skor araligi: {:.1f} - {:.1f} | medyan {:.1f}".format(s[0], s[-1], s[len(s) // 2]))
    print("yazildi:", a.cikti)


if __name__ == "__main__":
    main()
