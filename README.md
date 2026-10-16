# Müşteri Kaybı Tahmini (Customer Churn Prediction)

IBM Telco Customer Churn verisiyle uçtan uca churn tahmini: keşifsel analiz,
üç model karşılaştırması, risk segmentasyonu ve gelir etkisi.

**Ana teslimat:** `rapor.html` — tek dosyalık, tarayıcıda açılan analiz raporu.
Grafikler gömülü SVG'dir; dış bağlantı veya internet gerektirmez.

## Sonuçlar

| Model | ROC-AUC (test) | ROC-AUC (5 kat CV) | Duyarlılık |
|---|---|---|---|
| Lojistik regresyon | 0,841 | **0,845 ± 0,014** | **0,783** |
| Rastgele orman | 0,837 | 0,841 ± 0,013 | 0,743 |
| Extra Trees | 0,826 | 0,830 ± 0,013 | 0,709 |

- 7.043 müşteri, 21 değişken, kayıp oranı %26,5
- Taban oran %73,5 — bu veride doğruluk tek başına anlamsız
- En riskli %10'luk dilimde kayıp oranı %75,7 (rastgele aramanın **2,85 katı**)
- Yüksek risk grubu müşterilerin %35'ini kapsıyor, kaybedilen aylık gelirin %74,8'ini taşıyor

## Dosyalar

| Dosya | İçerik |
|---|---|
| `rapor.html` | Ana rapor (çift tıklayın) |
| `analiz.py` | EDA, model karşılaştırması, eşik taraması, değişken önemi |
| `rapor_verisi.py` | Çapraz doğrulama, risk grupları, ROC ve kazanım eğrisi verileri |
| `rapor_uret.py` | `rapor_verisi.json` → `rapor.html` |
| `sonuclar.txt`, `rapor_sonuclar.txt` | Ham konsol çıktıları; rapordaki her sayı buradan doğrulanabilir |
| `WA_Fn-UseC_-Telco-Customer-Churn.csv` | Kaynak veri (7.043 satır) |

## Çalıştırma

```bash
pip install -r requirements.txt
python analiz.py
python rapor_verisi.py
python rapor_uret.py
```

Bütün betiklerde `random_state=42` sabittir; aynı veriyle aynı sayılar üretilir.

## Veri kaynağı

IBM Telco Customer Churn (IBM Cognos Analytics örnek veri setleri). Kurgusal bir
telekom şirketinin müşteri kayıtlarıdır. Sentetik veri üretilmemiştir; rapordaki
bütün sayılar bu dosyadan hesaplanmıştır. Bulgular ilişkiseldir, nedensel değildir.
