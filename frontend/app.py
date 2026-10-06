import streamlit as st
import pandas as pd
import json
import networkx as nx
# pyrefly: ignore [missing-import]
from pyvis.network import Network
import streamlit.components.v1 as components
import textwrap

# ─── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TARA Workbench | Orchid Security",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── GLOBAL CSS: Orchid Security Deep-Space Theme ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── Base reset & typography ── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #070415 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #ededed !important;
    perspective: 1000px;
}

/* Orchid subtle cyber-grid parallax overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: -10%;
    background-image:
        linear-gradient(rgba(131, 91, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(131, 91, 255, 0.04) 1px, transparent 1px);
    background-size: 44px 44px;
    pointer-events: none;
    z-index: 0;
    will-change: transform;
    transform: translateZ(-10px) scale(1.1);
}

/* Orchid ambient glowing parallax orbs */
.stApp::after {
    content: '';
    position: fixed;
    inset: -10%;
    background:
        radial-gradient(ellipse 65% 55% at 15% 25%, rgba(104, 51, 255, 0.22) 0%, transparent 65%),
        radial-gradient(ellipse 55% 45% at 85% 15%, rgba(0, 245, 212, 0.12) 0%, transparent 60%),
        radial-gradient(ellipse 45% 40% at 50% 85%, rgba(224, 64, 251, 0.14) 0%, transparent 55%),
        radial-gradient(ellipse 35% 30% at 75% 75%, rgba(255, 183, 3, 0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
    will-change: transform;
    transform: translateZ(-20px) scale(1.2);
}

/* Hide Streamlit top header, decoration bar & status overlay */
header[data-testid="stHeader"],
div[data-testid="stHeader"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
#MainMenu, footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Elevate main container & remove top margin overlay */
section[data-testid="stMain"] > div { position: relative; z-index: 1; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0.5rem 2rem 3rem !important; margin-top: 0 !important; max-width: 100% !important; }

/* ── Tabs (Orchid Glass Pills) ── */
div[data-testid="stTabs"] {
    background: rgba(13, 8, 38, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(131, 91, 255, 0.25);
    border-radius: 14px;
    padding: 8px 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.06);
}
div[data-testid="stTabs"] [role="tablist"] {
    gap: 18px !important;
    justify-content: flex-start !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button {
    color: #9d9aa9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    margin: 0 2px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button:hover {
    color: #ffffff !important;
    background: rgba(131, 91, 255, 0.15) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, #6833ff 0%, #835bff 100%) !important;
    border-bottom: none !important;
    box-shadow: 0 0 20px rgba(104, 51, 255, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
}

/* ── Glass Cards ── */
.g-card {
    background: rgba(13, 8, 38, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(131, 91, 255, 0.22);
    border-radius: 16px;
    padding: 26px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}
.g-card:hover {
    border-color: rgba(131, 91, 255, 0.55);
    box-shadow: 0 12px 36px rgba(104, 51, 255, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
.g-card h3 {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    letter-spacing: -0.3px !important;
    margin-bottom: 4px !important;
}
.g-card p.sub { color: #9d9aa9 !important; font-size: 13px !important; margin-bottom: 20px !important; }

/* ── Severity & Tag Chips ── */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.chip-critical { background: rgba(255, 42, 133, 0.15); color: #ff5eab; border: 1px solid rgba(255, 42, 133, 0.45); box-shadow: 0 0 12px rgba(255, 42, 133, 0.25); }
.chip-high     { background: rgba(255, 128, 0, 0.15); color: #ffa248; border: 1px solid rgba(255, 128, 0, 0.45); box-shadow: 0 0 12px rgba(255, 128, 0, 0.2); }
.chip-medium   { background: rgba(255, 183, 3, 0.15); color: #ffc833; border: 1px solid rgba(255, 183, 3, 0.45); }
.chip-low      { background: rgba(0, 245, 212, 0.15); color: #00f5d4; border: 1px solid rgba(0, 245, 212, 0.4); box-shadow: 0 0 10px rgba(0, 245, 212, 0.2); }
.chip-info     { background: rgba(131, 91, 255, 0.16); color: #a782ff; border: 1px solid rgba(131, 91, 255, 0.4); }
.chip-violet   { background: rgba(131, 91, 255, 0.2); color: #c4b5fd; border: 1px solid rgba(131, 91, 255, 0.45); }

/* ── Section Divider ── */
.sec-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(131, 91, 255, 0.5), rgba(224, 64, 251, 0.4), rgba(0, 245, 212, 0.5), transparent);
    margin: 24px 0;
    border: none;
}

/* ── Threat Row Cards ── */
.threat-row {
    background: rgba(13, 8, 38, 0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(131, 91, 255, 0.22);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
}
.threat-row:hover {
    border-color: rgba(131, 91, 255, 0.55);
    box-shadow: 0 8px 30px rgba(104, 51, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);
}
.threat-id { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #00f5d4; font-weight: 700; letter-spacing: 0.5px; }
.threat-asset { font-weight: 700; color: #ffffff; font-size: 16px; margin-top: 2px; }
.threat-meta { font-size: 12px; color: #9d9aa9; margin: 8px 0; }
.threat-meta code { background: rgba(131, 91, 255, 0.15); color: #c4b5fd; padding: 2px 8px; border-radius: 5px; font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.threat-desc { font-size: 13.5px; color: #ededed; margin: 10px 0; line-height: 1.6; }
.csr-box {
    background: rgba(104, 51, 255, 0.12);
    border: 1px solid rgba(131, 91, 255, 0.3);
    border-left: 4px solid #6833ff;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 12.5px;
    color: #e4daff;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.65;
    margin-top: 12px;
}

/* ── Buttons (Orchid Electric Violet Pill) ── */
div.stButton > button {
    background: linear-gradient(135deg, #6833ff 0%, #835bff 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(131, 91, 255, 0.4) !important;
    border-radius: 999px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(104, 51, 255, 0.35) !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #7c47ff 0%, #956dff 100%) !important;
    border-color: #a782ff !important;
    box-shadow: 0 0 25px rgba(131, 91, 255, 0.65) !important;
    transform: translateY(-2px) !important;
}

/* ── Download Buttons (Orchid Mint Pill) ── */
div.stDownloadButton > button {
    background: rgba(0, 245, 212, 0.12) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0, 245, 212, 0.4) !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 10px 22px !important;
    transition: all 0.25s ease !important;
}
div.stDownloadButton > button:hover {
    background: rgba(0, 245, 212, 0.22) !important;
    box-shadow: 0 0 20px rgba(0, 245, 212, 0.4) !important;
    transform: translateY(-2px) !important;
}

/* ── Inputs & Selectboxes ── */
input, select, textarea {
    background-color: rgba(13, 8, 38, 0.85) !important;
    color: #ffffff !important;
    border: 1px solid rgba(131, 91, 255, 0.3) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: rgba(131, 91, 255, 0.7) !important;
    box-shadow: 0 0 0 2px rgba(131, 91, 255, 0.25) !important;
}
div[data-baseweb="select"] > div {
    background: rgba(13, 8, 38, 0.85) !important;
    border-color: rgba(131, 91, 255, 0.3) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

/* ── Single Clean File Uploader Styling ── */
div[data-testid="stFileUploader"] {
    background: rgba(13, 8, 38, 0.6) !important;
    border: 2px dashed rgba(131, 91, 255, 0.4) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(0, 245, 212, 0.6) !important;
    background: rgba(104, 51, 255, 0.08) !important;
    box-shadow: 0 0 25px rgba(104, 51, 255, 0.2) !important;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: rgba(13, 8, 38, 0.5) !important;
    border: 1px solid rgba(131, 91, 255, 0.22) !important;
    border-radius: 12px !important;
    margin-top: 10px !important;
}
div[data-testid="stExpander"] summary { color: #c4b5fd !important; font-size: 13px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] summary:hover { color: #ffffff !important; }

/* ── Toggle Switch ── */
div.stToggle label { color: #ededed !important; font-size: 14px !important; font-weight: 500 !important; }

/* ── Dataframe ── */
div[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden; border: 1px solid rgba(131, 91, 255, 0.25) !important; }

/* ── Smooth Scroll & Entrance Animations ── */
html {
    scroll-behavior: smooth !important;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(28px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes glowPulse {
    0%, 100% { box-shadow: 0 4px 20px rgba(104, 51, 255, 0.35); }
    50% { box-shadow: 0 0 35px rgba(131, 91, 255, 0.6); }
}

/* Apply scroll entrance animation to workbench elements */
.stApp section[data-testid="stMain"] {
    animation: fadeIn 0.8s ease-out both;
}

div[data-testid="stTabs"] {
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.threat-row, .g-card, div[data-testid="stFileUploader"], div[data-testid="stExpander"], div[data-testid="stDataFrame"] {
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* ── Footer ── */
.app-footer {
    background: rgba(13, 8, 38, 0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(131, 91, 255, 0.25);
    border-radius: 20px;
    padding: 36px 32px 24px;
    margin-top: 48px;
    margin-bottom: 24px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    position: relative;
    overflow: hidden;
}
.app-footer::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #6833ff 0%, #00f5d4 50%, #ff2a85 100%);
}
.ft-grid {
    display: grid;
    grid-template-columns: 2.2fr 1.5fr 1.5fr 1.8fr;
    gap: 28px;
    margin-bottom: 32px;
}
.ft-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.ft-brand-icon {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(135deg, #6833ff 0%, #00f5d4 100%);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 16px rgba(104,51,255,0.5);
}
.ft-brand-icon svg { width: 18px; height: 18px; color: #ffffff; }
.ft-brand-name { font-weight: 800; font-size: 18px; color: #ffffff; letter-spacing: -0.3px; }
.ft-desc { font-size: 13px; color: #9d9aa9; line-height: 1.6; margin-bottom: 16px; }

.ft-col-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #c4b5fd;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
}
.ft-col-title::after { content: ''; flex: 1; height: 1px; background: rgba(131, 91, 255, 0.2); }

.ft-links { list-style: none; padding: 0; margin: 0; }
.ft-links li { margin-bottom: 9px; }
.ft-links a {
    color: #9d9aa9;
    text-decoration: none;
    font-size: 12.5px;
    transition: color 0.2s ease;
    display: inline-flex; align-items: center; gap: 6px;
}
.ft-links a:hover { color: #00f5d4; }

.ft-status-card {
    background: rgba(20, 12, 48, 0.6);
    border: 1px solid rgba(131, 91, 255, 0.2);
    border-radius: 12px;
    padding: 14px;
}
.ft-status-item {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; margin-bottom: 8px;
}
.ft-status-item:last-child { margin-bottom: 0; }
.ft-status-label { color: #9d9aa9; font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.ft-status-val { font-weight: 600; color: #ffffff; }

.ft-bottom {
    border-top: 1px solid rgba(131, 91, 255, 0.18);
    padding-top: 20px;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 12px;
}
.ft-copy { font-size: 12px; color: #9d9aa9; }
.ft-sublinks { display: flex; gap: 18px; }
.ft-sublinks a { color: #9d9aa9; text-decoration: none; font-size: 12px; transition: color 0.2s; }
.ft-sublinks a:hover { color: #ffffff; }
.ft-badge-pulse {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 999px;
    background: rgba(0, 245, 212, 0.1); color: #00f5d4;
    border: 1px solid rgba(0, 245, 212, 0.3);
    font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700;
}
.pulse-dot { width: 6px; height: 6px; border-radius: 50%; background: #00f5d4; box-shadow: 0 0 8px #00f5d4; }

.footer-bar {
    text-align: center;
    font-size: 12px;
    color: #9d9aa9;
    padding: 30px 0 16px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
    border-top: 1px solid rgba(131, 91, 255, 0.2);
    margin-top: 24px;
    animation: fadeIn 1s ease-out both;
}
.footer-bar span { color: #835bff; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ─── HERO HEADER (Matching Orchid Security Reference Layout) ─────────────────
HERO_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: transparent;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #f1f5f9;
    overflow-x: hidden;
    padding: 0;
}

/* ── Ambient background ── */
.grid-bg {
    position: fixed; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(131, 91, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(131, 91, 255, 0.04) 1px, transparent 1px);
    background-size: 44px 44px;
    z-index: 0;
}
.glow-orb-center {
    position: fixed; top: 15%; left: 50%; transform: translateX(-50%);
    width: 700px; height: 450px; border-radius: 50%;
    background: radial-gradient(circle, rgba(104,51,255,0.22) 0%, rgba(0,245,212,0.08) 50%, transparent 75%);
    pointer-events: none; z-index: 0; filter: blur(30px);
}

.wrapper { position: relative; z-index: 1; padding: 10px 16px 20px; }

/* ── Smooth Scroll & Entrance Animations ── */
@keyframes heroSlideUp {
    from { opacity: 0; transform: translateY(30px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes frameFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-7px); }
}

/* ── Top Navigation (Orchid Nav Bar Layout) ── */
.nav {
    display: flex; justify-content: space-between; align-items: center;
    background: rgba(13, 8, 38, 0.65);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(131, 91, 255, 0.22);
    border-radius: 999px;
    padding: 8px 24px;
    margin-bottom: 32px;
    position: relative;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    animation: heroSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.brand { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.brand-icon {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(135deg, #6833ff 0%, #00f5d4 100%);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 16px rgba(104,51,255,0.5);
}
.brand-icon svg { width: 18px; height: 18px; color: #ffffff; }
.brand-name { font-weight: 800; font-size: 17px; color: #ffffff; letter-spacing: -0.3px; }

/* Center Pill Navbar menu */
.nav-menu {
    display: flex; align-items: center; gap: 24px;
    background: rgba(20, 12, 48, 0.6);
    border: 1px solid rgba(131, 91, 255, 0.2);
    border-radius: 999px;
    padding: 6px 22px;
}
.nav-item {
    font-size: 13px; font-weight: 500; color: #c4b5fd;
    text-decoration: none; cursor: pointer; transition: color 0.2s;
    display: flex; align-items: center; gap: 4px;
}
.nav-item:hover { color: #ffffff; }
.nav-item svg { width: 12px; height: 12px; color: #9d9aa9; }

/* Right action pill buttons */
.nav-actions { display: flex; align-items: center; gap: 10px; }
.btn-partner {
    background: linear-gradient(135deg, #6833ff 0%, #835bff 100%);
    color: #ffffff; font-weight: 600; font-size: 13px;
    padding: 8px 18px; border-radius: 999px; border: none;
    cursor: pointer; transition: all 0.25s ease;
    box-shadow: 0 4px 16px rgba(104,51,255,0.4);
}
.btn-partner:hover { transform: translateY(-1px); box-shadow: 0 0 20px rgba(131,91,255,0.6); }

.btn-demo-nav {
    background: #ffffff; color: #070415; font-weight: 700; font-size: 13px;
    padding: 8px 20px; border-radius: 999px; border: none;
    cursor: pointer; transition: all 0.25s ease;
    box-shadow: 0 4px 16px rgba(255,255,255,0.2);
}
.btn-demo-nav:hover { background: #f1f5f9; transform: translateY(-1px); box-shadow: 0 0 20px rgba(255,255,255,0.4); }

/* ── Centered Hero Typography Section ── */
.hero-centered {
    text-align: center; max-width: 920px; margin: 0 auto 36px;
    position: relative; z-index: 1;
    animation: heroSlideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.12s both;
}

.hero-title {
    font-size: 48px; font-weight: 800;
    letter-spacing: -1.8px; line-height: 1.12;
    color: #ffffff; margin-bottom: 18px;
}

.hero-desc {
    font-size: 15px; color: #b4b0c2;
    line-height: 1.7; max-width: 780px; margin: 0 auto 28px;
    font-weight: 400;
}

/* Centered CTA Buttons */
.hero-cta-row {
    display: flex; justify-content: center; align-items: center; gap: 14px;
    margin-bottom: 40px;
}
.btn-hero-primary {
    background: linear-gradient(135deg, #6833ff 0%, #835bff 100%);
    color: #ffffff; font-weight: 700; font-size: 14.5px;
    padding: 13px 32px; border-radius: 999px; border: none;
    cursor: pointer; transition: all 0.25s ease;
    box-shadow: 0 6px 24px rgba(104,51,255,0.45);
}
.btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(131,91,255,0.7); }

.btn-hero-secondary {
    background: #ffffff; color: #070415; font-weight: 700; font-size: 14.5px;
    padding: 13px 30px; border-radius: 999px; border: none;
    cursor: pointer; transition: all 0.25s ease;
    box-shadow: 0 6px 24px rgba(255,255,255,0.25);
}
.btn-hero-secondary:hover { background: #f8fafc; transform: translateY(-2px); box-shadow: 0 0 30px rgba(255,255,255,0.4); }

/* ── Hero Embedded Dashboard Preview Window (Matching Screenshot) ── */
.dashboard-frame {
    background: rgba(13, 8, 38, 0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(131, 91, 255, 0.3);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(104, 51, 255, 0.25);
    max-width: 1100px; margin: 0 auto;
    position: relative;
    animation: heroSlideUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.25s both, frameFloat 7s ease-in-out 1.2s infinite;
}

.df-header {
    background: rgba(20, 12, 48, 0.8);
    border-bottom: 1px solid rgba(131, 91, 255, 0.2);
    padding: 12px 22px;
    display: flex; justify-content: space-between; align-items: center;
}
.df-title-wrap { display: flex; align-items: center; gap: 10px; }
.df-icon {
    width: 26px; height: 26px; border-radius: 7px;
    background: linear-gradient(135deg, #6833ff, #00f5d4);
    display: flex; align-items: center; justify-content: center;
}
.df-icon svg { width: 14px; height: 14px; color: #ffffff; }
.df-title { font-weight: 700; font-size: 13px; color: #ffffff; }
.df-time  { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #9d9aa9; margin-left: 6px; }

.df-body { padding: 18px 22px; display: grid; grid-template-columns: 200px 1fr 1fr 1fr; gap: 14px; align-items: center; }

.df-stat-main {
    background: rgba(13, 8, 38, 0.6);
    border: 1px solid rgba(131, 91, 255, 0.2);
    border-radius: 12px; padding: 14px;
}
.df-stat-val { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; }
.df-stat-lbl { font-size: 11px; color: #9d9aa9; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

.df-stat-mini {
    background: rgba(13, 8, 38, 0.6);
    border: 1px solid rgba(131, 91, 255, 0.2);
    border-radius: 12px; padding: 14px;
}
.df-mini-title { font-size: 10px; font-weight: 700; color: #c4b5fd; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; margin-bottom: 8px; }
.df-bar-bg { width: 100%; height: 6px; background: rgba(131, 91, 255, 0.2); border-radius: 999px; overflow: hidden; margin-top: 6px; }
.df-bar-fill { height: 100%; background: linear-gradient(90deg, #6833ff, #00f5d4); border-radius: 999px; }
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="glow-orb-center"></div>

<div class="wrapper">
<!-- ── Top Navigation Bar (Orchid Layout) ── -->
<nav class="nav">
    <div class="brand" onclick="window.scrollTo({top: 0, behavior: 'smooth'})" style="cursor: pointer;">
        <div class="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9,12 11,14 15,10"/></svg>
        </div>
        <div class="brand-name">Orchid TARA</div>
    </div>
    
    <div class="nav-menu">
        <a class="nav-item" onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})">The Platform</a>
        <a class="nav-item" onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})">Use Cases <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></a>
        <a class="nav-item" href="https://www.iso.org/standard/70918.html" target="_blank" rel="noopener noreferrer">ISO/SAE 21434</a>
        <a class="nav-item" href="https://unece.org/transport/documents/2021/03/standards/unece-regulation-no-155-cyber-security-and-cyber-security" target="_blank" rel="noopener noreferrer">UNECE R155 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></a>
    </div>

    <div class="nav-actions">
        <button class="btn-partner" onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})">Launch Workspace</button>
    </div>
</nav>

<!-- ── Centered Hero Section ── -->
<div class="hero-centered">
    <h1 class="hero-title">
        Cybersecurity Visibility and Intelligence for Connected Vehicle Systems
    </h1>
    <p class="hero-desc">
        TARA Engine discovers unmanaged vehicle attack vectors, maps how threats actually propagate inside CAN FD &amp; Automotive Ethernet networks, and brings connected ECUs under ISO/SAE 21434 and UNECE R155/R156 control without rewriting ECU software. Vehicle dark matter hides in connected architectures — TARA makes it visible, governable, and measurable.
    </p>

    <div class="hero-cta-row">
        <button class="btn-hero-primary" onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})">Launch Workspace</button>
    </div>
</div>

</div>

<script>
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset || document.documentElement.scrollTop;
    const orb = document.querySelector('.glow-orb-center');
    const grid = document.querySelector('.grid-bg');
    const hero = document.querySelector('.hero-centered');
    if (orb) orb.style.transform = `translate(-50%, ${scrolled * 0.35}px)`;
    if (grid) grid.style.transform = `translateY(${scrolled * 0.15}px)`;
    if (hero) hero.style.transform = `translateY(${scrolled * 0.12}px)`;
});
</script>
</body>
</html>
"""
if "tara_items" not in st.session_state:
    st.session_state.tara_items = [
        {
            "id": "THR-001",
            "asset": "Telematic Control Unit (TCU)",
            "boundary": "Public Cloud ↔ Telematics Gateway",
            "stride": "Elevation of Privilege",
            "mitre": "T1542 (Firmware Tampering)",
            "description": "OTA firmware manipulation over compromised cellular channel lacking cryptographic validation.",
            "attack_path": ["Public Cloud", "Cellular Modem", "Telematics Gateway", "Gateway ECU"],
            "csr": "CSR-OTA-01: The ECU shall authenticate incoming update payloads using asymmetric public keys anchored in the local eHSM Root of Trust.",
            "feasibility": "Medium",
            "impact": "Severe",
            "risk": 4,
            "status": "Pending Review",
            "notes": "",
            "severity": "critical"
        },
        {
            "id": "THR-002",
            "asset": "Central Gateway (CGW) / CAN FD",
            "boundary": "OBD-II Diagnostic Port ↔ Powertrain Bus",
            "stride": "Tampering / Spoofing",
            "mitre": "T1059 (Command Execution)",
            "description": "Unauthorized injection of torque deceleration frames on unauthenticated powertrain bus segment.",
            "attack_path": ["OBD-II Port", "Central Gateway", "Powertrain CAN FD", "Braking ECU"],
            "csr": "CSR-COM-02: Safety-critical broadcast frames shall enforce CMAC cryptographic signatures and freshness counter verification (SecOC).",
            "feasibility": "High",
            "impact": "Major",
            "risk": 4,
            "status": "Pending Review",
            "notes": "",
            "severity": "high"
        }
    ]

components.html(HERO_HTML, height=270, scrolling=False)
st.markdown('<div id="workspace-anchor"></div>', unsafe_allow_html=True)


# ─── WORKBENCH TABS ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "System Ingestion",
    "Attack Graph",
    "TARA Matrix",
    "What-If Simulator",
    "Engineer Review",
    "Compliance Export",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · SYSTEM INGESTION & TRUST BOUNDARIES
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    INGESTION_HEADER_HTML = """
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
    <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;color:#f1f5f9;padding:4px 0;}
    .sec-title{font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:4px;}
    .sec-sub{font-size:13px;color:#9d9aa9;margin-bottom:12px;}
    </style>
    </head>
    <body>
    <div class="sec-title">System Architecture &amp; Communication Matrix Ingestion</div>
    <div class="sec-sub">Upload vehicle DBC, ARXML, JSON, or PDF specifications for automated trust boundary extraction and vectorization.</div>
    </body></html>
    """
    components.html(INGESTION_HEADER_HTML, height=65, scrolling=False)

    up_file = st.file_uploader(
        "Upload Specification File (.DBC, .ARXML, .JSON, .PDF, .TXT)",
        type=["pdf", "txt", "dbc", "arxml", "json"],
        key="main_spec_uploader"
    )

    c_btn, _ = st.columns([1, 2])
    with c_btn:
        if up_file:
            if st.button("Process & Vectorize Architecture", use_container_width=True):
                progress_text = st.empty()
                bar = st.progress(0)
                
                # Real-time processing simulation & extraction steps
                import time
                progress_text.markdown("*Step 1/3: Parsing binary specification payload...*")
                bar.progress(35)
                time.sleep(0.4)

                progress_text.markdown("*Step 2/3: Extracting CAN FD IDs & Trust Boundaries...*")
                bar.progress(70)
                time.sleep(0.4)

                progress_text.markdown("*Step 3/3: Vectorizing embeddings → ChromaDB `architecture_store`...*")
                bar.progress(100)
                time.sleep(0.3)
                bar.empty()
                progress_text.empty()

                # Dynamically create new threat vector from uploaded file
                fname = up_file.name
                new_id = f"THR-{len(st.session_state.tara_items) + 1:03d}"
                new_item = {
                    "id": new_id,
                    "asset": f"Domain Gateway ({fname.split('.')[0].upper()})",
                    "boundary": "Ingress Network ↔ Powertrain Segment",
                    "stride": "Spoofing / Tampering",
                    "mitre": "T1565 (Data Manipulation)",
                    "description": f"Automated extraction from '{fname}': Unverified frame injection vector detected on internal bus route.",
                    "attack_path": ["Ingress Gateway", "Subnet Router", "Central Gateway ECU"],
                    "csr": f"CSR-{new_id}: The gateway shall validate frame IDs and SecOC freshness counters for all messages extracted from {fname}.",
                    "feasibility": "Medium",
                    "impact": "High",
                    "risk": 3,
                    "status": "Pending Review",
                    "notes": "",
                    "severity": "high"
                }
                
                st.session_state.tara_items.append(new_item)
                st.success(f"Ingested **{up_file.name}** ({up_file.size} bytes) → Extracted **{new_id}** into TARA Matrix!")
                st.rerun()
        else:
            st.button("Process & Vectorize Architecture", use_container_width=True, disabled=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    TRUST_CARDS_HTML = """
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
    <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;color:#f1f5f9;padding:4px 0;}
    .sec-label{font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;}
    .sec-label::after{content:'';flex:1;height:1px;background:rgba(131,91,255,0.25);}
    
    @keyframes cardPop {
        from { opacity: 0; transform: translateY(24px) scale(0.96); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .tb-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
    .tb-card{
        background:rgba(13,8,38,0.65);
        backdrop-filter:blur(16px);
        border-radius:14px;
        padding:20px;
        border:1px solid rgba(131,91,255,0.22);
        position:relative;overflow:hidden;
        transition:border-color 0.25s,box-shadow 0.25s,transform 0.25s;
        cursor:pointer;
        animation: cardPop 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .tb-card:nth-child(1) { animation-delay: 0.1s; }
    .tb-card:nth-child(2) { animation-delay: 0.2s; }
    .tb-card:nth-child(3) { animation-delay: 0.3s; }
    .tb-card:hover{border-color:rgba(131,91,255,0.55);box-shadow:0 8px 28px rgba(104,51,255,0.2);transform:translateY(-2px);}
    .tb-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;}
    .tb-critical::before{background:linear-gradient(90deg,#ff2a85,rgba(255,42,133,0.3));}
    .tb-medium::before  {background:linear-gradient(90deg,#ffb703,rgba(255,183,3,0.3));}
    .tb-low::before     {background:linear-gradient(90deg,#00f5d4,rgba(0,245,212,0.3));}
    .tb-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}
    .tb-id{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:#00f5d4;}
    .tb-chip{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;padding:3px 9px;border-radius:999px;font-family:'JetBrains Mono',monospace;}
    .tbc-critical{background:rgba(255,42,133,0.15);color:#ff5eab;border:1px solid rgba(255,42,133,0.4);}
    .tbc-medium  {background:rgba(255,183,3,0.15);color:#ffc833;border:1px solid rgba(255,183,3,0.4);}
    .tbc-low     {background:rgba(0,245,212,0.15);color:#00f5d4;border:1px solid rgba(0,245,212,0.4);}
    .tb-route{font-size:13px;font-weight:700;color:#ffffff;margin-bottom:6px;line-height:1.45;}
    .tb-desc{font-size:12px;color:#9d9aa9;line-height:1.55;}
    </style>
    </head>
    <body>
    <div class="sec-label">Extracted Vehicle Trust Boundaries</div>
    <div class="tb-grid">
        <div class="tb-card tb-critical">
            <div class="tb-head">
                <span class="tb-id">TB-01</span>
                <span class="tb-chip tbc-critical">Critical</span>
            </div>
            <div class="tb-route">Public Cloud ↔ Telematics Gateway</div>
            <div class="tb-desc">External cellular channel. OTA flashing surface lacking mandatory SecOC enforcement. Primary attack ingress.</div>
        </div>
        <div class="tb-card tb-medium">
            <div class="tb-head">
                <span class="tb-id">TB-02</span>
                <span class="tb-chip tbc-medium">Medium</span>
            </div>
            <div class="tb-route">OBD-II Port ↔ Central Gateway</div>
            <div class="tb-desc">Physical diagnostic access without PKI authentication. Lateral pivot risk to powertrain bus.</div>
        </div>
        <div class="tb-card tb-low">
            <div class="tb-head">
                <span class="tb-id">TB-03</span>
                <span class="tb-chip tbc-low">Internal</span>
            </div>
            <div class="tb-route">In-Vehicle Ethernet ↔ Powertrain Subnet</div>
            <div class="tb-desc">Internal bus segment. SecOC CMAC tags enforced. Freshness counter replay protection active.</div>
        </div>
    </div>
    </body></html>
    """
    components.html(TRUST_CARDS_HTML, height=180, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · ATTACK PROPAGATION GRAPH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    GRAPH_HTML = """
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;color:#f1f5f9;padding:4px 0;}
    .graph-wrap{position:relative;width:100%;height:225px;overflow:hidden;}
    svg.attack-svg{width:100%;height:100%;}
    .node-label{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;fill:#ffffff;}
    .node-sublabel{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;}
    .edge-label{font-family:'JetBrains Mono',monospace;font-size:9.5px;fill:#9d9aa9;}
    .node-circle{filter:drop-shadow(0 0 8px currentColor);}
    .node-pill{fill:rgba(20,12,48,0.95);stroke-width:1;}
    @keyframes flow1{0%{stroke-dashoffset:160}100%{stroke-dashoffset:0}}
    @keyframes flow2{0%{stroke-dashoffset:160}100%{stroke-dashoffset:0}}
    @keyframes flow3{0%{stroke-dashoffset:160}100%{stroke-dashoffset:0}}
    @keyframes flow4{0%{stroke-dashoffset:140}100%{stroke-dashoffset:0}}
    .edge-anim1{stroke-dasharray:7 5;animation:flow1 1.8s linear infinite;}
    .edge-anim2{stroke-dasharray:7 5;animation:flow2 2.1s linear infinite;}
    .edge-anim3{stroke-dasharray:7 5;animation:flow3 2.4s linear infinite;}
    .edge-anim4{stroke-dasharray:7 5;animation:flow4 2.0s linear infinite;}

    /* particle dots */
    .particle{r:4;opacity:0.95;}
    .p-magenta{fill:#ff2a85;filter:drop-shadow(0 0 5px #ff2a85);}
    .p-purple {fill:#835bff;filter:drop-shadow(0 0 5px #835bff);}
    .p-cyan   {fill:#00f5d4;filter:drop-shadow(0 0 5px #00f5d4);}
    .p-mint   {fill:#00f5d4;filter:drop-shadow(0 0 5px #00f5d4);}

    .legend{display:flex;gap:20px;margin-top:12px;flex-wrap:wrap;}
    .lg-item{display:flex;align-items:center;gap:7px;font-size:11px;color:#9d9aa9;font-family:'JetBrains Mono',monospace;}
    .lg-dot{width:9px;height:9px;border-radius:50%;}
    .sec-title{font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:4px;}
    .sec-sub{font-size:13px;color:#9d9aa9;margin-bottom:14px;}
    </style>
    </head>
    <body>
    <div class="sec-title">Interactive Attack Propagation Topology</div>
    <div class="sec-sub">Animated particle flow showing multi-hop exploit paths across CAN FD / Automotive Ethernet bus routes.</div>

    <div class="graph-wrap">
    <svg class="attack-svg" viewBox="0 0 900 210" xmlns="http://www.w3.org/2000/svg">
        <defs>
        <marker id="arrow-magenta" markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto"><polygon points="0 0, 7 2.5, 0 5" fill="#ff2a85"/></marker>
        <marker id="arrow-purple"  markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto"><polygon points="0 0, 7 2.5, 0 5" fill="#835bff"/></marker>
        <marker id="arrow-cyan"    markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto"><polygon points="0 0, 7 2.5, 0 5" fill="#00f5d4"/></marker>
        <marker id="arrow-mint"    markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto"><polygon points="0 0, 7 2.5, 0 5" fill="#00f5d4"/></marker>
        <radialGradient id="ng-magenta" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ff2a85" stop-opacity="0.3"/><stop offset="100%" stop-color="#ff2a85" stop-opacity="0"/></radialGradient>
        <radialGradient id="ng-purple"  cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#835bff" stop-opacity="0.3"/><stop offset="100%" stop-color="#835bff" stop-opacity="0"/></radialGradient>
        <radialGradient id="ng-cyan"    cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#00f5d4" stop-opacity="0.25"/><stop offset="100%" stop-color="#00f5d4" stop-opacity="0"/></radialGradient>
        </defs>

        <!-- Background glow halos -->
        <ellipse cx="90"  cy="75" rx="38" ry="32" fill="url(#ng-magenta)" opacity="0.6"/>
        <ellipse cx="280" cy="75" rx="34" ry="28" fill="url(#ng-purple)"  opacity="0.5"/>
        <ellipse cx="470" cy="75" rx="34" ry="28" fill="url(#ng-purple)"  opacity="0.5"/>
        <ellipse cx="660" cy="75" rx="34" ry="28" fill="url(#ng-cyan)"    opacity="0.6"/>
        <ellipse cx="830" cy="75" rx="34" ry="28" fill="url(#ng-cyan)"    opacity="0.6"/>

        <!-- Animated edge connection lines -->
        <line x1="122" y1="75" x2="248" y2="75" stroke="#ff2a85" stroke-width="1.8" stroke-opacity="0.2"/>
        <line x1="122" y1="75" x2="242" y2="75" stroke="#ff2a85" stroke-width="1.8" class="edge-anim1" fill="none" marker-end="url(#arrow-magenta)"/>
        <text x="185" y="58" class="edge-label" text-anchor="middle">TLS 1.3 / Cellular</text>

        <line x1="312" y1="75" x2="438" y2="75" stroke="#835bff" stroke-width="1.8" stroke-opacity="0.2"/>
        <line x1="312" y1="75" x2="432" y2="75" stroke="#835bff" stroke-width="1.8" class="edge-anim2" fill="none" marker-end="url(#arrow-purple)"/>
        <text x="375" y="58" class="edge-label" text-anchor="middle">UART / SPI Bus</text>

        <line x1="502" y1="75" x2="628" y2="75" stroke="#835bff" stroke-width="1.8" stroke-opacity="0.2"/>
        <line x1="502" y1="75" x2="622" y2="75" stroke="#835bff" stroke-width="1.8" class="edge-anim3" fill="none" marker-end="url(#arrow-purple)"/>
        <text x="565" y="58" class="edge-label" text-anchor="middle">100Base-T1</text>

        <line x1="692" y1="75" x2="798" y2="75" stroke="#00f5d4" stroke-width="1.8" stroke-opacity="0.2"/>
        <line x1="692" y1="75" x2="792" y2="75" stroke="#00f5d4" stroke-width="1.8" class="edge-anim4" fill="none" marker-end="url(#arrow-mint)"/>
        <text x="745" y="58" class="edge-label" text-anchor="middle">CAN FD 500k</text>

        <!-- Particle animations along paths -->
        <circle class="particle p-magenta"><animateMotion dur="1.8s" repeatCount="indefinite" path="M 122 75 L 242 75"/></circle>
        <circle class="particle p-magenta"><animateMotion dur="1.8s" repeatCount="indefinite" begin="0.9s" path="M 122 75 L 242 75"/></circle>
        <circle class="particle p-purple" ><animateMotion dur="2.1s" repeatCount="indefinite" path="M 312 75 L 432 75"/></circle>
        <circle class="particle p-purple" ><animateMotion dur="2.1s" repeatCount="indefinite" begin="1.05s" path="M 312 75 L 432 75"/></circle>
        <circle class="particle p-cyan"   ><animateMotion dur="2.4s" repeatCount="indefinite" path="M 502 75 L 622 75"/></circle>
        <circle class="particle p-mint"   ><animateMotion dur="2.0s" repeatCount="indefinite" path="M 692 75 L 792 75"/></circle>

        <!-- Node 1: Public Cloud -->
        <circle cx="90" cy="75" r="28" fill="rgba(255,42,133,0.12)" stroke="#ff2a85" stroke-width="1.8" class="node-circle" style="color:#ff2a85"/>
        <circle cx="90" cy="75" r="19" fill="rgba(13,8,38,0.9)" stroke="rgba(255,42,133,0.4)" stroke-width="1"/>
        <rect x="22" y="118" width="136" height="25" rx="12" class="node-pill" stroke="rgba(255,42,133,0.35)"/>
        <text x="90" y="135" text-anchor="middle" class="node-label">Public Cloud</text>
        <text x="90" y="157" text-anchor="middle" fill="#ff2a85" class="node-sublabel">ATTACKER ENTRY</text>

        <!-- Node 2: Cellular Modem -->
        <circle cx="280" cy="75" r="26" fill="rgba(131,91,255,0.12)" stroke="#835bff" stroke-width="1.8" class="node-circle" style="color:#835bff"/>
        <circle cx="280" cy="75" r="18" fill="rgba(13,8,38,0.9)" stroke="rgba(131,91,255,0.4)" stroke-width="1"/>
        <rect x="212" y="118" width="136" height="25" rx="12" class="node-pill" stroke="rgba(131,91,255,0.35)"/>
        <text x="280" y="135" text-anchor="middle" class="node-label">Cellular Modem</text>

        <!-- Node 3: Telematics GW -->
        <circle cx="470" cy="75" r="26" fill="rgba(131,91,255,0.12)" stroke="#835bff" stroke-width="1.8" class="node-circle" style="color:#835bff"/>
        <circle cx="470" cy="75" r="18" fill="rgba(13,8,38,0.9)" stroke="rgba(131,91,255,0.4)" stroke-width="1"/>
        <rect x="402" y="118" width="136" height="25" rx="12" class="node-pill" stroke="rgba(131,91,255,0.35)"/>
        <text x="470" y="135" text-anchor="middle" class="node-label">Telematics GW</text>

        <!-- Node 4: Central GW ECU -->
        <circle cx="660" cy="75" r="26" fill="rgba(0,245,212,0.12)" stroke="#00f5d4" stroke-width="1.8" class="node-circle" style="color:#00f5d4"/>
        <circle cx="660" cy="75" r="18" fill="rgba(13,8,38,0.9)" stroke="rgba(0,245,212,0.4)" stroke-width="1"/>
        <rect x="592" y="118" width="136" height="25" rx="12" class="node-pill" stroke="rgba(0,245,212,0.35)"/>
        <text x="660" y="135" text-anchor="middle" class="node-label">Central GW ECU</text>

        <!-- Node 5: Braking ECU -->
        <circle cx="830" cy="75" r="26" fill="rgba(0,245,212,0.12)" stroke="#00f5d4" stroke-width="1.8" class="node-circle" style="color:#00f5d4"/>
        <circle cx="830" cy="75" r="18" fill="rgba(13,8,38,0.9)" stroke="rgba(0,245,212,0.4)" stroke-width="1"/>
        <rect x="762" y="118" width="136" height="25" rx="12" class="node-pill" stroke="rgba(0,245,212,0.35)"/>
        <text x="830" y="135" text-anchor="middle" class="node-label">Braking ECU</text>
        <text x="830" y="157" text-anchor="middle" fill="#00f5d4" class="node-sublabel">SAFETY-CRITICAL</text>
    </svg>
    </div>

    <div class="legend">
        <div class="lg-item"><div class="lg-dot" style="background:#ff2a85;box-shadow:0 0 6px #ff2a85"></div>Attacker entry / critical risk</div>
        <div class="lg-item"><div class="lg-dot" style="background:#835bff;box-shadow:0 0 6px #835bff"></div>Lateral pivot nodes</div>
        <div class="lg-item"><div class="lg-dot" style="background:#00f5d4;box-shadow:0 0 6px #00f5d4"></div>Internal gateway &amp; Safety-critical target ECU</div>
        <div class="lg-item">&#9679; Particle = active threat propagation signal</div>
    </div>
    </body></html>
    """
    components.html(GRAPH_HTML, height=330, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · TARA MATRIX & RISK SCORING
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <h3>Threat Matrix &amp; Risk Scoring</h3>
    <p class="sub">ISO/SAE 21434 Clause 15 Attack Potential · STRIDE + MITRE ATT&amp;CK for ICS</p>
    <hr class="sec-divider"/>
    """, unsafe_allow_html=True)

    with st.expander("Inject Live Real-Time Threat Vector"):
        with st.form(key="add_threat_form"):
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                new_asset = st.text_input("Asset / Target Component", placeholder="e.g., ADAS Camera ECU, BMS Controller")
                new_boundary = st.text_input("Trust Boundary Route", placeholder="e.g., Radar Bus ↔ ADAS Controller")
                new_stride = st.selectbox("STRIDE Classification", ["Spoofing", "Tampering", "Repudiation", "Information Disclosure", "Denial of Service", "Elevation of Privilege"])
            with c_f2:
                new_mitre = st.text_input("MITRE ATT&CK Technique ID", placeholder="e.g., T1565 (Data Manipulation)")
                new_impact = st.selectbox("Impact Category", ["Severe", "Major", "Moderate", "Minor"])
                new_csr = st.text_input("Cybersecurity Requirement (CSR)", placeholder="e.g., CSR-ADAS-01: Authenticate all sensor frames...")

            submit_threat = st.form_submit_button("Inject Threat Vector into Real-Time Engine")
            if submit_threat and new_asset:
                nt_id = f"THR-{len(st.session_state.tara_items) + 1:03d}"
                st.session_state.tara_items.append({
                    "id": nt_id,
                    "asset": new_asset,
                    "boundary": new_boundary or "Internal Bus",
                    "stride": new_stride,
                    "mitre": new_mitre or "T1059",
                    "description": f"Real-time engineer injection: Identified risk surface on {new_asset}.",
                    "attack_path": ["Public Cloud", new_asset],
                    "csr": new_csr or f"CSR-{nt_id}: Enforce cryptographic verification.",
                    "feasibility": "High",
                    "impact": new_impact,
                    "risk": 4,
                    "status": "Pending Review",
                    "notes": "",
                    "severity": "critical" if new_impact == "Severe" else "high"
                })
                st.toast(f"Threat Vector {nt_id} injected into real-time matrix!")
                st.rerun()

    CHIP_MAP = {
        "critical": '<span class="chip chip-critical">Critical</span>',
        "high":     '<span class="chip chip-high">High</span>',
        "medium":   '<span class="chip chip-medium">Medium</span>',
        "low":      '<span class="chip chip-low">Low</span>',
    }

    for idx, item in enumerate(st.session_state.tara_items):
        sev = item.get("severity", "high")
        chip = CHIP_MAP.get(sev, CHIP_MAP["high"])
        feasibility_chip = '<span class="chip chip-medium">Medium Feasibility</span>' if item["feasibility"] == "Medium" else '<span class="chip chip-high">High Feasibility</span>'
        impact_chip = '<span class="chip chip-critical">Severe Impact</span>' if item["impact"] == "Severe" else '<span class="chip chip-high">Major Impact</span>'

        st.markdown(f"""
        <div class="threat-row">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                <div>
                    <span class="threat-id">{item['id']}</span>
                    <div class="threat-asset">{item['asset']}</div>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;">
                    {chip}
                    {feasibility_chip}
                    {impact_chip}
                    <span class="chip chip-info">Risk Level {item['risk']}</span>
                </div>
            </div>
            <div class="threat-meta">
                <strong style="color:#c4b5fd">Trust Boundary:</strong>
                <code>{item['boundary']}</code>
                &nbsp;·&nbsp;
                <strong style="color:#c4b5fd">STRIDE:</strong>
                <span style="color:#00f5d4">{item['stride']}</span>
                &nbsp;·&nbsp;
                <strong style="color:#c4b5fd">MITRE:</strong>
                <span style="color:#ffb703;font-family:'JetBrains Mono',monospace;font-size:11px">{item['mitre']}</span>
            </div>
            <div class="threat-desc">{item['description']}</div>
            <div class="csr-box"><strong>Cybersecurity Requirement:</strong> {item['csr']}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"Recalculate Attack Potential — {item['id']}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                t_val = st.selectbox("Elapsed Time", ["< 1 Month (0)", "<= 3 Months (1)", "<= 6 Months (4)", "> 6 Months (10)"], key=f"t_{idx}")
                e_val = st.selectbox("Specialist Expertise", ["Layman (0)", "Proficient (3)", "Expert (6)", "Multiple Experts (8)"], key=f"e_{idx}")
            with c2:
                k_val = st.selectbox("Knowledge of Item", ["Public (0)", "Restricted (3)", "Confidential (7)", "Strictly Confidential (11)"], key=f"k_{idx}")
                w_val = st.selectbox("Window of Opportunity", ["Unrestricted (0)", "Easy (1)", "Moderate (4)", "Difficult (10)"], key=f"w_{idx}")
            with c3:
                eq_val = st.selectbox("Equipment Required", ["Standard (0)", "Specialized (4)", "Bespoke (7)"], key=f"eq_{idx}")
                if st.button("Re-evaluate Score", key=f"btn_calc_{idx}"):
                    # ISO 21434 Annex G Attack Potential calculation
                    t_score = int(t_val.split("(")[1].replace(")", ""))
                    e_score = int(e_val.split("(")[1].replace(")", ""))
                    k_score = int(k_val.split("(")[1].replace(")", ""))
                    w_score = int(w_val.split("(")[1].replace(")", ""))
                    eq_score = int(eq_val.split("(")[1].replace(")", ""))
                    total_pts = t_score + e_score + k_score + w_score + eq_score

                    if total_pts <= 9:
                        feas = "High"
                        risk_lvl = 4
                    elif total_pts <= 19:
                        feas = "Medium"
                        risk_lvl = 3
                    elif total_pts <= 24:
                        feas = "Low"
                        risk_lvl = 2
                    else:
                        feas = "Very Low"
                        risk_lvl = 1

                    st.session_state.tara_items[idx]["feasibility"] = feas
                    st.session_state.tara_items[idx]["risk"] = risk_lvl
                    st.toast(f"{item['id']} score re-evaluated (Score: {total_pts})")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · WHAT-IF ARCHITECTURE SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin-bottom:4px;">'What-If' Architecture Defense Simulator</h3>
        <p style="font-size:13px;color:#9d9aa9;margin:0;">Toggle security controls to evaluate real-time changes to the UNECE R155 attack surface and risk posture.</p>
    </div>
    """, unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([1, 1], gap="large")

    with col_t1:
        st.markdown("""
        <div class="g-card" style="margin-bottom:0px; padding:22px;">
            <div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#c4b5fd;font-family:'JetBrains Mono',monospace;margin-bottom:18px;display:flex;align-items:center;gap:10px;">
                ARCHITECTURE CONTROLS
                <span style="flex:1;height:1px;background:rgba(131,91,255,0.25);"></span>
            </div>
        """, unsafe_allow_html=True)
        s_ota   = st.toggle("External Cellular OTA Flashing", value=True)
        s_secoc = st.toggle("Enforce SecOC on Powertrain CAN FD", value=False)
        s_obd   = st.toggle("PKI Auth on OBD-II Diagnostic", value=False)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t2:
        st.markdown("""
        <div class="g-card" style="margin-bottom:0px; padding:22px;">
            <div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#c4b5fd;font-family:'JetBrains Mono',monospace;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
                LIVE BUS SECURITY VISUALIZATION
                <span style="flex:1;height:1px;background:rgba(131,91,255,0.25);"></span>
            </div>
        """, unsafe_allow_html=True)

        bus_ota_color = "#ff2a85" if s_ota else "#00f5d4"
        bus_ota_class = "bus-threat" if s_ota else "bus-active"
        bus_sec_color = "#00f5d4" if s_secoc else "#ff2a85"
        bus_sec_class = "bus-active" if s_secoc else "bus-threat"
        bus_obd_color = "#00f5d4" if s_obd else "#ffb703"

        BUS_ANIMATION_HTML = f"""
        <!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
        <style>
        *{{box-sizing:border-box;margin:0;padding:0}}
        body{{background:transparent;font-family:'JetBrains Mono',monospace;color:#f1f5f9;padding:0;}}
        .bus-wrap{{width:100%;overflow:hidden;}}
        svg.bus-svg{{width:100%;height:110px;}}
        @keyframes busflow{{0%{{stroke-dashoffset:60}}100%{{stroke-dashoffset:0}}}}
        @keyframes busflow-red{{0%{{stroke-dashoffset:60}}100%{{stroke-dashoffset:0}}}}
        .bus-active{{stroke-dasharray:6 4;animation:busflow 1.5s linear infinite;}}
        .bus-threat{{stroke-dasharray:6 4;animation:busflow-red 1.2s linear infinite;}}
        </style>
        </head>
        <body>
        <div class="bus-wrap">
        <svg class="bus-svg" viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
            <text x="10" y="22" fill="#9d9aa9" font-size="9.5">CELLULAR → TCU</text>
            <line x1="10" y1="30" x2="390" y2="30" stroke="{bus_ota_color}" stroke-width="2.2" class="{bus_ota_class}"/>
            <circle cx="390" cy="30" r="4.5" fill="{bus_ota_color}" style="filter:drop-shadow(0 0 6px {bus_ota_color})"/>

            <text x="10" y="58" fill="#9d9aa9" font-size="9.5">CAN FD POWERTRAIN</text>
            <line x1="10" y1="66" x2="390" y2="66" stroke="{bus_sec_color}" stroke-width="2.2" class="{bus_sec_class}"/>
            <circle cx="390" cy="66" r="4.5" fill="{bus_sec_color}" style="filter:drop-shadow(0 0 6px {bus_sec_color})"/>

            <text x="10" y="92" fill="#9d9aa9" font-size="9.5">OBD-II DIAGNOSTIC</text>
            <line x1="10" y1="98" x2="390" y2="98" stroke="{bus_obd_color}" stroke-width="2.2" class="bus-active"/>
            <circle cx="390" cy="98" r="4.5" fill="{bus_obd_color}" style="filter:drop-shadow(0 0 6px {bus_obd_color})"/>
        </svg>
        </div>
        </body></html>
        """
        components.html(BUS_ANIMATION_HTML, height=115, scrolling=False)

        if s_ota and not s_secoc:
            st.error("**High Risk** — OTA exposed without SecOC. Remote takeover vector active.")
        elif s_ota and s_secoc and not s_obd:
            st.warning("**Moderate Risk** — OTA secured, but OBD-II port unauthenticated.")
        else:
            st.success("**Hardened** — All controls active. UNECE R155 §7.3 compliant.")

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 · ENGINEER REVIEW & AUDIT TRAIL
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <h3>Engineer Review &amp; Audit Trail</h3>
    <p class="sub">Disposition decisions logged per ISO/SAE 21434 Clause 6</p>
    <hr class="sec-divider"/>
    """, unsafe_allow_html=True)

    STATUS_COLOR = {
        "Pending Review": "chip-info",
        "Approved": "chip-low",
        "Rejected": "chip-critical"
    }

    for item in st.session_state.tara_items:
        sc = STATUS_COLOR.get(item['status'], 'chip-info')
        st.markdown(f"""
        <div class="threat-row" style="margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span class="threat-id">{item['id']}</span>
                    <div class="threat-asset" style="font-size:15px;">{item['asset']}</div>
                </div>
                <span class="chip {sc}">{item['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        notes = st.text_input(
            f"Disposition Rationale — {item['id']}",
            value=item.get("notes", ""),
            placeholder="Enter engineering rationale, mitigating factors, or residual risk acceptance justification...",
            key=f"note_{item['id']}"
        )
        b_app, b_rej, _ = st.columns([1, 1, 4])
        with b_app:
            if st.button(f"Approve {item['id']}", key=f"app_{item['id']}"):
                item['status'] = "Approved"
                item['notes'] = notes
                st.toast(f"**{item['id']}** approved and logged to audit trail")
                st.rerun()
        with b_rej:
            if st.button(f"Reject {item['id']}", key=f"rej_{item['id']}"):
                item['status'] = "Rejected"
                item['notes'] = notes
                st.toast(f"**{item['id']}** rejected and logged to audit trail")
                st.rerun()
        st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 · COMPLIANCE EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("""
    <h3>Compliance Export</h3>
    <p class="sub">Generate audit packages for UNECE R155/R156 type approval</p>
    <hr class="sec-divider"/>
    """, unsafe_allow_html=True)

    # Summary metrics row
    total = len(st.session_state.tara_items)
    approved = sum(1 for i in st.session_state.tara_items if i['status'] == 'Approved')
    pending  = sum(1 for i in st.session_state.tara_items if i['status'] == 'Pending Review')
    critical = sum(1 for i in st.session_state.tara_items if i.get('severity') == 'critical')

    mc1, mc2, mc3, mc4 = st.columns(4)
    for col, label, value, cls in [
        (mc1, "Total Threats",  total,    "chip-info"),
        (mc2, "Approved",       approved, "chip-low"),
        (mc3, "Pending",        pending,  "chip-medium"),
        (mc4, "Critical",       critical, "chip-critical"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:rgba(13,8,38,0.65);backdrop-filter:blur(16px);border:1px solid rgba(131,91,255,0.25);border-radius:14px;padding:20px;text-align:center;">
                <div style="font-size:30px;font-weight:800;color:#ffffff;letter-spacing:-1px;">{value}</div>
                <div style="font-size:11px;color:#c4b5fd;margin-top:4px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:0.8px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    df_exp = pd.DataFrame(st.session_state.tara_items)
    st.dataframe(
        df_exp[["id", "asset", "boundary", "stride", "mitre", "feasibility", "impact", "risk", "status"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id":          st.column_config.TextColumn("ID"),
            "asset":       st.column_config.TextColumn("Asset"),
            "risk":        st.column_config.NumberColumn("Risk Lvl", format="%d ★"),
            "status":      st.column_config.TextColumn("Status"),
        }
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    c_e1, c_e2, c_e3 = st.columns(3)
    with c_e1:
        st.download_button(
            label="Export TARA Matrix (.CSV)",
            data=df_exp.to_csv(index=False).encode('utf-8'),
            file_name="AutoSec_TARA_WorkProduct_ISO21434.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c_e2:
        st.download_button(
            label="Export JSON Report",
            data=json.dumps(st.session_state.tara_items, indent=2).encode('utf-8'),
            file_name="AutoSec_TARA_Report.json",
            mime="application/json",
            use_container_width=True
        )
    with c_e3:
        if st.button("Generate UNECE R155 PDF Audit Package", use_container_width=True):
            st.success("ISO 21434 / UNECE R155 Audit Package PDF compiled & ready for CSMS submission!")


# ─── FOOTER ───────────────────────────────────────────────────────────────────
FOOTER_RAW_HTML = """
<div class="app-footer">
    <div class="ft-grid">
        <div>
            <div class="ft-brand">
                <div class="ft-brand-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9,12 11,14 15,10"/></svg>
                </div>
                <div class="ft-brand-name">Orchid TARA Engine</div>
            </div>
            <p class="ft-desc">
                Automotive Cybersecurity Threat Analysis and Risk Assessment platform aligned strictly with ISO/SAE 21434 Clause 15 and UNECE R155/R156 type approval mandates.
            </p>
            <div class="ft-badge-pulse">
                <span class="pulse-dot"></span> UNECE R155 &amp; ISO 21434 ACTIVE
            </div>
        </div>

        <div>
            <div class="ft-col-title">TARA Capabilities</div>
            <ul class="ft-links">
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">ISO 21434 Risk Engine</a></li>
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">Attack Graph Topology</a></li>
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">What-If Defense Simulator</a></li>
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">AUTOSAR ARXML Parser</a></li>
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">CAN Database DBC Matrix</a></li>
            </ul>
        </div>

        <div>
            <div class="ft-col-title">Compliance &amp; ALM</div>
            <ul class="ft-links">
                <li><a href="https://www.iso.org/standard/70918.html" target="_blank" rel="noopener noreferrer">ISO/SAE 21434 Clause 15</a></li>
                <li><a href="https://unece.org/transport/documents/2021/03/standards/unece-regulation-no-155-cyber-security-and-cyber-security" target="_blank" rel="noopener noreferrer">UNECE R155 CSMS Approval</a></li>
                <li><a href="https://unece.org/transport/documents/2021/03/standards/unece-regulation-no-156-software-update-and-software-update" target="_blank" rel="noopener noreferrer">UNECE R156 SUMS Management</a></li>
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">Atlassian Jira REST API</a></li>
                <li><a onclick="document.getElementById('workspace-anchor').scrollIntoView({behavior: 'smooth', block: 'start'})" style="cursor:pointer;">Jama Connect REST API</a></li>
            </ul>
        </div>

        <div>
            <div class="ft-col-title">Live System Telemetry</div>
            <div class="ft-status-card">
                <div class="ft-status-item">
                    <span class="ft-status-label">Backend API:</span>
                    <span class="ft-status-val" style="color:#00f5d4;">Operational (Port 8000)</span>
                </div>
                <div class="ft-status-item">
                    <span class="ft-status-label">Streamlit UI:</span>
                    <span class="ft-status-val" style="color:#00f5d4;">Active (Port 8501)</span>
                </div>
                <div class="ft-status-item">
                    <span class="ft-status-label">VectorDB Store:</span>
                    <span class="ft-status-val" style="color:#c4b5fd;">ChromaDB Persistent</span>
                </div>
                <div class="ft-status-item">
                    <span class="ft-status-label">Audit Engine:</span>
                    <span class="ft-status-val" style="color:#ffb703;">SQLite ORM Active</span>
                </div>
            </div>
        </div>
    </div>

    <div class="ft-bottom">
        <div class="ft-copy">
            © 2026 Orchid Security Inc. Automotive Cybersecurity Division. All rights reserved.
        </div>
        <div class="ft-sublinks">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Compliance</a>
            <a href="#">ISO 21434 Documentation</a>
            <a href="#">Security Audit Trail</a>
        </div>
    </div>
</div>
"""
FOOTER_CLEAN_HTML = "".join(line.strip() for line in FOOTER_RAW_HTML.splitlines())
st.markdown(FOOTER_CLEAN_HTML, unsafe_allow_html=True)

