"""Aplikasi web prediksi kategori ISPU H+1 DKI Jakarta (Streamlit)."""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ispu
from ispu import KELAS, NAMA_POLUTAN, POLUTAN

st.set_page_config(page_title="Prediksi ISPU H+1 Jakarta", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")

# ------------------------------------------------------------------ tema
WARNA = {"BAIK": "#2fa36b", "SEDANG": "#f5b82e", "TIDAK SEHAT": "#ef6a3c"}
TEKS_DI_ATAS = {"BAIK": "#ffffff", "SEDANG": "#3b2f00", "TIDAK SEHAT": "#ffffff"}
INDIGO, LIME, NAVY = "#4f46e5", "#d8f56b", "#14192b"
SARAN = {
    "BAIK": "Kualitas udara baik. Aktivitas luar ruangan aman dilakukan.",
    "SEDANG": "Kelompok sensitif (anak, lansia, penderita asma) sebaiknya mengurangi aktivitas berat di luar ruangan.",
    "TIDAK SEHAT": "Kurangi aktivitas luar ruangan, gunakan masker, dan perhatikan kelompok rentan.",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--indigo:#4f46e5;--lime:#d8f56b;--navy:#14192b;--ink:#151a2b;--mute:#6b7390;--line:#e4e9f5;--card:#ffffff;}
html,body,.stApp,[class*="st-"]{font-family:'Plus Jakarta Sans',system-ui,sans-serif;}
.stApp{background:linear-gradient(180deg,#f4f7ff 0%,#fbfcff 380px,#ffffff 100%);color:var(--ink);}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none !important;}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none !important;}
.block-container{max-width:100% !important;padding:1.4rem 2rem 4rem 2rem !important;}
[data-testid="stIconMaterial"],.material-symbols-rounded,.material-icons{font-family:'Material Symbols Rounded','Material Icons' !important;}
h1,h2,h3{color:var(--ink);letter-spacing:-0.02em;font-weight:800;}
.acc{color:var(--indigo);}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:1.05rem;letter-spacing:-.01em;padding-top:6px;}
.logo{width:30px;height:30px;border-radius:10px;background:linear-gradient(135deg,#4f46e5,#8fb4ff);display:grid;place-items:center;color:#fff;font-size:16px;}
.chip-lime{display:inline-block;background:var(--lime);color:#1b2a00;font-weight:700;font-size:.82rem;padding:8px 16px;border-radius:999px;}
.chip-out{display:inline-block;border:1px solid #c9d3ee;color:var(--ink);font-weight:600;font-size:.82rem;padding:7px 14px;border-radius:999px;background:#ffffffaa;}
.topright{text-align:right;padding-top:2px;}
/* hero */
.hero{position:relative;overflow:hidden;border-radius:28px;padding:44px 44px 40px;margin:14px 0 14px;
 background:radial-gradient(circle at 85% 90%,#e4f9a3 0,#e4f9a300 38%),radial-gradient(circle at 70% 10%,#ffffffcc 0,#ffffff00 40%),linear-gradient(135deg,#b9d4ff 0%,#d6e6ff 45%,#eef4ff 100%);
 display:grid;grid-template-columns:1.25fr 1fr;gap:28px;align-items:center;min-height:330px;}
.hero h1{font-size:3rem;line-height:1.05;margin:0 0 14px;}
.hero p{max-width:480px;color:#3d4766;font-size:1rem;line-height:1.6;margin:0 0 20px;}
.blob{position:absolute;border-radius:50%;pointer-events:none;}
.b1{width:190px;height:190px;right:-50px;bottom:-60px;background:radial-gradient(circle at 30% 30%,#f2ffb4,#c6ec4c 70%);filter:blur(1px);}
.b2{width:120px;height:120px;right:310px;top:-40px;border:26px solid #6d63f0;opacity:.35;}
.glass{position:relative;z-index:1;background:#ffffffb8;backdrop-filter:blur(10px);border:1px solid #ffffff;border-radius:22px;padding:20px 22px;box-shadow:0 14px 40px rgba(60,80,180,.18);max-width:340px;justify-self:end;width:100%;}
.glass .t{font-size:.78rem;color:var(--mute);font-weight:600;}
.glass .v{font-size:2.3rem;font-weight:800;color:var(--indigo);line-height:1.1;margin:2px 0;}
.glass .s{font-size:.8rem;color:var(--mute);}
.bars{display:flex;gap:8px;align-items:flex-end;height:84px;margin-top:14px;}
.bars span{flex:1;border-radius:8px 8px 4px 4px;}
.bars-l{display:flex;gap:8px;font-size:.68rem;color:var(--mute);margin-top:6px;}.bars-l span{flex:1;text-align:center;}
/* bento */
.bento{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:34px;}
.bc{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px 18px;min-height:150px;box-shadow:0 4px 18px rgba(60,80,160,.06);position:relative;overflow:hidden;}
.bc .h{font-size:.8rem;font-weight:700;color:var(--ink);}
.bc .d{font-size:.78rem;color:var(--mute);margin-top:4px;line-height:1.45;}
.bc.dark{background:var(--navy);color:#fff;}
.bc.dark .big{font-size:1.15rem;font-weight:700;line-height:1.3;margin-top:14px;}
.bc.dark .big b{color:var(--lime);font-weight:800;}
.star{width:28px;height:28px;border-radius:9px;background:var(--lime);display:grid;place-items:center;font-size:14px;color:#1b2a00;}
.orb{position:absolute;right:-18px;bottom:-22px;width:90px;height:90px;border-radius:50%;}
.o-a{background:radial-gradient(circle at 30% 30%,#a9c8ff,#5b7cf0);} .o-b{background:radial-gradient(circle at 30% 30%,#f3ffb8,#bde33f);}
.row{display:flex;justify-content:space-between;font-size:.76rem;padding:5px 0;border-top:1px solid var(--line);color:#3d4766;} .row b{color:var(--ink);}
.row.top b{color:var(--indigo);}
.tag{display:inline-block;font-size:.7rem;font-weight:700;padding:5px 10px;border-radius:999px;margin:6px 4px 0 0;}
/* section heads */
.eyebrow{font-size:.72rem;letter-spacing:.14em;color:var(--mute);font-weight:700;text-transform:uppercase;margin-top:6px;}
.eyebrow:before{content:"• ";color:var(--indigo);}
.sec{margin-top:18px;}
.sec h2{font-size:2.1rem;line-height:1.1;margin:.3rem 0 .4rem;}
.sec p{color:var(--mute);max-width:620px;margin:0 0 14px;}
/* stat cards */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:10px 0 26px;}
.st-card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:18px 20px;}
.st-card .i{width:34px;height:34px;border-radius:11px;background:#eef1ff;display:grid;place-items:center;margin-bottom:22px;}
.st-card .l{font-size:.8rem;color:var(--mute);font-weight:600;} .st-card .n{font-size:2rem;font-weight:800;letter-spacing:-.02em;} .st-card .k{font-size:.78rem;color:var(--mute);}
.st-card.lime{background:var(--lime);border-color:var(--lime);} .st-card.lime .i{background:#ffffff99;} .st-card.lime .l,.st-card.lime .k{color:#3c4d0a;}
.st-card.dark{background:var(--navy);border-color:var(--navy);color:#fff;} .st-card.dark .i{background:#ffffff1f;} .st-card.dark .l,.st-card.dark .k{color:#aeb6d4;}
/* hasil */
.hasil{border-radius:24px;padding:26px 28px;position:relative;overflow:hidden;}
.hasil:after{content:"";position:absolute;right:-40px;bottom:-50px;width:170px;height:170px;border-radius:50%;background:#ffffff26;}
.hasil .label{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;opacity:.9;font-weight:700;}
.hasil .nilai{font-size:2.8rem;font-weight:800;line-height:1.1;margin:.25rem 0 .4rem;letter-spacing:-.02em;}
.kartu{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px 20px;margin-top:10px;}
.kartu.dark{background:var(--navy);border-color:var(--navy);color:#dfe4f7;} .kartu.dark b{color:var(--lime);}
.pil{display:inline-block;padding:3px 12px;border-radius:999px;font-weight:700;font-size:.82rem;}
.kecil{color:var(--mute);font-size:.86rem;}
/* streamlit elemen */
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-radius:24px !important;border:1px solid var(--line) !important;box-shadow:0 6px 24px rgba(60,80,160,.06);}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div{border-radius:14px !important;}
[data-testid="stDataFrame"]{border-radius:16px;overflow:hidden;}
.st-key-bento{display:grid !important;grid-template-columns:repeat(5,1fr);gap:14px !important;margin-bottom:34px;align-items:start;}
.st-key-bento button{height:var(--kh);border-radius:22px;background:#fff;border:1px solid var(--line);box-shadow:0 4px 18px rgba(60,80,160,.06);padding:20px 22px;justify-content:flex-start;align-items:flex-start;transition:transform .15s,box-shadow .15s,border-color .15s;animation:flipIn .5s ease;}
.st-key-bento button>div{flex-direction:column;align-items:flex-start !important;justify-content:flex-start !important;gap:14px;width:100%;}
.st-key-bento button span{justify-content:flex-start !important;text-align:left;}
.st-key-bento button>div>span{flex-direction:column !important;align-items:flex-start !important;gap:14px;height:auto !important;}
.st-key-bento button>div>span>span{height:auto !important;}
.st-key-bento button [data-testid="stIconEmoji"],.st-key-bento button [data-testid="stIconMaterial"]{font-size:2rem;line-height:1;}
.st-key-bento button p{font-size:1.25rem;font-weight:800;text-align:left;color:var(--ink);line-height:1.25;letter-spacing:-.01em;}
.st-key-bento button:hover{transform:translateY(-4px);border-color:#c3c9fa;box-shadow:0 12px 28px rgba(79,70,229,.18);}
.st-key-kartu0 button:hover,.st-key-kartu0 button:focus,.st-key-kartu0 button:active{background:#e6f0ff !important;border-color:#9db8f5 !important;}
.st-key-kartu0 button:hover p,.st-key-kartu0 button:focus p,.st-key-kartu0 button:active p{color:var(--ink) !important;}
.st-key-kartu1 button:hover,.st-key-kartu1 button:focus,.st-key-kartu1 button:active{background:#f0fbc4 !important;border-color:#bde33f !important;}
.st-key-kartu1 button:hover p,.st-key-kartu1 button:focus p,.st-key-kartu1 button:active p{color:var(--ink) !important;}
.st-key-kartu2 button:hover,.st-key-kartu2 button:focus,.st-key-kartu2 button:active{background:#232b52 !important;border-color:#d8f56b !important;}
.st-key-kartu2 button:hover p,.st-key-kartu2 button:focus p,.st-key-kartu2 button:active p{color:#ffffff !important;}
.st-key-kartu3 button:hover,.st-key-kartu3 button:focus,.st-key-kartu3 button:active{background:#ece8ff !important;border-color:#a99cf7 !important;}
.st-key-kartu3 button:hover p,.st-key-kartu3 button:focus p,.st-key-kartu3 button:active p{color:var(--ink) !important;}
.st-key-kartu4 button:hover,.st-key-kartu4 button:focus,.st-key-kartu4 button:active{background:#ffeadb !important;border-color:#f5a97c !important;}
.st-key-kartu4 button:hover p,.st-key-kartu4 button:focus p,.st-key-kartu4 button:active p{color:var(--ink) !important;}
.st-key-kartu2 button{background:var(--navy);border-color:var(--navy);} .st-key-kartu2 button p{color:#fff;} .st-key-kartu2 button:hover{border-color:var(--lime);}
.st-key-bento{--kh:150px;}
[class*="st-key-slot"]{gap:0 !important;}
[class*="st-key-slot"] [data-testid="stElementContainer"]:has(.flipstate){display:none !important;}
[class*="st-key-slot"]:has(.flipstate.on) [class*="st-key-kartu"]{display:none !important;}
[class*="st-key-slot"]:has(.flipstate.off) [class*="st-key-back"]{display:none !important;}
[class*="st-key-back"]{position:relative;height:var(--kh) !important;min-height:var(--kh) !important;box-sizing:border-box;overflow:hidden;background:linear-gradient(145deg,#4f46e5,#6f66f2);color:#fff;border-radius:22px;padding:18px 20px;box-shadow:0 12px 30px rgba(79,70,229,.28);animation:flipIn .5s ease;gap:0 !important;}
[class*="st-key-back"] .bt{font-size:1.05rem;font-weight:800;color:var(--lime);margin-bottom:6px;line-height:1.2;}
[class*="st-key-back"] .bb{font-size:.84rem;line-height:1.45;color:#eef0ff;}
[class*="st-key-back"] .hint{position:absolute;right:16px;bottom:9px;font-size:.66rem;opacity:.7;}
[class*="st-key-back"] [data-testid="stElementContainer"]:has(button){position:absolute !important;top:0;left:0;width:100% !important;height:100% !important;z-index:3;}
[class*="st-key-back"] [data-testid="stButton"]{width:100% !important;height:100% !important;}
[class*="st-key-back"] button{position:absolute;top:0;left:0;width:100% !important;height:100% !important;min-height:0 !important;opacity:0;cursor:pointer;animation:none !important;}
@keyframes flipIn{from{transform:perspective(900px) rotateY(-90deg);opacity:.15;}to{transform:perspective(900px) rotateY(0);opacity:1;}}
.st-key-burger,.st-key-mobmenu,.st-key-scrim{display:none;}
.st-key-burger button{width:44px;height:44px;border-radius:14px;border:1px solid var(--line);background:#fff;padding:0;} .st-key-burger button p{font-size:1.3rem;line-height:1;}
.st-key-scrim{position:fixed;top:0;left:0;width:100vw;height:100dvh;z-index:999;background:rgba(20,25,43,.45);animation:fadeIn .25s ease;}
.st-key-scrim [data-testid="stElementContainer"],.st-key-scrim [data-testid="stButton"]{width:100% !important;height:100% !important;}
.st-key-scrim button{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;cursor:pointer;}
.st-key-mobmenu{position:fixed;top:0;left:0;height:100dvh;width:min(78vw,300px);z-index:1000;background:linear-gradient(225deg,#c3e94a 0%,#e3f6a0 20%,#f6fbe0 38%,#ffffff 60%,#ffffff 100%);padding:22px 14px;border-radius:0 26px 26px 0;box-shadow:12px 0 40px rgba(20,25,43,.25);animation:slideInLeft .3s cubic-bezier(.2,.8,.2,1);gap:.4rem !important;overflow-y:auto;}
.st-key-mobmenu .drawer-t{display:flex;align-items:center;gap:10px;font-weight:800;font-size:1.05rem;color:#1f3a0a;padding:2px 8px 14px;border-bottom:1px solid #1f3a0a1f;margin-bottom:10px;}
.st-key-mobmenu .logo{background:linear-gradient(135deg,#8bc83a,#c3e94a);}
.st-key-mobmenu button{justify-content:flex-start;border:1px solid #dfe9c4;border-radius:16px;background:#ffffffd9;padding:12px 14px;transition:transform .15s,background .15s,border-color .15s;}
.st-key-mobmenu button p{font-weight:700;font-size:1rem;color:var(--ink);text-align:left;}
.st-key-mobmenu button:hover,.st-key-mobmenu button:focus{background:#f1fbc8 !important;border-color:#b9de45 !important;transform:translateX(4px);}
.st-key-mobmenu button:hover p,.st-key-mobmenu button:focus p{color:var(--ink) !important;}
.st-key-mobmenu button[kind="primary"]{background:linear-gradient(135deg,#a6d636,#86bd27) !important;border-color:#76a91f !important;box-shadow:0 8px 20px rgba(100,150,20,.3);}
.st-key-mobmenu button[kind="primary"] p{color:#1f3a0a !important;}
.st-key-mobmenu button>div{justify-content:flex-start !important;width:100%;} .st-key-mobmenu button span{justify-content:flex-start !important;text-align:left;}
.st-key-mobmenu [data-testid="stElementContainer"]:has(.drawer-f){margin-top:auto;}
.st-key-mobmenu .drawer-f{padding:10px 8px 4px;}
.st-key-mobmenu .drawer-f .kecil{display:block;margin-top:8px;color:#5b6a45;font-weight:600;}
@keyframes slideInLeft{from{transform:translateX(-105%);}to{transform:translateX(0);}}
@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
.st-key-nav{display:flex;justify-content:center;width:100% !important;}
.st-key-nav [data-testid="stButtonGroup"]{justify-content:center;flex-wrap:nowrap;}
@media(max-width:700px){
 .block-container{padding:1rem 1rem 3rem !important;}
 .topright{display:none;}
 [data-testid="stColumn"]:has(.st-key-nav){display:none !important;}
 .st-key-topbar [data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:.5rem;}
 .st-key-topbar [data-testid="stColumn"]{min-width:0 !important;width:auto !important;flex:1 1 auto !important;}
 .st-key-topbar [data-testid="stColumn"]:last-child{flex:0 0 auto !important;}
 .st-key-burger{display:block;}
 .st-key-mobmenu,.st-key-scrim{display:flex;}
 .st-key-scrim{display:block;}
 .st-key-topbar [data-testid="stColumn"]:last-child{order:-1;}
 .st-key-topbar .brand{justify-content:flex-end;}
 .hero{padding:22px 20px;min-height:0;border-radius:22px;gap:18px;}
 .hero h1{font-size:1.8rem;} .hero p{font-size:.92rem;} .b2{display:none;}
 .glass{padding:16px 18px;max-width:none;}
 .st-key-bento{grid-template-columns:repeat(2,1fr);gap:10px !important;}
 .st-key-bento{--kh:132px;}
 .st-key-slot2,.st-key-bento>*:has(.st-key-slot2){grid-column:span 2;}
 .st-key-bento button{padding:14px;} .st-key-bento button p{font-size:1.05rem;}
 [class*="st-key-back"]{padding:14px 15px;} [class*="st-key-back"] .bt{font-size:.92rem;margin-bottom:4px;} [class*="st-key-back"] .bb{font-size:.74rem;line-height:1.4;} [class*="st-key-back"] .hint{display:none;}
 .st-card .n{font-size:1.5rem;} .st-card .i{margin-bottom:12px;}
 .hasil .nilai{font-size:2.2rem;} .sec h2{font-size:1.6rem;}
}
@media(max-width:900px){.hero{grid-template-columns:1fr;padding:28px;}.hero h1{font-size:2.1rem;}.glass{justify-self:start;}.bento{grid-template-columns:repeat(2,1fr);}.stats{grid-template-columns:repeat(2,1fr);}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

_BLN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def tgl(d) -> str:
    d = pd.Timestamp(d)
    return f"{d.day} {_BLN[d.month - 1]} {d.year}"


def pil(k: str) -> str:
    return f'<span class="pil" style="background:{WARNA[k]};color:{TEKS_DI_ATAS[k]}">{k}</span>'


def kepala(label: str, judul: str, sub: str = ""):
    st.markdown(f'<div class="sec"><div class="eyebrow">{label}</div><h2>{judul}</h2><p>{sub}</p></div>', unsafe_allow_html=True)


def kartu_stat(items):
    html = ""
    for ikon, label, nilai, ket, varian in items:
        html += f'<div class="st-card {varian}"><div class="i">{ikon}</div><div class="l">{label}</div><div class="n">{nilai}</div><div class="k">{ket}</div></div>'
    st.markdown(f'<div class="stats">{html}</div>', unsafe_allow_html=True)


def layout_plot(fig, h=320, **kw):
    fig.update_layout(height=h, margin=dict(l=0, r=0, t=36, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Plus Jakarta Sans, sans-serif", color="#3d4766"),
                      colorway=[INDIGO, "#8fb4ff", "#bde33f", NAVY, "#a78bfa"], **kw)
    fig.update_xaxes(gridcolor="#eef1fa")
    fig.update_yaxes(gridcolor="#eef1fa")
    return fig


@st.cache_data
def data():
    return ispu.load_data()


@st.cache_resource
def model(nama):
    return ispu.muat_model(nama)


df = data()
STASIUN = sorted(df["stasiun"].unique())
MEDIAN = {p: float(df[p].median()) for p in POLUTAN}
PERB = pd.read_csv(ispu.BASE / "data" / "perbandingan_model.csv", index_col=0)
HALAMAN = ["Prediksi", "Data", "Evaluasi", "Tentang"]

# ------------------------------------------------------------------ navigasi atas
st.session_state.setdefault("nav", "Prediksi")
st.session_state.setdefault("menu_open", False)


def _pilih(p):
    st.session_state["nav"] = p
    st.session_state["menu_open"] = False


def _toggle_menu():
    st.session_state["menu_open"] = not st.session_state["menu_open"]


with st.container(key="topbar"):
    n1, n2, n3 = st.columns([1, 2.4, 1], vertical_alignment="center")
    n1.markdown('<div class="brand"><div class="logo">🌿</div>ISPU·H+1</div>', unsafe_allow_html=True)
    with n2:
        st.segmented_control("Menu", HALAMAN, key="nav", label_visibility="collapsed")
    with n3:
        st.markdown('<div class="topright"><span class="chip-lime">Kelompok 6 · Kelas A</span></div>', unsafe_allow_html=True)
        st.button("✕" if st.session_state["menu_open"] else "☰", key="burger", on_click=_toggle_menu)
if st.session_state["menu_open"]:
    with st.container(key="scrim"):
        st.button("Tutup menu", key="scrim_btn", on_click=_toggle_menu)
    with st.container(key="mobmenu"):
        st.markdown('<div class="drawer-t"><div class="logo">🌿</div>Menu</div>', unsafe_allow_html=True)
        IKON = {"Prediksi": "🌤️", "Data": "📊", "Evaluasi": "🎯", "Tentang": "🌿"}
        for p in HALAMAN:
            st.button(p, icon=IKON[p], key=f"m_{p}", on_click=_pilih, args=(p,), type="primary" if st.session_state["nav"] == p else "secondary", width="stretch")
        st.markdown('<div class="drawer-f"><span class="chip-lime">Kelompok 6 · Kelas A</span><span class="kecil">Prediksi ISPU H+1 DKI Jakarta</span></div>', unsafe_allow_html=True)
halaman = st.session_state.get("nav") or "Prediksi"


# ================================================================== PREDIKSI
TEKS_BELAKANG = [
    f"Data harian 5 stasiun Jakarta, 2010–2025: {len(df):,} baris dengan 5 polutan.".replace(",", "."),
    "58 petunjuk untuk model: nilai hari ini, 7 hari lalu, rata-rata, dan waktu.",
    "Data hari ini → diolah jadi 58 fitur → model menghitung → kategori besok beserta peluangnya.",
    f"Nilai ketepatan 0–1, makin dekat 1 makin baik. Random Forest tertinggi ({PERB.loc['Random Forest', 'F1 macro validasi (CV)']:.3f}).",
    "Kategori udara besok: Baik, Sedang, atau Tidak Sehat.",
]


KARTU = [("🗂️", "Data historis"), ("🧩", "Fitur"), ("✨", "Dari data hari ini, ke kategori besok"), ("📈", "F1 validasi"), ("🏷️", "Target klasifikasi")]


def _buka(i):
    st.session_state["flip"] = i


def _tutup():
    st.session_state["flip"] = None


def bento():
    buka = st.session_state.get("flip")
    st.caption("Ketuk kartu untuk membaliknya, ketuk lagi untuk menutup.")
    with st.container(key="bento"):
        for i, (ikon, judul) in enumerate(KARTU):
            # Depan dan belakang selalu ada di slot yang sama; CSS yang menampilkan salah satunya,
            # jadi tata letak tidak bergeser saat kartu dibalik.
            with st.container(key=f"slot{i}"):
                st.markdown(f'<span class="flipstate {"on" if buka == i else "off"}"></span>', unsafe_allow_html=True)
                st.button(judul, icon=ikon, key=f"kartu{i}", on_click=_buka, args=(i,), width="stretch")
                with st.container(key=f"back{i}"):
                    st.markdown(f'<div class="bt">{judul}</div><div class="bb">{TEKS_BELAKANG[i]}</div>', unsafe_allow_html=True)
                    st.button("Balik", key=f"tutup{i}", on_click=_tutup)


def hero():
    dist = df["kategori"].value_counts(normalize=True).reindex(KELAS)
    f1 = PERB.loc["Random Forest", "F1 macro validasi (CV)"]
    batang = "".join(f'<span style="height:{max(dist[k]/dist.max()*100, 14):.0f}%;background:{WARNA[k]}"></span>' for k in KELAS)
    label = "".join(f"<span>{k.title()}<br>{dist[k]*100:.0f}%</span>" for k in KELAS)
    st.markdown(
        f"""
<div class="hero"><div class="blob b1"></div><div class="blob b2"></div>
 <div style="position:relative;z-index:1">
  <h1>Udara Jakarta besok,<br><span class="acc">terbaca hari ini.</span></h1>
  <p>Model machine learning memperkirakan kategori ISPU hari berikutnya (H+1) dari riwayat polutan 7 hari di lima stasiun pemantauan.</p>
  <span class="chip-lime">Random Forest · 58 fitur</span> &nbsp;<span class="chip-out">5 stasiun SPKU</span>
 </div>
 <div class="glass"><div class="t">F1 macro validasi · Random Forest</div><div class="v">{f1:.3f}</div>
  <div class="s">Komposisi kategori pada data</div><div class="bars">{batang}</div><div class="bars-l">{label}</div></div>
</div>""",
        unsafe_allow_html=True,
    )
    bento()


def halaman_prediksi():
    hero()
    kepala("Prediksi", "Pilih stasiun dan <span class='acc'>tanggal.</span>", "Model menghitung peluang tiap kategori untuk hari berikutnya.")

    tersedia = ispu.model_tersedia()
    if not tersedia:
        st.error("Belum ada file model di folder `models/`. Letakkan `model_random_forest.joblib` di sana.")
        return

    with st.container(border=True):
        nama_model = "Random Forest"
        st.markdown("**Model yang digunakan:** Random Forest")
        c2, c3 = st.columns([1.3, 1])
        stasiun = c2.selectbox("Stasiun", STASIUN)
        g = df[df["stasiun"] == stasiun]
        tmin, tmax = g["tanggal"].min().date(), g["tanggal"].max().date()
        tanggal = c3.date_input("Tanggal hari ini (H)", value=tmax, min_value=tmin, max_value=tmax + timedelta(days=3650))
        mode = st.radio("Sumber data", ["Data historis", "Input manual"], horizontal=True,
                        help="Historis: nilai diambil otomatis dari data bersih. Manual: ubah nilai 7 hari terakhir sendiri.")

    bundle, is_demo = model(nama_model)
    if bundle is None:
        st.error(f"File model {ispu.MODEL_FILES[nama_model]} belum ada di folder models/.")
        return
    if is_demo:
        st.warning("**Model demo.** File `model_random_forest.joblib` yang asli belum dipasang, jadi hasil di bawah berasal dari model pengganti. Salin file asli ke folder `models/`.", icon="⚠️")

    t = pd.Timestamp(tanggal)
    riw = g[g["tanggal"] <= t]
    aktual_h = g[g["tanggal"] == t]

    if mode == "Data historis":
        if aktual_h.empty:
            st.info("Tidak ada pengukuran pada tanggal ini untuk stasiun tersebut. Pilih tanggal lain, atau pakai **Input manual**.")
            return
        hist = riw[["tanggal"] + POLUTAN]
        kat_hari_ini = aktual_h["kategori"].iloc[0]
    else:
        st.markdown("**Nilai sub-indeks 7 hari terakhir** (baris paling bawah = hari ini). Ubah langsung di tabel.")
        hari = pd.date_range(t - timedelta(days=6), t)
        awal = g.set_index("tanggal").reindex(hari)[POLUTAN]
        awal = awal.fillna(pd.Series(MEDIAN)).round(0)
        awal.index = [tgl(d) for d in hari]
        edit = st.data_editor(awal, width="stretch", num_rows="fixed",
                              column_config={p: st.column_config.NumberColumn(NAMA_POLUTAN[p], min_value=0, max_value=500, step=1) for p in POLUTAN})
        hist = edit.copy()
        hist.insert(0, "tanggal", hari)
        kat_hari_ini = ispu.kategori_dari_nilai(float(edit.iloc[-1].max()))

    try:
        X, diisi = ispu.bangun_fitur(hist, t, stasiun, bundle["fitur"], STASIUN, MEDIAN)
    except ispu.FiturTidakDikenal as e:
        st.error("Nama fitur di file model belum dikenali oleh aplikasi:\n\n`" + "`, `".join(e.names[:12]) + "`\n\nJalankan `python cek_model.py` untuk detailnya.")
        return
    proba = ispu.prediksi_proba(bundle, X)
    pred = max(proba, key=proba.get)

    st.markdown("")
    kiri, kanan = st.columns([1, 1.15], gap="large")
    with kiri:
        st.markdown(
            f"""<div class="hasil" style="background:linear-gradient(135deg,{WARNA[pred]},{WARNA[pred]}dd);color:{TEKS_DI_ATAS[pred]}">
<div class="label">Prediksi {tgl(t + timedelta(days=1))}</div>
<div class="nilai">{pred}</div>
<div style="font-weight:600">Keyakinan model {proba[pred]*100:.0f}%</div></div>""",
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="kartu"><b>Hari ini ({tgl(t)}):</b> {pil(kat_hari_ini)}{"" if mode == "Data historis" else " <span class=kecil>(perkiraan dari 5 polutan)</span>"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kartu dark"><b>Saran</b><br>{SARAN[pred]}</div>', unsafe_allow_html=True)
        if mode == "Data historis":
            besok = g[g["tanggal"] == t + timedelta(days=1)]
            if not besok.empty:
                nyata = besok["kategori"].iloc[0]
                ok = "✅ tepat" if nyata == pred else "❌ meleset"
                st.markdown(f'<div class="kartu"><b>Kenyataan H+1:</b> {pil(nyata)} &nbsp; {ok}</div>', unsafe_allow_html=True)
        if diisi:
            st.caption(f"ℹ️ {diisi} nilai riwayat yang kosong diisi otomatis (nilai terdekat/median stasiun).")
    with kanan:
        with st.container(border=True):
            fig = go.Figure(go.Bar(
                x=[proba[k] * 100 for k in KELAS], y=KELAS, orientation="h",
                marker=dict(color=[WARNA[k] for k in KELAS], cornerradius=8),
                text=[f"{proba[k]*100:.1f}%" for k in KELAS], textposition="outside",
            ))
            layout_plot(fig, 220, title="Peluang tiap kategori", xaxis=dict(range=[0, 112], ticksuffix="%", showgrid=False), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, width="stretch")
            h7 = hist.tail(7).copy()
            h7["tanggal"] = pd.to_datetime(h7["tanggal"])
            fig2 = go.Figure()
            for p in POLUTAN:
                fig2.add_trace(go.Scatter(x=h7["tanggal"], y=h7[p], name=NAMA_POLUTAN[p], mode="lines+markers"))
            layout_plot(fig2, 290, title="Riwayat 7 hari terakhir (sub-indeks ISPU)", legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig2, width="stretch")

    with st.expander("Fitur yang dimasukkan ke model"):
        st.dataframe(X.T.rename(columns={0: "nilai"}), width="stretch", height=300)
    st.caption("Catatan: akurasi model terbatas (lihat halaman Evaluasi Model). Hasil ini adalah alat bantu pembelajaran, bukan peringatan resmi kualitas udara.")


# ============================================================ EKSPLORASI DATA
def halaman_eksplorasi():
    kepala("Data", "Eksplorasi <span class='acc'>data.</span>", "Gambaran data bersih yang dipakai melatih dan menguji model.")
    kartu_stat([
        ("🗂️", "Jumlah baris", f"{len(df):,}".replace(",", "."), "setelah pembersihan", ""),
        ("📍", "Stasiun", df["stasiun"].nunique(), "SPKU DKI Jakarta", "lime"),
        ("📅", "Periode", f"{df['tanggal'].min().year}–{df['tanggal'].max().year}", "data harian", ""),
        ("🧪", "Polutan", "5", "sub-indeks ISPU", "dark"),
    ])
    l, r = st.columns([1, 1.5], gap="large")
    with l, st.container(border=True):
        dist = df["kategori"].value_counts().reindex(KELAS)
        fig = go.Figure(go.Pie(labels=dist.index, values=dist.values, hole=0.6, marker_colors=[WARNA[k] for k in dist.index], sort=False))
        layout_plot(fig, 320, title="Komposisi kategori")
        st.plotly_chart(fig, width="stretch")
        st.caption("Kategori SEDANG mendominasi (±68%), sehingga akurasi saja bisa menyesatkan.")
    with r, st.container(border=True):
        a, b = st.columns(2)
        pilih = a.selectbox("Stasiun", ["Semua stasiun"] + STASIUN)
        pol = b.selectbox("Polutan", POLUTAN, format_func=lambda p: NAMA_POLUTAN[p])
        x = df if pilih == "Semua stasiun" else df[df["stasiun"] == pilih]
        m = x.set_index("tanggal")[pol].resample("MS").mean().reset_index()
        fig = go.Figure(go.Scatter(x=m["tanggal"], y=m[pol], line=dict(color=INDIGO, width=2), fill="tozeroy", fillcolor="rgba(79,70,229,.08)"))
        layout_plot(fig, 300, title=f"Rata-rata bulanan {NAMA_POLUTAN[pol]}")
        st.plotly_chart(fig, width="stretch")

    with st.container(border=True):
        tb = pd.crosstab(df["stasiun"], df["kategori"])[KELAS]
        fig = go.Figure([go.Bar(name=k, x=tb.index, y=tb[k], marker_color=WARNA[k]) for k in KELAS])
        layout_plot(fig, 320, title="Kategori per stasiun", barmode="stack", legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, width="stretch")

    st.markdown("")
    kepala("Pembersihan", "Dari data mentah ke <span class='acc'>data bersih.</span>")
    rg = pd.read_excel(ispu.BASE / "data" / "data_bersih.xlsx", sheet_name="ringkasan")
    rg.columns = ["Langkah", "Keterangan", "Jumlah baris"]
    st.dataframe(rg, width="stretch", hide_index=True)


# ============================================================= EVALUASI MODEL
LAPORAN = {
    "Logistic Regression": {"BAIK": (0.18, 0.94, 0.30, 564), "SEDANG": (0.80, 0.44, 0.56, 3866), "TIDAK SEHAT": (0.00, 0.00, 0.00, 600)},
    "Decision Tree": {"BAIK": (0.18, 0.97, 0.30, 564), "SEDANG": (0.82, 0.41, 0.55, 3866), "TIDAK SEHAT": (0.31, 0.01, 0.01, 600)},
    "Random Forest": {"BAIK": (0.25, 0.84, 0.38, 564), "SEDANG": (0.80, 0.56, 0.66, 3866), "TIDAK SEHAT": (0.17, 0.11, 0.13, 600)},
}
OVERFIT = pd.DataFrame({"F1 macro latih": [0.6062, 0.6121, 0.8740], "F1 macro uji": [0.2896, 0.2863, 0.3903]},
                       index=["Logistic Regression", "Decision Tree", "Random Forest"])
OVERFIT["Selisih"] = (OVERFIT["F1 macro latih"] - OVERFIT["F1 macro uji"]).round(4)


def halaman_evaluasi():
    kepala("Evaluasi", "Seberapa baik <span class='acc'>modelnya?</span>",
           "Data latih 2010–Apr 2021 (17.464 baris) · data uji Apr 2021–Feb 2025 (5.030 baris) · validasi TimeSeriesSplit 5 lipatan, penilaian F1 macro.")
    t = PERB

    with st.container(border=True):
        metrik = st.multiselect("Metrik pada grafik", ["Accuracy", "F1 (macro)", "Recall TIDAK SEHAT"], default=["F1 (macro)", "Accuracy"])
        warna = {"Accuracy": "#b9c6f5", "F1 (macro)": INDIGO, "Recall TIDAK SEHAT": WARNA["TIDAK SEHAT"]}
        fig = go.Figure([go.Bar(name=m, x=t.index, y=t[m], marker=dict(color=warna[m], cornerradius=6), text=t[m].round(3), textposition="outside") for m in metrik])
        layout_plot(fig, 340, barmode="group", yaxis=dict(range=[0, 1]), legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, width="stretch")
        st.dataframe(t.round(4).astype(object).where(t.notna(), "–"), width="stretch")

    best = t.loc[["Baseline persistensi", "Random Forest"], "F1 (macro)"]
    st.markdown(
        f"""<div class="kartu dark" style="padding:22px 26px;border-radius:22px"><b>Temuan</b><br>
Random Forest memiliki F1 macro validasi tertinggi (0,6032), sehingga dipilih sebagai model utama. Pada data uji, F1 macro-nya {best['Random Forest']:.3f},
sedangkan baseline persistensi (besok dianggap sama dengan hari ini) mencapai {best['Baseline persistensi']:.3f}. Selisih besar antara skor latih dan uji
menunjukkan model belum menggeneralisasi dengan baik ke periode 2021–2025.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("")
    l, r = st.columns(2, gap="large")
    with l, st.container(border=True):
        st.subheader("Cek overfitting")
        st.dataframe(OVERFIT, width="stretch")
    with r, st.container(border=True):
        st.subheader("Laporan per kelas")
        nm = st.selectbox("Model", list(LAPORAN), index=2)
        rep = pd.DataFrame(LAPORAN[nm], index=["Precision", "Recall", "F1", "Support"]).T
        rep["Support"] = rep["Support"].astype(int)
        st.dataframe(rep, width="stretch")

    st.markdown("")
    kepala("Visual", "Gambar dari <span class='acc'>notebook.</span>")
    for f, cap in [("confusion_matrix_3_model.png", "Confusion matrix tiga model"), ("fitur_penting_pohon.png", "Fitur terpenting (Decision Tree dan Random Forest)")]:
        p = ispu.BASE / "assets" / f
        if p.exists():
            st.image(str(p), caption=cap, width="stretch")
        else:
            st.caption(f"Letakkan `{f}` di folder `assets/` untuk menampilkan: {cap}.")


# ================================================================== TENTANG
def halaman_tentang():
    kepala("Tentang proyek", "Peringatan dini, <span class='acc'>satu hari lebih awal.</span>",
           "Kajian terdahulu umumnya mengklasifikasikan kondisi udara pada hari yang sama. Proyek ini memprediksi kategori hari berikutnya agar bisa dipakai sebagai peringatan dini.")
    kartu_stat([
        ("1", "Hari ini", "Polutan", "PM10, SO₂, CO, O₃, NO₂ per stasiun", ""),
        ("2", "Pengolahan", "Fitur", "Riwayat 7 hari, rata-rata 3 dan 7 hari, bulan, musim, hari", "lime"),
        ("3", "Model ML", "3 model", "Logistic Regression, Random Forest, Decision Tree", ""),
        ("4", "Hasil H+1", "Kategori", "Kategori ISPU besok dan peluang tiap kelas", "dark"),
    ])
    with st.container(border=True):
        st.markdown(
            """
**Data.** Air Quality Index in Jakarta (Kaggle, salinan Satu Data Jakarta): lima stasiun SPKU, 2010–2025. Kelas *sangat tidak sehat* dan *berbahaya* digabung ke *tidak sehat*, sehingga target menjadi tiga kelas: BAIK, SEDANG, TIDAK SEHAT. Baris yang labelnya bertentangan dengan nilai maksimum, serta kolom `max` dan `critical`, dibuang untuk mencegah kebocoran target.

**Evaluasi.** Dua baseline (persistensi dan kelas mayoritas), F1 macro sebagai metrik utama, pembagian latih/uji berdasarkan waktu.

**Tim.** Yuwandri Alfarizi (J0404241010) · Adnan Muhammad G. K. (J0404241098) · Nayla Januarisa Prihadi (J0404241149) — Kelompok 6, Kelas A.
"""
        )


{"Prediksi": halaman_prediksi, "Data": halaman_eksplorasi, "Evaluasi": halaman_evaluasi, "Tentang": halaman_tentang}[halaman]()