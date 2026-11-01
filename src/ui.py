"""
Komponen tampilan dashboard (HTML/CSS kecil untuk elemen yang tidak tersedia
sebagai komponen bawaan Streamlit: header, banner, kartu berikon, daftar batang).
"""

import base64
import datetime
import html

import altair as alt
import streamlit as st

BLUE = "#1E4FD8"

CSS = """
<style>
/* ---------- area konten ---------- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #E6EEFF 0%, #F1ECFF 45%, #FFF2E8 100%) fixed;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 4.2rem; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    border-radius: 10px; padding: 0.15rem 0.6rem; margin: 1px 0;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background: rgba(255,255,255,0.14); }
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: #FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] * { color: #1E4FD8 !important; font-weight: 700; }
.sb-brand { display:flex; align-items:center; gap:12px; padding: 4px 4px 14px 4px;
            border-bottom: 1px solid rgba(255,255,255,0.18); margin-bottom: 6px; }
.sb-logo { width:42px; height:42px; border-radius:12px; background:#FFFFFF; display:flex;
           align-items:center; justify-content:center; flex-shrink:0; }
.sb-title { color:#FFFFFF; font-weight:700; font-size:1.02rem; line-height:1.2; }
.sb-sub { color:rgba(255,255,255,0.75); font-size:0.78rem; }
.sb-section { color:rgba(255,255,255,0.7); font-size:0.7rem; font-weight:700; letter-spacing:0.08em;
              text-transform:uppercase; margin: 14px 0 2px 8px; }
.sb-foot { color:rgba(255,255,255,0.7); font-size:0.75rem; border-top: 1px solid rgba(255,255,255,0.18);
           padding-top: 12px; margin-top: 10px; line-height:1.6; }

/* ---------- header ---------- */
.tb-header { display:flex; justify-content:space-between; align-items:center; gap:16px;
             background:#FFFFFF; border:1px solid #E4EAF5; border-radius:16px; padding:14px 22px;
             margin-bottom: 4px; box-shadow: 0 1px 2px rgba(16,40,90,0.04); }
.tb-title { font-size:1.35rem; font-weight:700; color:#16213E; line-height:1.25; }
.tb-sub { color:#6B7590; font-size:0.86rem; }
.tb-chip { display:flex; align-items:center; gap:10px; border:1px solid #E4EAF5; border-radius:999px;
           padding:6px 16px 6px 6px; background:#FFFFFF; white-space:nowrap; }
.tb-avatar { width:34px; height:34px; border-radius:50%; background:#1E4FD8; color:#FFFFFF; font-weight:700;
             display:flex; align-items:center; justify-content:center; }
.tb-chip-name { font-weight:700; font-size:0.86rem; color:#16213E; line-height:1.2; }
.tb-chip-date { font-size:0.74rem; color:#6B7590; }

/* ---------- banner ---------- */
.tb-banner { background: linear-gradient(120deg, #1E4FD8 0%, #2F6BEA 60%, #3B82F6 100%);
             border-radius:18px; padding:26px 28px; color:#FFFFFF;
             box-shadow: 0 8px 24px rgba(30,79,216,0.22); }
.tb-banner-date { font-size:0.75rem; font-weight:700; letter-spacing:0.08em; opacity:0.85; text-transform:uppercase; }
.tb-banner-title { font-size:1.45rem; font-weight:700; margin:8px 0 6px 0; }
.tb-banner-sub { font-size:0.9rem; opacity:0.9; }

/* ---------- langkah bernomor (panduan) ---------- */
.tb-steps { display:grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap:14px; }
.tb-step { background:var(--bg); border:1px solid var(--bd); border-radius:14px; padding:14px 16px;
           border-top:4px solid var(--c); box-shadow: 0 4px 14px rgba(30,60,140,0.06); }
.tb-step:nth-child(4n+1) { --c:#2563EB; --bg:#EEF4FF; --bd:#D3E0FB; }
.tb-step:nth-child(4n+2) { --c:#21A876; --bg:#EAF8F1; --bd:#C9EBDA; }
.tb-step:nth-child(4n+3) { --c:#EA6A35; --bg:#FFF3EB; --bd:#F8DCC9; }
.tb-step:nth-child(4n+4) { --c:#5B3FC4; --bg:#F3F0FF; --bd:#DDD5FB; }
.tb-step-num { width:28px; height:28px; border-radius:50%; background:var(--c); color:#FFFFFF;
               font-weight:700; display:flex; align-items:center; justify-content:center; margin-bottom:8px; }
.tb-step-title { font-weight:700; color:#16213E; margin-bottom:4px; }
.tb-step-text { color:#4A5573; font-size:0.86rem; line-height:1.45; }

/* ---------- kartu angka ---------- */
.tb-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:16px; }
.tb-card { background:#FFFFFF; border:1px solid #E4EAF5; border-radius:16px; padding:16px 18px 14px 18px;
           box-shadow: 0 1px 2px rgba(16,40,90,0.04); }
.tb-card-top { display:flex; justify-content:space-between; align-items:flex-start; }
.tb-card-label { color:#6B7590; font-size:0.84rem; }
.tb-card-value { font-size:1.7rem; font-weight:800; color:#16213E; margin-top:4px; line-height:1.15; }
.tb-card-sub { color:#6B7590; font-size:0.8rem; margin-top:4px; min-height:1.1rem; }
.tb-icon { width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; }
.tb-track { height:5px; background:rgba(255,255,255,0.85); border-radius:99px; margin-top:12px; overflow:hidden; }
.tb-fill { height:100%; border-radius:99px; }

/* ---------- daftar batang ---------- */
.tb-row { display:grid; grid-template-columns: 34% 1fr 64px; align-items:center; gap:12px; padding:5px 0; }
.tb-row-label { color:#2B3550; font-size:0.88rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.tb-row-val { text-align:right; font-weight:700; color:#16213E; font-size:0.88rem; }

/* ---------- kartu Streamlit (container ber-key "card...") dan metric ---------- */
div[class*="st-key-card"] { background:#FFFFFF; border:1px solid #E4EAF5 !important; border-radius:16px;
                            padding: 18px 20px; box-shadow: 0 4px 14px rgba(30,60,140,0.07); }
/* warna pastel per kartu: nama warna ada di key, mis. key="card_mint_..." */
div[class*="st-key-card_sky"]      { background:linear-gradient(135deg,#E8F0FF 0%,#F1ECFF 100%); border-color:#D3E0FB !important; border-top:4px solid #2563EB !important; }
div[class*="st-key-card_mint"]     { background:linear-gradient(135deg,#E3F7EE 0%,#EAF3FF 100%); border-color:#C9EBDA !important; border-top:4px solid #21A876 !important; }
div[class*="st-key-card_peach"]    { background:linear-gradient(135deg,#FFEFE4 0%,#FFF8E1 100%); border-color:#F8DCC9 !important; border-top:4px solid #EA6A35 !important; }
div[class*="st-key-card_lavender"] { background:linear-gradient(135deg,#F0ECFF 0%,#FFEFF5 100%); border-color:#DDD5FB !important; border-top:4px solid #5B3FC4 !important; }
div[class*="st-key-card_butter"]   { background:linear-gradient(135deg,#FFF7DC 0%,#FFEFE6 100%); border-color:#F3E4B3 !important; border-top:4px solid #E0A100 !important; }
div[class*="st-key-card_rose"]     { background:linear-gradient(135deg,#FFEDF3 0%,#F2EEFF 100%); border-color:#F6D2DE !important; border-top:4px solid #E5739D !important; }
/* kartu hasil pencarian: putih dengan aksen biru di kiri agar mudah dibaca */
div[class*="st-key-card_hasil"] { border-left:4px solid #2563EB !important; }
/* kotak input di dalam kartu berwarna tetap putih */
div[class*="st-key-card"] [data-baseweb="input"], div[class*="st-key-card"] [data-baseweb="base-input"],
div[class*="st-key-card"] [data-baseweb="input"] input, div[class*="st-key-card"] [data-baseweb="select"] > div {
    background:#FFFFFF !important;
}
/* tombol contoh query: pil warna-warni */
div[class*="_examples"] button { border-radius:999px; min-height:32px; padding:2px 14px;
                                 background:var(--pb) !important; border:1px solid var(--pl) !important; }
div[class*="_examples"] button p { font-size:0.86rem; font-weight:600; color:var(--pt) !important; }
div[class*="_examples"] button:hover { filter:brightness(0.96); }
div[class*="_examples"] > div:nth-child(6n+1) { --pb:#E3ECFF; --pl:#BFD3FF; --pt:#1E4FD8; }
div[class*="_examples"] > div:nth-child(6n+2) { --pb:#DFF5EA; --pl:#B4E4CB; --pt:#15803D; }
div[class*="_examples"] > div:nth-child(6n+3) { --pb:#FFE9DC; --pl:#F8CBAE; --pt:#C2410C; }
div[class*="_examples"] > div:nth-child(6n+4) { --pb:#EEE8FF; --pl:#D3C7FB; --pt:#5B3FC4; }
div[class*="_examples"] > div:nth-child(6n+5) { --pb:#FFF3CC; --pl:#F1DC92; --pt:#A16207; }
div[class*="_examples"] > div:nth-child(6n+6) { --pb:#FFE6EF; --pl:#F5C2D4; --pt:#BE185D; }
/* tombol Kosongkan */
div[class*="_clear"] button { background:#FFE9EF !important; border:1px solid #F5C2D4 !important; }
div[class*="_clear"] button p, div[class*="_clear"] button span { color:#BE185D !important; font-weight:600; }
div[class*="_clear"] button:disabled { opacity:0.55; }
[data-testid="stExpander"] details { background:linear-gradient(90deg,#FFF7DC 0%,#FFFFFF 70%); border-radius:14px;
                                      border-left:4px solid #E0A100 !important; }
[data-testid="stExpander"] summary p { font-weight:600; color:#8A5A00; }
/* metric berwarna bergantian */
div[data-testid="stMetric"] { background:#FFFFFF; border-top:4px solid var(--m, #2563EB) !important; }
div[data-testid="stElementContainer"]:nth-child(6n+1) div[data-testid="stMetric"] { --m:#2563EB; background:#EEF4FF; }
div[data-testid="stElementContainer"]:nth-child(6n+2) div[data-testid="stMetric"] { --m:#21A876; background:#EAF8F1; }
div[data-testid="stElementContainer"]:nth-child(6n+3) div[data-testid="stMetric"] { --m:#EA6A35; background:#FFF3EB; }
div[data-testid="stElementContainer"]:nth-child(6n+4) div[data-testid="stMetric"] { --m:#5B3FC4; background:#F3F0FF; }
div[data-testid="stElementContainer"]:nth-child(6n+5) div[data-testid="stMetric"] { --m:#E0A100; background:#FFF9E6; }
div[data-testid="stElementContainer"]:nth-child(6n+6) div[data-testid="stMetric"] { --m:#E5739D; background:#FFF0F5; }
.tb-card-title { font-weight:700; font-size:1.02rem; color:#16213E; }
.tb-card-caption { color:#6B7590; font-size:0.8rem; margin-bottom:6px; }
</style>
"""

