# -*- coding: utf-8 -*-
"""Tek dosyalik portfolyo raporu uretir: rapor.html (gomulu SVG grafikler)."""
import json, os, io

KLASOR = os.path.dirname(os.path.abspath(__file__))
HEDEF = os.path.join(KLASOR, "proje")
os.makedirs(HEDEF, exist_ok=True)
D = json.load(open(os.path.join(KLASOR, "rapor_verisi.json"), encoding="utf-8"))

MOR, CAM, YESIL, KIRMIZI, SARI = "#8b5cf6", "#59d9ff", "#2dd4a7", "#ff5668", "#f0b429"


def cubuk(basliklar, degerler, renkler, birim="%", genislik=680, satir=42, etiket_g=190):
    """Yatay cubuk grafik (SVG)."""
    h = satir * len(degerler) + 16
    enb = max(degerler)
    p = [f'<svg viewBox="0 0 {genislik} {h}" role="img" class="chart">']
    for i, (b, d, r) in enumerate(zip(basliklar, degerler, renkler)):
        y = i * satir + 8
        uz = (genislik - etiket_g - 70) * d / enb
        p.append(f'<text x="0" y="{y+21}" class="c-lbl">{b}</text>')
        p.append(f'<rect x="{etiket_g}" y="{y+8}" width="{genislik-etiket_g-70}" height="18" rx="9" class="c-trk"/>')
        p.append(f'<rect x="{etiket_g}" y="{y+8}" width="{uz:.1f}" height="18" rx="9" fill="{r}"/>')
        v = f"%{d}".replace(".", ",") if birim == "%" else f"{d}"
        p.append(f'<text x="{genislik-62}" y="{y+22}" class="c-val">{v}</text>')
    p.append("</svg>")
    return "".join(p)