# Ikon garis (gaya Lucide), digambar dengan stroke putih di atas kotak berwarna
ICONS = {
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "landmark": '<line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
    "palette": '<circle cx="13.5" cy="6.5" r="1"/><circle cx="17.5" cy="10.5" r="1"/><circle cx="8.5" cy="7.5" r="1"/><circle cx="6.5" cy="12.5" r="1"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.9 0 1.6-.7 1.6-1.7 0-.4-.2-.8-.4-1.1-.3-.3-.4-.7-.4-1.1a1.6 1.6 0 0 1 1.7-1.7h2c3 0 5.5-2.5 5.5-5.5C22 6 17.5 2 12 2z"/>',
    "hash": '<line x1="4" x2="20" y1="9" y2="9"/><line x1="4" x2="20" y1="15" y2="15"/><line x1="10" x2="8" y1="3" y2="21"/><line x1="16" x2="14" y1="3" y2="21"/>',
    "layers": '<path d="m12.8 2.2a2 2 0 0 0-1.7 0L2.6 6.1a1 1 0 0 0 0 1.8l8.6 3.9a2 2 0 0 0 1.7 0l8.6-3.9a1 1 0 0 0 0-1.8Z"/><path d="m22 17.6-9.2 4.2a2 2 0 0 1-1.7 0L2 17.6"/><path d="m22 12.6-9.2 4.2a2 2 0 0 1-1.7 0L2 12.6"/>',
    "ruler": '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 12.9 17 22l-5-3-5 3 1.5-9.1"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
}

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]


def tanggal_hari_ini():
    d = datetime.date.today()
    return f"{HARI[d.weekday()]}, {d.day} {BULAN[d.month - 1]} {d.year}"


def fmt_angka(x):
    return f"{x:,}".replace(",", ".")


def svg(name, color="#FFFFFF", size=20):
    """Ikon sebagai <img> data URI (tag <svg> langsung dibuang oleh penyaring st.html)."""
    raw = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
           f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
           f'{ICONS[name]}</svg>')
    b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="{size}" height="{size}" alt="">' 


def inject_css():
    st.html(CSS)


def sidebar_brand():
    st.html(f"""
    <div class="sb-brand">
      <div class="sb-logo">{svg("search", BLUE, 22)}</div>
      <div><div class="sb-title">Mesin Pencari Budaya</div>
           <div class="sb-sub">Indonesia Kaya · Tradisi &amp; Kesenian</div></div>
    </div>""")


def sidebar_section(label):
    st.html(f'<div class="sb-section">{html.escape(label)}</div>')


def sidebar_footer(n_docs, n_terms):
    st.html(f'<div class="sb-foot">{n_docs} dokumen · {fmt_angka(n_terms)} term<br>'
            f'BM25: k1 = 1,2 · b = 0,75</div>')


def page_header(title, subtitle):
    st.html(f"""
    <div class="tb-header">
      <div><div class="tb-title">{html.escape(title)}</div>
           <div class="tb-sub">{html.escape(subtitle)}</div></div>
      <div class="tb-chip">
        <div class="tb-avatar">B</div>
        <div><div class="tb-chip-name">Tugas 2 · Temu Kembali Informasi</div>
             <div class="tb-chip-date">{tanggal_hari_ini()}</div></div>
      </div>
    </div>""")