def egri(seriler, x_etiket, y_etiket, kosegen=False, genislik=620, yukseklik=380):
    """Cok serili cizgi grafigi (0-1 veya 0-100 olcegi)."""
    sol, alt, ust, sag = 56, 46, 18, 14
    gw, gh = genislik - sol - sag, yukseklik - alt - ust
    p = [f'<svg viewBox="0 0 {genislik} {yukseklik}" role="img" class="chart">']
    for t in range(0, 101, 25):
        y = ust + gh - gh * t / 100
        p.append(f'<line x1="{sol}" y1="{y:.1f}" x2="{sol+gw}" y2="{y:.1f}" class="c-grid"/>')
        p.append(f'<text x="{sol-10}" y="{y+4:.1f}" class="c-tick" text-anchor="end">{t}</text>')
    for t in range(0, 101, 25):
        x = sol + gw * t / 100
        p.append(f'<text x="{x:.1f}" y="{ust+gh+22}" class="c-tick" text-anchor="middle">{t}</text>')
    p.append(f'<line x1="{sol}" y1="{ust+gh}" x2="{sol+gw}" y2="{ust+gh}" class="c-axis"/>')
    p.append(f'<line x1="{sol}" y1="{ust}" x2="{sol}" y2="{ust+gh}" class="c-axis"/>')
    if kosegen:
        p.append(f'<line x1="{sol}" y1="{ust+gh}" x2="{sol+gw}" y2="{ust}" class="c-diag"/>')
    for ad, xs, ys, renk in seriler:
        d = " ".join(("M" if i == 0 else "L") + f"{sol+gw*x/100:.1f},{ust+gh-gh*y/100:.1f}"
                     for i, (x, y) in enumerate(zip(xs, ys)))
        p.append(f'<path d="{d}" fill="none" stroke="{renk}" stroke-width="2.6" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
    p.append(f'<text x="{sol+gw/2:.0f}" y="{yukseklik-6}" class="c-ax-lbl" text-anchor="middle">{x_etiket}</text>')
    p.append(f'<text x="14" y="{ust+gh/2:.0f}" class="c-ax-lbl" text-anchor="middle" '
             f'transform="rotate(-90 14 {ust+gh/2:.0f})">{y_etiket}</text>')
    p.append("</svg>")
    return "".join(p)


# ---------------------------------------------------------------- grafikler
g_sozlesme = cubuk(["Aydan aya (3.875)", "1 yıllık (1.473)", "2 yıllık (1.695)"],
                   [42.7, 11.3, 2.8], [KIRMIZI, SARI, YESIL])
g_kidem = cubuk(["0–6 ay (1.481)", "7–12 ay (705)", "13–24 ay (1.024)",
                 "25–48 ay (1.594)", "49–72 ay (2.239)"],
                [52.9, 35.9, 28.7, 20.4, 9.5], [KIRMIZI, KIRMIZI, SARI, CAM, YESIL])
g_odeme = cubuk(["Elektronik çek (2.365)", "Posta çeki (1.612)",
                 "Banka transferi (1.544)", "Kredi kartı (1.522)"],
                [45.3, 19.1, 16.7, 15.2], [KIRMIZI, SARI, CAM, YESIL])
g_internet = cubuk(["Fiber optik (3.096)", "DSL (2.421)", "İnternet yok (1.526)"],
                   [41.9, 19.0, 7.4], [KIRMIZI, SARI, YESIL])

roc = D["roc"]
g_roc = egri([("Lojistik regresyon", [v * 100 for v in roc["fpr"]], [v * 100 for v in roc["tpr"]], MOR)],
             "Yanlış alarm oranı (%)", "Yakalama oranı (%)", kosegen=True)
kz = D["kazanim"]
g_kazanim = egri([("Model", [k["yuzde"] for k in kz], [k["yakalanan"] for k in kz], CAM)],
                 "Aranan müşteri dilimi (%)", "Yakalanan kayıp (%)", kosegen=True)

cm = D["karisiklik"]
g_matris = f"""<div class="cm">
  <div class="cm-cell cm-head"></div><div class="cm-cell cm-head">Tahmin: Kalır</div><div class="cm-cell cm-head">Tahmin: Ayrılır</div>
  <div class="cm-cell cm-head">Gerçek: Kalmış</div><div class="cm-cell cm-ok">{cm[0][0]}</div><div class="cm-cell cm-no">{cm[0][1]}</div>
  <div class="cm-cell cm-head">Gerçek: Ayrılmış</div><div class="cm-cell cm-no">{cm[1][0]}</div><div class="cm-cell cm-ok">{cm[1][1]}</div>
</div>"""

G = D["gruplar"]


def grp(ad, alan):
    return G[ad][alan]


def tl(v):
    return f"{v:,.0f}".replace(",", ".")


HTML = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Müşteri Kaybı Tahmini — Analiz Raporu</title>
<meta name="description" content="IBM Telco Customer Churn verisiyle uçtan uca müşteri kaybı tahmini: keşifsel analiz, üç model karşılaştırması, risk grupları ve elde tutma önerileri.">
<style>
:root{{
  --bg:#0b0e18; --panel:#121729; --panel2:#161d33; --line:#243054;
  --ink:#eef2fb; --muted:#9aa8c4; --dim:#6f7d9b;
  --mor:{MOR}; --cam:{CAM}; --yesil:{YESIL}; --kirmizi:{KIRMIZI}; --sari:{SARI};
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 "Segoe UI",Inter,system-ui,-apple-system,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 20px 72px}}
a{{color:var(--cam)}}

.hero{{background:
    radial-gradient(1200px 420px at 15% -10%, rgba(139,92,246,.30), transparent 60%),
    radial-gradient(900px 400px at 85% 0%, rgba(89,217,255,.18), transparent 60%),
    linear-gradient(180deg,#121729,#0b0e18);
  border-bottom:1px solid var(--line);padding:56px 0 42px;margin-bottom:38px}}
.eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--cam);font-weight:700}}
h1{{font-size:clamp(30px,5.2vw,50px);line-height:1.08;margin:14px 0 16px;letter-spacing:-.5px}}
.hero p{{max-width:760px;color:#c6d1e8;margin:0;font-size:17px}}
.meta{{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}}
.chip{{border:1px solid var(--line);background:#ffffff08;border-radius:99px;
  padding:6px 14px;font-size:13px;color:var(--muted)}}

section{{margin-top:46px;scroll-margin-top:20px}}
h2{{font-size:25px;margin:0 0 6px;letter-spacing:-.3px}}
h2 .num{{color:var(--mor);font-variant-numeric:tabular-nums;margin-right:10px}}
.sub{{color:var(--muted);margin:0 0 20px;max-width:800px}}
h3{{font-size:17px;margin:26px 0 10px}}
p{{margin:0 0 14px}}

.toc{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px;
  background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}}
.toc a{{color:var(--muted);text-decoration:none;font-size:14px;padding:5px 8px;border-radius:8px;display:block}}
.toc a:hover{{color:var(--ink);background:#ffffff0a}}

.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px}}
.kpi .v{{font-size:31px;font-weight:700;letter-spacing:-1px;line-height:1.1}}
.kpi .k{{font-size:13px;color:var(--muted);margin-top:6px}}
.kpi .h{{font-size:12px;color:var(--dim);margin-top:9px;line-height:1.45}}
.kpi.mor .v{{color:var(--mor)}} .kpi.cam .v{{color:var(--cam)}}
.kpi.yesil .v{{color:var(--yesil)}} .kpi.kirmizi .v{{color:var(--kirmizi)}}

.panel{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.cols3{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.fig{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px 22px 14px;margin:16px 0}}
.fig h4{{margin:0 0 14px;font-size:14px;letter-spacing:.4px;text-transform:uppercase;color:var(--muted);font-weight:600}}
.chart{{width:100%;max-width:760px;height:auto;display:block;margin:0 auto}}
.c-lbl{{fill:#d4ddf0;font-size:13px}}
.c-val{{fill:var(--ink);font-size:13px;font-weight:600}}
.c-trk{{fill:#ffffff0f}}
.c-grid{{stroke:#ffffff12;stroke-width:1}}
.c-axis{{stroke:#ffffff28;stroke-width:1}}
.c-diag{{stroke:#ffffff33;stroke-width:1.4;stroke-dasharray:5 5}}
.c-tick{{fill:var(--dim);font-size:11px}}
.c-ax-lbl{{fill:var(--muted);font-size:12px}}
.cap{{font-size:12.5px;color:var(--dim);margin:4px 0 8px}}

table{{width:100%;border-collapse:collapse;background:var(--panel);
  border:1px solid var(--line);border-radius:14px;overflow:hidden}}
th,td{{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);font-size:14.5px;vertical-align:top}}
th{{background:#ffffff07;font-size:11.5px;letter-spacing:.7px;text-transform:uppercase;color:var(--muted);font-weight:600}}
tr:last-child td{{border-bottom:0}}
td.num{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.tbl{{overflow-x:auto;margin:14px 0;border-radius:14px}}
.win td{{background:rgba(139,92,246,.13)}}

.pill{{font-size:11.5px;font-weight:700;border-radius:99px;padding:4px 10px;white-space:nowrap;display:inline-block}}
.p-hi{{background:rgba(255,86,104,.16);color:#ff8b98}}
.p-md{{background:rgba(240,180,41,.16);color:#f4c76a}}
.p-lo{{background:rgba(45,212,167,.14);color:#5fe0bd}}

.note{{border-left:3px solid var(--mor);background:#ffffff07;border-radius:0 12px 12px 0;
  padding:15px 18px;margin:16px 0;color:#d6dff0;font-size:14.5px}}
.note.warn{{border-left-color:var(--sari)}}
.note strong{{color:var(--ink)}}

.cm{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-width:520px}}
.cm-cell{{background:var(--panel2);border:1px solid var(--line);border-radius:10px;
  padding:16px 10px;text-align:center;font-size:23px;font-weight:700;font-variant-numeric:tabular-nums}}
.cm-head{{font-size:12px;font-weight:600;color:var(--muted);background:transparent;border:0;
  display:grid;place-items:center;padding:6px}}
.cm-ok{{color:var(--yesil)}} .cm-no{{color:var(--kirmizi)}}

.steps{{counter-reset:s;display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}
.step{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}
.step:before{{counter-increment:s;content:counter(s);display:grid;place-items:center;
  width:28px;height:28px;border-radius:50%;background:rgba(139,92,246,.18);color:#c3a6ff;
  font-weight:700;font-size:13px;margin-bottom:11px}}
.step h4{{margin:0 0 6px;font-size:15px}}
.step p{{margin:0;font-size:13.5px;color:var(--muted)}}

code{{background:#ffffff0d;border:1px solid var(--line);border-radius:6px;
  padding:1px 6px;font-family:Consolas,"SF Mono",Menlo,monospace;font-size:13px;color:#cbb6ff}}
pre{{background:#0a0d17;border:1px solid var(--line);border-radius:14px;padding:18px;
  overflow-x:auto;font-family:Consolas,"SF Mono",Menlo,monospace;font-size:13px;line-height:1.6;color:#c8d4ec}}
pre .c{{color:#6f7d9b}} pre .s{{color:#7ee0b8}} pre .k{{color:#c3a6ff}}

footer{{margin-top:56px;padding-top:22px;border-top:1px solid var(--line);
  color:var(--dim);font-size:13px}}

@media(max-width:860px){{
  .cols,.cols3{{grid-template-columns:1fr}}
  .hero{{padding:40px 0 32px}}
  th,td{{padding:10px;font-size:13.5px}}
}}
@media print{{
  body{{background:#fff;color:#111}}
  .hero,.panel,.fig,table,.kpi,.step{{background:#fff;border-color:#ccc}}
  .toc{{display:none}}
}}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <div class="eyebrow">Veri Analitiği · Makine Öğrenmesi · Portfolyo Projesi</div>
    <h1>Müşteri Kaybı Tahmini</h1>
    <p>7.043 telekom müşterisinin verisiyle uçtan uca bir churn tahmini: hangi müşterilerin ayrılma riski taşıdığını belirliyor, riski hangi davranışların açıkladığını ölçüyor ve elde tutma çalışmasını sınırlı kapasiteye göre önceliklendiriyorum.</p>
    <div class="meta">
      <span class="chip">IBM Telco Customer Churn · gerçek veri</span>
      <span class="chip">7.043 müşteri · 21 değişken</span>
      <span class="chip">Python · scikit-learn</span>
      <span class="chip">16 Ekim 2026</span>
    </div>
  </div>
</header>

<main class="wrap">

<nav class="toc" aria-label="İçindekiler">
  <a href="#problem">1. İş problemi ve kapsam</a>
  <a href="#veri">2. Veri seti ve kaynak</a>
  <a href="#sozluk">3. Veri sözlüğü ve hedef</a>
  <a href="#temizlik">4. Temizlik ve keşifsel analiz</a>
  <a href="#bolme">5. Eğitim/test ayrımı ve sızıntı</a>
  <a href="#modeller">6. Model karşılaştırması</a>
  <a href="#metrik">7. Metrikler: hangisi neden?</a>
  <a href="#etkenler">8. Başlıca etkenler</a>
  <a href="#gruplar">9. Risk grupları ve öneriler</a>
  <a href="#dashboard">10. KPI ve dashboard</a>
  <a href="#sinir">11. Sınırlamalar</a>
  <a href="#dosyalar">12. Proje dosyaları</a>
</nav>

<section id="ozet">
  <h2>Yönetici özeti</h2>
  <p class="sub">Dört sayı projenin tamamını özetliyor.</p>
  <div class="kpis">
    <div class="kpi mor"><div class="v">0,845</div><div class="k">ROC-AUC (5 katlı CV)</div><div class="h">Lojistik regresyon; ±0,014 standart sapma</div></div>
    <div class="kpi cam"><div class="v">2,85×</div><div class="k">En riskli %10'da isabet</div><div class="h">Rastgele aramaya kıyasla</div></div>
    <div class="kpi kirmizi"><div class="v">%54,0</div><div class="k">Yüksek risk grubu kayıp oranı</div><div class="h">489 müşterinin 264'ü ayrılmış</div></div>
    <div class="kpi yesil"><div class="v">%74,8</div><div class="k">Risk altındaki gelirin kapsanması</div><div class="h">Yüksek risk grubu, kaybedilen aylık gelirin bu kadarını taşıyor</div></div>
  </div>
  <div class="note"><strong>Tek cümlelik sonuç:</strong> Model, müşterilerin yalnızca üçte birini arayarak kaybedilen aylık gelirin dörtte üçüne ulaşmayı mümkün kılıyor. Doğruluk oranı ise bu veride neredeyse hiçbir şey anlatmıyor — nedeni 7. bölümde.</div>
</section>

<section id="problem">
  <h2><span class="num">01</span>İş Problemi ve Kapsam</h2>
  <p class="sub">Abonelik iş modellerinde yeni müşteri kazanmanın maliyeti, mevcut müşteriyi elde tutmanın maliyetinden belirgin biçimde yüksektir. Sorun müşterinin ayrılması değil, ayrıldığını ancak ayrıldıktan sonra öğrenmektir.</p>
  <div class="cols">
    <div class="panel">
      <h3 style="margin-top:0">Çözülen problem</h3>
      <p>Hangi müşterilerin yakın dönemde ayrılma riski taşıdığını, <strong>ayrılmadan önce</strong> belirlemek; böylece elde tutma ekibinin sınırlı kapasitesini doğru müşterilere yöneltmek.</p>
      <p style="margin:0">Çıktı bir olasılık puanı değil, <strong>öncelik sırasına dizilmiş bir arama listesi</strong>.</p>
    </div>
    <div class="panel">
      <h3 style="margin-top:0">Kapsam ve kapsam dışı</h3>
      <p><strong>Kapsam:</strong> müşteri bazında kayıp olasılığı, riski açıklayan etkenler, risk segmentasyonu ve segment bazlı aksiyon önerileri.</p>
      <p style="margin:0"><strong>Kapsam dışı:</strong> müdahalelerin nedensel etkisi. Model kimin ayrılacağını tahmin eder; bir aramanın bunu <em>değiştirdiğini</em> yalnızca kontrol gruplu bir deney gösterebilir.</p>
    </div>
  </div>
  <div class="steps" style="margin-top:16px">
    <div class="step"><h4>Analiz birimi</h4><p>Tekil müşteri (hesap). Her müşteri veri setinde tek satır.</p></div>
    <div class="step"><h4>Hedef</h4><p>Müşterinin aboneliğini sonlandırmış olması (ikili: evet / hayır).</p></div>
    <div class="step"><h4>Karar anı</h4><p>Müşterinin mevcut sözleşme ve kullanım profiliyle puanlanması.</p></div>
    <div class="step"><h4>Başarı ölçüsü</h4><p>Sabit arama kapasitesinde yakalanan kayıp müşteri sayısı.</p></div>
  </div>
</section>

<section id="veri">
  <h2><span class="num">02</span>Veri Seti ve Kaynak</h2>
  <p class="sub">Sentetik veri üretilmedi. Analizin tamamı açık erişimli, gerçek bir veri setinin üzerinde çalışıyor.</p>
  <div class="note"><strong>Veri kaynağı:</strong> IBM <em>Telco Customer Churn</em> (IBM Cognos Analytics örnek veri setleri; Kaggle üzerinde <code>WA_Fn-UseC_-Telco-Customer-Churn.csv</code> adıyla yaygın olarak dağıtılır). Kurgusal bir telekom şirketinin müşteri kayıtlarıdır; churn literatüründe karşılaştırma amacıyla standart hâle gelmiştir. <strong>Raporda yer alan bütün sayılar bu dosyadan hesaplanmıştır</strong> — hiçbir sonuç, oran veya metrik tahmin ya da temsilî değildir.</div>
  <div class="kpis">
    <div class="kpi"><div class="v">7.043</div><div class="k">Müşteri kaydı</div><div class="h">Yinelenen müşteri numarası yok</div></div>
    <div class="kpi"><div class="v">21</div><div class="k">Değişken</div><div class="h">4 sayısal, 16 kategorik, 1 hedef</div></div>
    <div class="kpi"><div class="v">%26,5</div><div class="k">Kayıp oranı</div><div class="h">1.869 ayrılmış, 5.174 kalmış</div></div>
    <div class="kpi"><div class="v">11</div><div class="k">Eksik hücre</div><div class="h">Yalnızca TotalCharges sütununda</div></div>
  </div>
</section>

<section id="sozluk">
  <h2><span class="num">03</span>Veri Sözlüğü ve Hedef Değişken</h2>
  <p class="sub">Değişkenler üç gruba ayrılıyor: müşteri profili, aldığı hizmetler ve sözleşme–ödeme bilgileri.</p>
  <div class="tbl"><table>
    <thead><tr><th>Değişken</th><th>Tür</th><th>Anlamı</th></tr></thead>
    <tbody>
      <tr><td><code>customerID</code></td><td>Kimlik</td><td>Müşteri anahtarı. Modelden çıkarıldı — tahmin gücü yok, ezberlemeye yol açar.</td></tr>
      <tr><td><code>gender</code>, <code>SeniorCitizen</code>, <code>Partner</code>, <code>Dependents</code></td><td>Kategorik</td><td>Demografik profil: cinsiyet, 65 yaş üstü olma, partner ve bakmakla yükümlü olunan kişi durumu.</td></tr>
      <tr><td><code>tenure</code></td><td>Sayısal</td><td>Müşterinin kaç aydır abone olduğu (0–72).</td></tr>
      <tr><td><code>PhoneService</code>, <code>MultipleLines</code></td><td>Kategorik</td><td>Telefon hizmeti ve birden fazla hat.</td></tr>
      <tr><td><code>InternetService</code></td><td>Kategorik</td><td>DSL / Fiber optik / yok.</td></tr>
      <tr><td><code>OnlineSecurity</code>, <code>OnlineBackup</code>, <code>DeviceProtection</code>, <code>TechSupport</code></td><td>Kategorik</td><td>İnternete bağlı ek hizmetler.</td></tr>
      <tr><td><code>StreamingTV</code>, <code>StreamingMovies</code></td><td>Kategorik</td><td>İçerik hizmetleri.</td></tr>
      <tr><td><code>Contract</code></td><td>Kategorik</td><td>Aydan aya / 1 yıllık / 2 yıllık.</td></tr>
      <tr><td><code>PaperlessBilling</code>, <code>PaymentMethod</code></td><td>Kategorik</td><td>Kağıtsız fatura ve ödeme yöntemi.</td></tr>
      <tr><td><code>MonthlyCharges</code>, <code>TotalCharges</code></td><td>Sayısal</td><td>Aylık ücret ve bugüne kadarki toplam ödeme.</td></tr>
      <tr class="win"><td><code>Churn</code></td><td><strong>Hedef</strong></td><td><strong>Müşteri ayrıldı mı?</strong> Evet = 1 (1.869 müşteri), Hayır = 0 (5.174 müşteri).</td></tr>
    </tbody>
  </table></div>
</section>

<section id="temizlik">
  <h2><span class="num">04</span>Temizlik ve Keşifsel Analiz</h2>
  <p class="sub">Model kurmadan önce veri dört kırılımda incelendi. Modelin sonradan bulduğu yapının büyük kısmı bu aşamada zaten görünüyor.</p>

  <h3>Temizlik kararları</h3>
  <div class="tbl"><table>
    <thead><tr><th>Bulgu</th><th>Karar</th><th>Gerekçe</th></tr></thead>
    <tbody>
      <tr><td><code>TotalCharges</code> metin olarak okunuyor; 11 hücre boşluk karakteri</td><td>Sayısala çevrildi, boşluklar <code>NA</code> yapıldı</td><td>Doğrudan okunduğunda sütunun tamamı kategorik sanılıyor</td></tr>
      <tr class="win"><td>Eksik 11 kaydın <strong>tamamında</strong> <code>tenure = 0</code></td><td>Yapısal eksiklik olarak işaretlendi; medyanla doldurulmadı</td><td>Bunlar henüz faturalandırılmamış yeni abonelikler — değer eksik değil, <strong>henüz yok</strong></td></tr>
      <tr><td>Yinelenen <code>customerID</code></td><td>Kontrol edildi: yok</td><td>Aynı müşterinin iki kez sayılması metrikleri bozardı</td></tr>
      <tr><td><code>customerID</code> tahmin değişkeni değil</td><td>Modelden çıkarıldı</td><td>Kimlik alanları ezberleme ve sahte performans üretir</td></tr>
    </tbody>
  </table></div>
  <div class="note warn"><strong>Eksik veriyi doldurmadan önce desenine bakın.</strong> Rastgele eksiklik ile yapısal eksiklik farklı problemlerdir. Burada eksiklik tek bir değişkenle tamamen açıklanıyor; medyan yazmak bu müşterilere var olmayan bir geçmiş atfederdi.</div>

  <h3>Kayıp nerede yoğunlaşıyor?</h3>
  <div class="fig"><h4>Sözleşme türüne göre kayıp oranı</h4>{g_sozlesme}<p class="cap">Aydan aya sözleşmeli müşterilerin kayıp oranı, iki yıllık sözleşmelilerin 15 katı.</p></div>
  <div class="fig"><h4>Müşteri kıdemine göre kayıp oranı</h4>{g_kidem}<p class="cap">İlk altı ayda yeni müşterilerin yarısından fazlası ayrılıyor; risk kıdemle birlikte tek yönlü düşüyor.</p></div>
  <div class="cols">
    <div class="fig" style="margin:0"><h4>Ödeme yöntemine göre</h4>{g_odeme}<p class="cap">Elektronik çekle ödeyenler, otomatik ödeme yapanların üç katı oranında ayrılıyor.</p></div>
    <div class="fig" style="margin:0"><h4>İnternet hizmetine göre</h4>{g_internet}<p class="cap">Fiber optik abonelerde kayıp oranı DSL'in iki katından fazla.</p></div>
  </div>
  <p>Dört kırılım da aynı profili işaret ediyor: <strong>bağlılığı zayıf, aylık ödemeli, ek hizmet ve destek almayan, kıdemi düşük müşteri.</strong> Ödeme yönteminin bu kadar ayırt edici olması dikkat çekici — otomatik ödeme talimatı vermek, ilişkiyi sürdürme niyetinin bir göstergesi gibi davranıyor.</p>
</section>

<section id="bolme">
  <h2><span class="num">05</span>Eğitim/Test Ayrımı ve Veri Sızıntısı</h2>
  <p class="sub">Performansın gerçekçi olması, modelin hiç görmediği veriyle ölçülmesine bağlı. Bu aşamada alınan dört önlem var.</p>
  <div class="steps">
    <div class="step"><h4>Tabakalı bölme</h4><p>%80 eğitim (5.634) / %20 test (1.409). Kayıp oranı iki sette de %26,5.</p></div>
    <div class="step"><h4>Dönüşümler hat içinde</h4><p>Ölçekleme, doldurma ve kodlama <code>Pipeline</code> içinde; parametreler yalnızca eğitimden öğreniliyor.</p></div>
    <div class="step"><h4>Kimlik alanı dışarıda</h4><p><code>customerID</code> modele girmiyor.</p></div>
    <div class="step"><h4>Sabit tohum</h4><p><code>random_state=42</code>; sonuçlar tekrar üretilebilir.</p></div>
  </div>
  <div class="note"><strong>Sızıntının en sinsi biçimi:</strong> ölçekleme ortalamasını veya doldurma medyanını <em>tüm veri</em> üzerinden hesaplamaktır. Test setinin bilgisi böylece modele sızar ve rapor edilen performans gerçekte ulaşılamayacak kadar iyi çıkar. <code>Pipeline</code> kullanmak bunu yapısal olarak engeller: her katlamada parametreler yeniden ve yalnızca eğitim verisinden öğrenilir.</div>
<pre><span class="c"># Butun on isleme adimlari hat icinde: sizinti yapisal olarak engellenir</span>
onisle = ColumnTransformer([
    (<span class="s">"num"</span>, Pipeline([(<span class="s">"i"</span>, SimpleImputer(strategy=<span class="s">"median"</span>)),
                      (<span class="s">"s"</span>, StandardScaler())]), sayisal),
    (<span class="s">"cat"</span>, Pipeline([(<span class="s">"i"</span>, SimpleImputer(strategy=<span class="s">"most_frequent"</span>)),
                      (<span class="s">"o"</span>, OneHotEncoder(handle_unknown=<span class="s">"ignore"</span>))]), kategorik),
])

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=<span class="k">0.2</span>, random_state=<span class="k">42</span>, stratify=y)

model = Pipeline([(<span class="s">"prep"</span>, onisle), (<span class="s">"model"</span>, LogisticRegression(
    max_iter=<span class="k">2000</span>, class_weight=<span class="s">"balanced"</span>))]).fit(X_tr, y_tr)</pre>
</section>

<section id="modeller">
  <h2><span class="num">06</span>Model Karşılaştırması</h2>
  <p class="sub">Bir başlangıç modeli (lojistik regresyon) ve iki topluluk yöntemi aynı veri hattından, aynı test setinde karşılaştırıldı. Sınıf dengesizliği için üçünde de <code>class_weight="balanced"</code> kullanıldı.</p>
  <div class="tbl"><table>
    <thead><tr><th>Model</th><th>Doğruluk</th><th>Kesinlik</th><th>Duyarlılık</th><th>F1</th><th>ROC-AUC</th><th>PR-AUC</th><th>5 katlı CV (ROC-AUC)</th></tr></thead>
    <tbody>
      <tr class="win"><td><strong>Lojistik regresyon</strong></td><td class="num">0,738</td><td class="num">0,504</td><td class="num"><strong>0,783</strong></td><td class="num">0,614</td><td class="num"><strong>0,841</strong></td><td class="num">0,633</td><td class="num"><strong>0,845 ± 0,014</strong></td></tr>
      <tr><td>Rastgele orman</td><td class="num"><strong>0,759</strong></td><td class="num">0,534</td><td class="num">0,743</td><td class="num"><strong>0,621</strong></td><td class="num">0,837</td><td class="num"><strong>0,641</strong></td><td class="num">0,841 ± 0,013</td></tr>
      <tr><td>Extra Trees</td><td class="num">0,757</td><td class="num">0,532</td><td class="num">0,709</td><td class="num">0,608</td><td class="num">0,826</td><td class="num">0,626</td><td class="num">0,830 ± 0,013</td></tr>
      <tr><td><em>Taban oran (hiç kimse ayrılmaz)</em></td><td class="num">0,735</td><td class="num">—</td><td class="num">0,000</td><td class="num">—</td><td class="num">0,500</td><td class="num">0,265</td><td class="num">—</td></tr>
    </tbody>
  </table></div>
  <p>Üç modelin çapraz doğrulanmış ROC-AUC'leri 0,830 ile 0,845 arasında; aradaki fark standart sapmaların mertebesinde. <strong>Model seçimi bu problemin zor kısmı değil.</strong> Yorumlanabilir olduğu ve en yüksek duyarlılığı verdiği için lojistik regresyon üretim adayı olarak seçildi.</p>
  <div class="cols">
    <div class="fig" style="margin:0"><h4>ROC eğrisi — lojistik regresyon</h4>{g_roc}<p class="cap">Eğrinin altındaki alan 0,841. Kesikli çizgi rastgele tahmini gösterir.</p></div>
    <div class="fig" style="margin:0"><h4>Karışıklık matrisi (eşik 0,50)</h4>{g_matris}<p class="cap">1.409 test müşterisi. Model 581 müşteriyi işaretliyor; 293'ü gerçekten ayrılıyor, 81 kayıp müşteri gözden kaçıyor.</p></div>
  </div>
</section>

<section id="metrik">
  <h2><span class="num">07</span>Metrikler: Churn'de Hangisi Neden Önemli?</h2>
  <p class="sub">Bu bölüm raporun en kritik kısmı. Yanlış metrik seçmek, işe yarayan bir modeli çöpe attırabilir.</p>
  <div class="note warn"><strong>Doğruluk bu problemde kullanılamaz.</strong> Müşterilerin %73,5'i kalıyor. "Hiç kimse ayrılmaz" diyen, hiçbir şey öğrenmemiş bir model %73,5 doğruluk alır. Lojistik regresyonun %73,8'i bunun yalnızca <strong>0,3 puan</strong> üzerinde. Doğruluğa bakan biri modeli işe yaramaz sanır; oysa aynı model kayıp müşterilerin %78,3'ünü yakalıyor.</div>
  <div class="tbl"><table>
    <thead><tr><th>Metrik</th><th>Ne ölçer?</th><th>Churn'de rolü</th></tr></thead>
    <tbody>
      <tr><td><strong>Doğruluk</strong></td><td>Toplam doğru tahmin oranı</td><td><span class="pill p-hi">Yanıltıcı</span> Dengesiz sınıfta taban oranı aşmak kolay; tek başına raporlanmamalı.</td></tr>
      <tr class="win"><td><strong>Duyarlılık (recall)</strong></td><td>Gerçek kayıpların kaçını yakaladık</td><td><span class="pill p-lo">Birincil</span> Kaçırılan her müşteri geri kazanma şansı olmadan giden gelirdir.</td></tr>
      <tr><td><strong>Kesinlik (precision)</strong></td><td>İşaretlediklerimizin kaçı gerçekten ayrılıyor</td><td><span class="pill p-md">Maliyet tarafı</span> Düşük kesinlik, elde tutma bütçesinin boşa gitmesi demektir.</td></tr>
      <tr><td><strong>F1</strong></td><td>İkisinin harmonik ortalaması</td><td><span class="pill p-md">Dengeleyici</span> Maliyetler simetrikse işe yarar; churn'de genelde değildir.</td></tr>
      <tr><td><strong>ROC-AUC</strong></td><td>Sıralama kalitesi, eşikten bağımsız</td><td><span class="pill p-lo">Model seçimi</span> Modelleri kıyaslamak için en uygun tek sayı.</td></tr>
      <tr><td><strong>PR-AUC</strong></td><td>Azınlık sınıfında kesinlik–duyarlılık dengesi</td><td><span class="pill p-lo">Dengesizlikte</span> Taban oran %26,5; PR-AUC 0,633 bunun 2,4 katı.</td></tr>
      <tr class="win"><td><strong>İlk %N yakalama / lift</strong></td><td>Sabit kapasiteyle ulaşılan kayıp oranı</td><td><span class="pill p-lo">İş metriği</span> Ekip kapasitesiyle doğrudan eşleşen tek ölçü.</td></tr>
    </tbody>
  </table></div>

  <h3>Eşik bir varsayımdır</h3>
  <p>Yukarıdaki metriklerin tamamı "olasılık 0,5'i geçerse ayrılacak" kararından doğuyor. Bu eşik matematikten değil alışkanlıktan geliyor ve kapasiteye göre değiştirilmelidir.</p>
  <div class="tbl"><table>
    <thead><tr><th>Eşik</th><th>Doğruluk</th><th>Duyarlılık</th><th>Kesinlik</th><th>İşaretlenen müşteri</th><th>Ne zaman tercih edilir?</th></tr></thead>
    <tbody>
      <tr><td class="num">0,30</td><td class="num">0,653</td><td class="num"><strong>0,928</strong></td><td class="num">0,429</td><td class="num">809</td><td>Kapasite bol, kaçırmanın maliyeti yüksek</td></tr>
      <tr><td class="num">0,40</td><td class="num">0,701</td><td class="num">0,866</td><td class="num">0,466</td><td class="num">695</td><td>Dengeli, geniş kampanya</td></tr>
      <tr class="win"><td class="num"><strong>0,50</strong></td><td class="num">0,738</td><td class="num">0,783</td><td class="num">0,504</td><td class="num">581</td><td>Varsayılan; en yüksek F1</td></tr>
      <tr><td class="num">0,60</td><td class="num">0,762</td><td class="num">0,706</td><td class="num">0,540</td><td class="num">489</td><td>Kapasite sınırlı</td></tr>
      <tr><td class="num">0,70</td><td class="num"><strong>0,789</strong></td><td class="num">0,602</td><td class="num">0,603</td><td class="num">373</td><td>Temas maliyeti yüksek, isabet önemli</td></tr>
    </tbody>
  </table></div>
  <div class="note warn"><strong>Eşik test setinde seçilmemelidir.</strong> Yukarıdaki tablo bir gösterimdir. Üretimde eşik, eğitim verisinden ayrılan bir doğrulama kümesinde ya da çapraz doğrulamayla belirlenmelidir; eşik de diğerleri gibi bir hiperparametredir.</div>
</section>

<section id="etkenler">
  <h2><span class="num">08</span>Kayıpla İlişkili Başlıca Etkenler</h2>
  <p class="sub">İki bağımsız yöntem — permütasyon önemi ve lojistik regresyon katsayıları — aynı sıralamayı veriyor.</p>
  <div class="fig"><h4>Permütasyon önemi (ROC-AUC düşüşü, test setinde)</h4>{cubuk(
      ["tenure (kıdem)", "InternetService", "Contract", "MonthlyCharges", "TotalCharges",
       "StreamingMovies", "OnlineSecurity", "TechSupport"],
      [0.1515, 0.0431, 0.0402, 0.0376, 0.0104, 0.0046, 0.0044, 0.0039],
      [MOR, CAM, CAM, CAM, YESIL, YESIL, YESIL, YESIL], birim="")}
    <p class="cap">Değişken karıştırıldığında modelin ROC-AUC'si ne kadar düşüyor. Kıdem tek başına diğerlerinin toplamından fazla.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Değişken</th><th>Katsayı</th><th>Odds oranı</th><th>Yorum</th></tr></thead>
    <tbody>
      <tr><td>Fiber optik internet</td><td class="num">+0,705</td><td class="num"><strong>2,02</strong></td><td>Kayıp bahis oranını iki katına çıkarıyor. Fiyat/beklenti uyumsuzluğuna işaret ediyor olabilir.</td></tr>
      <tr><td>Aydan aya sözleşme</td><td class="num">+0,663</td><td class="num"><strong>1,94</strong></td><td>Bağlayıcılığın olmaması riski neredeyse iki katına çıkarıyor.</td></tr>
      <tr><td>Elektronik çek</td><td class="num">+0,239</td><td class="num">1,27</td><td>Otomatik ödemeye kıyasla belirgin biçimde riskli.</td></tr>
      <tr><td>Teknik destek yok</td><td class="num">+0,164</td><td class="num">1,18</td><td>Destek paketi almamak riski artırıyor.</td></tr>
      <tr class="win"><td>Kıdem (standartlaştırılmış)</td><td class="num">−1,124</td><td class="num"><strong>0,33</strong></td><td>En güçlü koruyucu etki: bir standart sapma kıdem, bahis oranını üçte bire indiriyor.</td></tr>
      <tr><td>2 yıllık sözleşme</td><td class="num">−0,781</td><td class="num">0,46</td><td>Uzun sözleşme riski yarıdan fazla azaltıyor.</td></tr>
    </tbody>
  </table></div>
  <div class="note"><strong>Görünürdeki çelişki:</strong> <code>MonthlyCharges</code> katsayısı negatif (odds oranı 0,52) — oysa tek başına bakıldığında pahalı paketlerde kayıp daha yüksek. Bu bir hata değil, koşullu etki: model zaten "fiber optik" bilgisine sahip ve pahalı olmanın riskini oradan okuyor. Fiber olduğu bilindikten <em>sonra</em>, yüksek aylık ücret daha kapsamlı ve daha bağlı bir aboneliğe işaret ediyor. Çok değişkenli modellerde katsayılar "diğerleri sabitken" okunur.</div>
  <div class="note warn"><strong>Bunlar ilişkidir, neden değildir.</strong> Fiber optik aboneliği kaybı "yapmıyor"; kaybeden müşterilerle birlikte anılıyor. Nedensel bir iddia için kontrollü deney gerekir.</div>
</section>

<section id="gruplar">
  <h2><span class="num">09</span>Risk Grupları ve Elde Tutma Önerileri</h2>
  <p class="sub">Model çıktısı olasılık eşiklerine göre üç gruba ayrıldı. Tablodaki kayıp oranları <strong>gerçekleşen</strong> değerlerdir — test setindeki 1.409 müşterinin gerçek sonuçlarından hesaplanmıştır.</p>
  <div class="tbl"><table>
    <thead><tr><th>Grup</th><th>Olasılık</th><th>Müşteri</th><th>Gerçekleşen kayıp</th><th>Ort. aylık ücret</th><th>Ort. kıdem</th><th>Risk altındaki aylık gelir</th></tr></thead>
    <tbody>
      <tr class="win"><td><span class="pill p-hi">Yüksek</span></td><td class="num">&gt; 0,60</td><td class="num">{int(grp("Yüksek","musteri"))}</td><td class="num"><strong>{int(grp("Yüksek","gercek_kayip"))} (%{grp("Yüksek","kayip_orani")*100:.1f})</strong></td><td class="num">{grp("Yüksek","ort_aylik"):.2f} $</td><td class="num">{grp("Yüksek","ort_kidem"):.0f} ay</td><td class="num"><strong>{tl(grp("Yüksek","risk_altinda_gelir"))} $</strong></td></tr>
      <tr><td><span class="pill p-md">Orta</span></td><td class="num">0,30 – 0,60</td><td class="num">{int(grp("Orta","musteri"))}</td><td class="num">{int(grp("Orta","gercek_kayip"))} (%{grp("Orta","kayip_orani")*100:.1f})</td><td class="num">{grp("Orta","ort_aylik"):.2f} $</td><td class="num">{grp("Orta","ort_kidem"):.0f} ay</td><td class="num">{tl(grp("Orta","risk_altinda_gelir"))} $</td></tr>
      <tr><td><span class="pill p-lo">Düşük</span></td><td class="num">&lt; 0,30</td><td class="num">{int(grp("Düşük","musteri"))}</td><td class="num">{int(grp("Düşük","gercek_kayip"))} (%{grp("Düşük","kayip_orani")*100:.1f})</td><td class="num">{grp("Düşük","ort_aylik"):.2f} $</td><td class="num">{grp("Düşük","ort_kidem"):.0f} ay</td><td class="num">{tl(grp("Düşük","risk_altinda_gelir"))} $</td></tr>
    </tbody>
  </table></div>
  <div class="note"><strong>Gruplama neden işe yarıyor:</strong> Yüksek risk grubu müşterilerin %{100*grp("Yüksek","musteri")/1409:.0f}'ini kapsıyor ama kaybedilen aylık gelirin <strong>%{100*grp("Yüksek","risk_altinda_gelir")/27214.9:.1f}'ini</strong> taşıyor. Üstelik bu grubun ortalama aylık ücreti ({grp("Yüksek","ort_aylik"):.0f} $) düşük risk grubundan ({grp("Düşük","ort_aylik"):.0f} $) belirgin biçimde yüksek — yani kaybedilen müşteriler aynı zamanda daha değerli müşteriler.</div>

  <div class="cols3">
    <div class="panel"><span class="pill p-hi">Yüksek risk</span>
      <h3>Kişisel temas</h3>
      <p>Profil: ortalama {grp("Yüksek","ort_kidem"):.0f} aylık kıdem, aydan aya sözleşme, fiber optik, destek paketi yok.</p>
      <p><strong>Öneri:</strong> Elde tutma ekibi tarafından aranma; sözleşme yükseltme teklifi (1–2 yıllık), ücretsiz teknik destek paketi, fatura/hız şikâyetinin çözülmesi.</p>
      <p style="margin:0"><strong>Ölçüm:</strong> kontrol grubuna kıyasla 90 günlük elde tutma farkı.</p></div>
    <div class="panel"><span class="pill p-md">Orta risk</span>
      <h3>Otomatik ve düşük maliyetli</h3>
      <p>Profil: risk yükseliyor ama henüz kritik değil; kıdem ortalama {grp("Orta","ort_kidem"):.0f} ay.</p>
      <p><strong>Öneri:</strong> Otomatik ödeme talimatına geçiş teşviki, kullanılmayan özelliklere yönelik kısa rehberler, yenileme öncesi hatırlatma.</p>
      <p style="margin:0"><strong>Ölçüm:</strong> otomatik ödemeye geçiş oranı ve risk puanındaki değişim.</p></div>
    <div class="panel"><span class="pill p-lo">Düşük risk</span>
      <h3>Rahat bırak</h3>
      <p>Profil: ortalama {grp("Düşük","ort_kidem"):.0f} aylık kıdem, gerçekleşen kayıp yalnızca %{grp("Düşük","kayip_orani")*100:.1f}.</p>
      <p><strong>Öneri:</strong> Olağan iletişim. Aşırı kampanya temasından kaçınılmalı; bu grup zaten kalıyor ve gereksiz temas ters etki yapabilir.</p>
      <p style="margin:0"><strong>Ölçüm:</strong> şikâyet sayısı ve uzun vadeli kayıp oranı.</p></div>
  </div>

  <h3>Puandan arama listesine</h3>
  <div class="fig"><h4>Kümülatif kazanım eğrisi</h4>{g_kazanim}<p class="cap">Müşteriler risk puanına göre sıralandığında, ilk %N'i aradığınızda kayıp müşterilerin yüzde kaçına ulaşırsınız. Kesikli çizgi rastgele arama.</p></div>
  <div class="tbl"><table>
    <thead><tr><th>Aranan dilim</th><th>Müşteri</th><th>Dilimdeki kayıp oranı</th><th>Yakalanan kayıp</th><th>Lift</th></tr></thead>
    <tbody>
      <tr class="win"><td><strong>İlk %10</strong></td><td class="num">140</td><td class="num"><strong>%75,7</strong></td><td class="num">106 / 374 (%28,3)</td><td class="num"><strong>2,85×</strong></td></tr>
      <tr><td>İlk %20</td><td class="num">281</td><td class="num">%65,8</td><td class="num">185 / 374 (%49,5)</td><td class="num">2,48×</td></tr>
      <tr><td>İlk %30</td><td class="num">422</td><td class="num">%57,6</td><td class="num">243 / 374 (%65,0)</td><td class="num">2,17×</td></tr>
      <tr><td>İlk %50</td><td class="num">704</td><td class="num">%46,3</td><td class="num">326 / 374 (%87,2)</td><td class="num">1,74×</td></tr>
    </tbody>
  </table></div>
  <div class="note warn"><strong>Aksiyonları kontrol grubuyla sınayın.</strong> Model, ayrılmaya en yakın müşterileri seçiyor; bu müşterilere yapılan müdahalenin işe yaradığını <em>varsaymak</em> churn projelerinin en yaygın hatasıdır. İşaretlenen müşterilerin rastgele seçilmiş bir bölümüne dokunmayıp iki grubu karşılaştırmak, artımlı etkiyi görmenin tek yoludur.</div>
</section>

<section id="dashboard">
  <h2><span class="num">10</span>KPI'lar ve Dashboard Bölümleri</h2>
  <p class="sub">Modelin operasyona bağlanması için izlenmesi önerilen dört panel.</p>
  <div class="kpis">
    <div class="kpi mor"><div class="v">0,845</div><div class="k">ROC-AUC (CV)</div><div class="h">Model kalitesi · haftalık</div></div>
    <div class="kpi cam"><div class="v">%28,3</div><div class="k">İlk %10'da yakalanan kayıp</div><div class="h">İş etkisi · haftalık</div></div>
    <div class="kpi kirmizi"><div class="v">{tl(grp("Yüksek","risk_altinda_gelir"))} $</div><div class="k">Risk altındaki aylık gelir</div><div class="h">Yüksek risk grubu · aylık</div></div>
    <div class="kpi yesil"><div class="v">{int(grp("Yüksek","musteri"))}</div><div class="k">Temas edilecek müşteri</div><div class="h">Kapasite planı · haftalık</div></div>
  </div>
  <div class="tbl"><table>
    <thead><tr><th>Panel</th><th>Gösterilecek</th><th>Kime</th><th>Sıklık</th></tr></thead>
    <tbody>
      <tr><td><strong>Model sağlığı</strong></td><td>ROC-AUC, PR-AUC, kalibrasyon sapması, girdi dağılımı kayması</td><td>Veri ekibi</td><td>Haftalık</td></tr>
      <tr><td><strong>Risk dağılımı</strong></td><td>Üç grubun müşteri sayısı, gelir payı ve haftalık değişimi</td><td>Elde tutma yönetimi</td><td>Haftalık</td></tr>
      <tr><td><strong>Operasyon</strong></td><td>Temas edilen müşteri, yanıt oranı, ortalama yanıt süresi, kapasite kullanımı</td><td>Çağrı merkezi</td><td>Günlük</td></tr>
      <tr><td><strong>İş sonucu</strong></td><td>Kontrol grubuna kıyasla elde tutma farkı, korunan aylık gelir, temas başına maliyet</td><td>Yönetim</td><td>Aylık</td></tr>
    </tbody>
  </table></div>
</section>

<section id="sinir">
  <h2><span class="num">11</span>Sınırlamalar</h2>
  <p class="sub">Raporun sonuçları aşağıdaki sınırlar içinde geçerlidir.</p>
  <div class="tbl"><table>
    <thead><tr><th>Sınırlama</th><th>Etkisi</th></tr></thead>
    <tbody>
      <tr><td><strong>Veri kesitseldir</strong></td><td>Her müşteri için tek bir anlık görüntü var; zaman içindeki davranış değişimi (kullanımdaki düşüş, artan şikâyet) modellenemiyor. Gerçek bir sistemde zaman serisi özellikleri performansı belirgin biçimde artırır.</td></tr>
      <tr><td><strong>Kayıp tanımı verili</strong></td><td>Hangi süre sonunda "ayrılmış" sayıldığı veri setinde tanımlanmış; tahmin ufku seçilebilir değil. Üretimde ufuk (ör. 30 gün) iş kararına göre belirlenmelidir.</td></tr>
      <tr><td><strong>Kurgusal şirket verisi</strong></td><td>IBM'in örnek veri seti gerçek bir operasyondan değil; bulgular yöntem gösterimi olarak güçlü, sektörel genelleme olarak sınırlıdır.</td></tr>
      <tr><td><strong>Nedensellik yok</strong></td><td>Bütün bulgular ilişkiseldir. "Fiber optiği ucuzlatırsak kayıp azalır" gibi bir çıkarım bu veriyle desteklenemez.</td></tr>
      <tr><td><strong>Maliyet verisi yok</strong></td><td>Temas başına maliyet ve müşteri yaşam boyu değeri bilinmediği için eşik, beklenen kâra göre optimize edilemedi; kapasite varsayımıyla ilerlendi.</td></tr>
      <tr><td><strong>Adalet denetimi yapılmadı</strong></td><td>Model çıktılarının demografik segmentler arasında dengeli davranıp davranmadığı ayrıca incelenmelidir.</td></tr>
    </tbody>
  </table></div>
</section>

<section id="dosyalar">
  <h2><span class="num">12</span>Proje Dosyaları ve Çalıştırma</h2>
  <p class="sub">Rapor tek başına açılır; hiçbir dış bağlantıya, internet erişimine veya JavaScript kütüphanesine ihtiyaç duymaz. Bütün grafikler HTML içine gömülü SVG'dir.</p>
  <div class="tbl"><table>
    <thead><tr><th>Dosya</th><th>İçerik</th></tr></thead>
    <tbody>
      <tr class="win"><td><code>rapor.html</code></td><td><strong>Ana teslimat.</strong> Çift tıklayın; herhangi bir tarayıcıda açılır. Yazdırma düzeni de hazırdır (Ctrl+P → PDF).</td></tr>
      <tr><td><code>analiz.py</code></td><td>Keşifsel analiz, üç model karşılaştırması, eşik taraması, permütasyon önemi ve katsayılar.</td></tr>
      <tr><td><code>rapor_verisi.py</code></td><td>Çapraz doğrulama, risk grupları, gelir etkisi, ROC ve kazanım eğrisi verileri.</td></tr>
      <tr><td><code>rapor_verisi.json</code></td><td>Yukarıdaki betiğin ürettiği sayılar; rapor bu dosyadan beslenir.</td></tr>
      <tr><td><code>rapor_uret.py</code></td><td>JSON'u okuyup <code>rapor.html</code>'i üreten betik.</td></tr>
      <tr><td><code>sonuclar.txt</code></td><td>Betiklerin ham konsol çıktısı — rapordaki her sayı buradan doğrulanabilir.</td></tr>
      <tr><td><code>WA_Fn-UseC_-Telco-Customer-Churn.csv</code></td><td>Kaynak veri (7.043 satır). Raporla aynı klasörde değilse betiklerdeki yol güncellenmelidir.</td></tr>
    </tbody>
  </table></div>
  <h3>Yeniden üretmek için</h3>
<pre><span class="c"># Gereksinimler</span>
pip install pandas scikit-learn

<span class="c"># Analizi calistir</span>
python analiz.py          <span class="c"># konsola tum sayilari yazar</span>
python rapor_verisi.py    <span class="c"># rapor_verisi.json uretir</span>
python rapor_uret.py      <span class="c"># rapor.html uretir</span></pre>
  <p>Bütün betiklerde <code>random_state=42</code> sabitlenmiştir; aynı veriyle aynı sayılar üretilir.</p>
</section>

<footer>
  <p style="margin:0 0 6px"><strong>Özgür Nurettin Öztürk</strong> · Veri Analisti · 16 Ekim 2026</p>
  <p style="margin:0">Veri kaynağı: IBM Telco Customer Churn. Raporda yer alan bütün sayılar bu veri setinden hesaplanmıştır; sentetik veri kullanılmamış, hiçbir sonuç temsilî olarak üretilmemiştir. Bulgular ilişkiseldir, nedensel değildir.</p>
</footer>

</main>
</body>
</html>
"""

yol = os.path.join(HEDEF, "rapor.html")
io.open(yol, "w", encoding="utf-8", newline="\n").write(HTML)
print("yazildi:", yol, os.path.getsize(yol), "bayt")