def banner(title, subtitle):
    st.html(f"""
    <div class="tb-banner">
      <div class="tb-banner-date">{tanggal_hari_ini()}</div>
      <div class="tb-banner-title">{html.escape(title)}</div>
      <div class="tb-banner-sub">{html.escape(subtitle)}</div>
    </div>""")


def kpi_cards(cards):
    """cards: list dict {label, value, sub, icon, color, pct (0-100)}."""
    items = []
    for c in cards:
        pct = max(0.0, min(100.0, float(c.get("pct", 0))))
        items.append(f"""
        <div class="tb-card" style="background:{c['color']}14;border-color:{c['color']}33">
          <div class="tb-card-top">
            <div><div class="tb-card-label">{html.escape(c['label'])}</div>
                 <div class="tb-card-value">{html.escape(str(c['value']))}</div></div>
            <div class="tb-icon" style="background:{c['color']}">{svg(c['icon'])}</div>
          </div>
          <div class="tb-card-sub">{html.escape(c.get('sub', ''))}</div>
          <div class="tb-track"><div class="tb-fill" style="width:{pct:.1f}%;background:{c['color']}"></div></div>
        </div>""")
    st.html(f'<div class="tb-grid">{"".join(items)}</div>')


def steps_row(steps):
    """steps: list (judul, keterangan). Kartu bernomor berjajar untuk menjelaskan alur."""
    items = "".join(
        f'<div class="tb-step"><div class="tb-step-num">{i}</div>'
        f'<div class="tb-step-title">{html.escape(t)}</div>'
        f'<div class="tb-step-text">{html.escape(d)}</div></div>'
        for i, (t, d) in enumerate(steps, 1))
    st.html(f'<div class="tb-steps">{items}</div>')


def transparent(chart):
    """Latar grafik dibuat transparan agar menyatu dengan warna kartu."""
    return chart.configure(background="transparent").configure_view(stroke=None)


def bar_chart(df, x, y, color=None, height=260, single_color=BLUE):
    """Grafik batang (berkelompok jika ada `color`) dengan urutan sumbu x sesuai data."""
    enc = {"x": alt.X(f"{x}:N", sort=None, title=x, axis=alt.Axis(labelAngle=0)),
           "y": alt.Y(f"{y}:Q", title=y),
           "tooltip": [x, y] + ([color] if color else [])}
    if color:
        enc.update(color=alt.Color(f"{color}:N", legend=alt.Legend(orient="bottom", title=None)),
                   xOffset=f"{color}:N")
    mark = alt.Chart(df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3,
                                  **({} if color else {"color": single_color}))
    st.altair_chart(transparent(mark.encode(**enc).properties(height=height)), width="stretch")


def card_title(title, caption=""):
    st.html(f'<div class="tb-card-title">{html.escape(title)}</div>'
            + (f'<div class="tb-card-caption">{html.escape(caption)}</div>' if caption else ""))


def bar_list(rows, colors):
    """rows: list (label, nilai). Menampilkan daftar dengan batang horizontal."""
    top = max(v for _, v in rows) or 1
    out = []
    for i, (label, value) in enumerate(rows):
        color = colors[i % len(colors)]
        out.append(f"""
        <div class="tb-row">
          <div class="tb-row-label">{html.escape(str(label))}</div>
          <div class="tb-track" style="margin-top:0;height:8px">
            <div class="tb-fill" style="width:{100 * value / top:.1f}%;background:{color}"></div></div>
          <div class="tb-row-val">{fmt_angka(value)}</div>
        </div>""")
    st.html("".join(out))
