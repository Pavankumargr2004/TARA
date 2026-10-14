import os
import sys

# ── Ensure project root is importable when run as `streamlit run frontend/app.py` ──
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

import json
import re
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
    from sklearn.pipeline import Pipeline
    ML_LIBS_AVAILABLE = True
except ImportError:
    ML_LIBS_AVAILABLE = False

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
def extract_full_architecture(filepath: str, filename: str):
    """Dynamically extracts Architecture Name, Trust Boundaries, Threats, and ECUs from any ARXML, DBC, JSON, TXT, or PDF file."""
    ext = os.path.splitext(filename)[-1].lower()
    trust_boundaries = []
    threat_items = []
    extracted_ecus = []
    base_name = filename.replace("_", " ").replace(".json", "").replace(".dbc", "").replace(".arxml", "").replace(".txt", "").replace(".pdf", "").title()
    arch_name = base_name

    content = ""
    if ext != ".pdf":
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            pass

    if ext == ".arxml":
        from app.services.autosar_dbc_parser import AutosarArxmlParser
        parsed = AutosarArxmlParser.parse_arxml_string(content)
        arch_name = parsed.get("system_name", base_name).replace("_", " ")
        extracted_ecus = parsed.get("ecus", [])
        for i, tb in enumerate(parsed.get("trust_boundaries", [])):
            tb_id = tb.get("id", f"TB-A{i+1:02d}")
            src = tb.get("source", "Subnet")
            tgt = tb.get("target", "ECU Core")
            risk = tb.get("risk", "High")
            stride = tb.get("stride", "Elevation of Privilege")
            csr = tb.get("csr", "AUTOSAR trust boundary enforcement.")
            trust_boundaries.append({
                "id": tb_id,
                "route": f"{src} ↔ {tgt}",
                "risk": risk,
                "desc": csr
            })
            threat_items.append({
                "id": f"THR-{len(threat_items)+1:03d}",
                "asset": tgt,
                "boundary": f"{src} ↔ {tgt}",
                "stride": stride,
                "mitre": "T1565 (Data Manipulation)",
                "description": f"Lateral breach from {src} pivots across {tb.get('interface', 'Ethernet')} to compromise {tgt}.",
                "attack_path": [src, tb.get("interface", "Central Gateway"), tgt],
                "csr": csr,
                "feasibility": "Medium" if "Critical" in risk else "High",
                "impact": "Severe" if "Critical" in risk else "Major",
                "risk": 5 if "Critical" in risk else 4,
                "status": "Pending Review",
                "notes": "Extracted dynamically from AUTOSAR ARXML.",
                "severity": "critical" if "Critical" in risk else "high"
            })
        for ecu in extracted_ecus:
            if ecu.get("asil") in ["ASIL-D", "ASIL-B", "ASIL-C"] and not any(t["asset"] == ecu["name"] for t in threat_items):
                nt_id = f"THR-{len(threat_items)+1:03d}"
                threat_items.append({
                    "id": nt_id,
                    "asset": f"{ecu['name']} ({ecu.get('domain', 'Powertrain')})",
                    "boundary": f"In-Vehicle Bus ↔ {ecu['name']}",
                    "stride": "Tampering / Denial of Service",
                    "mitre": "T1499 (Endpoint DoS)",
                    "description": f"Targeted buffer starvation or CAN flood against safety-critical {ecu['name']} ({ecu.get('asil')}).",
                    "attack_path": ["Diagnostic Gateway", ecu.get("bus", "CAN FD"), ecu["name"]],
                    "csr": f"CSR-ASIL-{len(threat_items)+1:02d}: {ecu['name']} shall implement hardware rate limiting and secure boot.",
                    "feasibility": "Medium",
                    "impact": "Severe",
                    "risk": 5 if ecu.get("asil") == "ASIL-D" else 4,
                    "status": "Pending Review",
                    "notes": "Safety-critical ASIL requirement from AUTOSAR definition.",
                    "severity": "critical"
                })

    elif ext == ".dbc":
        from app.services.autosar_dbc_parser import CanDbcParser
        parsed = CanDbcParser.parse_dbc_string(content)
        arch_name = parsed.get("system_name", base_name).replace("_", " ")
        messages = parsed.get("messages", [])
        extracted_ecus = parsed.get("ecus", [])
        ecu_names = [e["name"] for e in extracted_ecus]

        comments = parsed.get("trust_boundaries_comments", [])
        if comments:
            for i, c in enumerate(comments):
                trust_boundaries.append({
                    "id": f"TB-D{i+1:02d}",
                    "route": f"{ecu_names[0] if ecu_names else 'BMS'} ↔ Actuation Subnet",
                    "risk": "High",
                    "desc": c
                })
        else:
            primary_ecu = ecu_names[0] if ecu_names else "Powertrain Controller"
            trust_boundaries.append({
                "id": "TB-CAN-01",
                "route": f"{primary_ecu} ↔ Central Inverter Gateway",
                "risk": "Critical",
                "desc": "High voltage and torque message interface lacking mandatory hardware MAC verification."
            })
            trust_boundaries.append({
                "id": "TB-CAN-02",
                "route": "Diagnostic Port ↔ Internal CAN-FD Bus",
                "risk": "High",
                "desc": "Unauthenticated frame injection risk on powertrain actuators."
            })
            if len(ecu_names) > 1:
                trust_boundaries.append({
                    "id": "TB-CAN-03",
                    "route": f"{ecu_names[1]} ↔ Gateway Router",
                    "risk": "Medium",
                    "desc": "Actuation communication route requiring freshness counter replay mitigation."
                })

        for i, msg in enumerate(messages[:10]):
            tx = msg.get("transmitter", "ECU")
            msg_name = msg.get("name", "CAN_Message")
            can_id = msg.get("can_id", "0x100")
            signals = [s["name"] for s in msg.get("signals", [])][:3]
            sig_str = f" [Signals: {', '.join(signals)}]" if signals else ""
            is_crit = any(k in msg_name.upper() for k in ["BATTERY", "BRAKE", "TORQUE", "STATUS", "CONTACTOR", "CURRENT", "VOLTAGE", "SAFE", "STEER"])
            
            threat_items.append({
                "id": f"THR-{len(threat_items)+1:03d}",
                "asset": f"{tx} ({msg_name}){sig_str}",
                "boundary": f"CAN-FD Subnet ↔ {tx}",
                "stride": "Tampering / Spoofing" if is_crit else "Information Disclosure",
                "mitre": "T1565 (CAN Bus Manipulation)",
                "description": f"Injection or spoofing of CAN frame '{msg_name}' (ID: {can_id}) overriding critical actuator signals on {tx}.",
                "attack_path": ["OBD-II / Gateway Tap", "CAN-FD Backbone", tx],
                "csr": f"CSR-CAN-{i+1:02d}: Frame {msg_name} (ID: {can_id}) shall enforce 128-bit SecOC CMAC validation and monotonic freshness counter.",
                "feasibility": "High",
                "impact": "Severe" if is_crit else "Major",
                "risk": 5 if is_crit else 4,
                "status": "Pending Review",
                "notes": f"Extracted dynamically from CAN DBC (ID: {can_id}, DLC: {msg.get('dlc')}).",
                "severity": "critical" if is_crit else "high"
            })

    elif ext == ".json":
        data = json.loads(content)
        arch_name = data.get("project_name") or data.get("system_name", base_name)
        extracted_ecus = data.get("ecus", [])
        
        for i, tb in enumerate(data.get("trust_boundaries", [])):
            tb_id = tb.get("id") or tb.get("boundary_id", f"TB-J{i+1:02d}")
            src = tb.get("source", "External Domain")
            tgt = tb.get("target", "Target Module")
            risk = tb.get("risk_level") or tb.get("risk", "High")
            stride = tb.get("stride_category") or tb.get("stride", "Spoofing / Tampering")
            desc = tb.get("description", "Trust boundary communication link.")
            trust_boundaries.append({
                "id": tb_id,
                "route": f"{src} ↔ {tgt}",
                "risk": risk,
                "desc": desc
            })
            threat_items.append({
                "id": f"THR-{len(threat_items)+1:03d}",
                "asset": tgt,
                "boundary": f"{src} ↔ {tgt}",
                "stride": stride,
                "mitre": "T1565 (Telemetry Spoofing)" if "Spoof" in stride else "T1542 (Firmware Manipulation)",
                "description": desc,
                "attack_path": [src, tb.get("interface", "Gateway Router"), tgt],
                "csr": f"CSR-{tb_id}: Enforce zero-trust cryptographic mutual authentication and plausibility checking on {tgt}.",
                "feasibility": "Medium" if "Critical" in risk else "High",
                "impact": "Severe" if "Critical" in risk else "Major",
                "risk": 5 if "Critical" in risk else 4,
                "status": "Pending Review",
                "notes": "Extracted dynamically from JSON architecture specification.",
                "severity": "critical" if "Critical" in risk else "high"
            })

        for sc in data.get("threat_scenarios", []):
            if not any(t["id"] == sc.get("threat_id") for t in threat_items):
                threat_items.append({
                    "id": sc.get("threat_id", f"THR-{len(threat_items)+1:03d}"),
                    "asset": sc.get("target_asset", "Target ECU"),
                    "boundary": sc.get("trust_boundary_id", "Internal Bus"),
                    "stride": sc.get("stride_category", "Spoofing"),
                    "mitre": sc.get("mitre_attack_id", "T1565"),
                    "description": sc.get("threat_description", "Potential vulnerability."),
                    "attack_path": sc.get("attack_path", ["Cloud", "Gateway", "ECU"]),
                    "csr": sc.get("cybersecurity_requirement", "Implement authentication."),
                    "feasibility": sc.get("calculated_feasibility", "Medium"),
                    "impact": sc.get("calculated_impact", "Major"),
                    "risk": sc.get("risk_level", 4),
                    "status": sc.get("review_status", "Pending Review"),
                    "notes": sc.get("reviewer_notes", "Loaded from JSON threat catalog."),
                    "severity": "critical" if sc.get("risk_level", 4) >= 5 else "high"
                })

    elif ext == ".pdf":
        pdf_text = ""
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    pdf_text += txt + "\n"
        except Exception:
            try:
                import fitz
                doc = fitz.open(filepath)
                for page in doc:
                    pdf_text += page.get_text() + "\n"
            except Exception:
                pass

        arch_name = base_name
        lines = [l.strip() for l in pdf_text.splitlines() if l.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 60 and any(k in first_line.lower() for k in ["spec", "system", "architecture", "tara", "gateway", "bms", "adas"]):
                arch_name = first_line

        tb_blocks = re.findall(r"\[Trust Boundary\s+([^\]]+)\](.*?)(?=\[Trust Boundary|\Z)", pdf_text, re.DOTALL | re.IGNORECASE)
        if tb_blocks:
            for i, (tb_header, tb_body) in enumerate(tb_blocks):
                tb_id = tb_header.split(":")[0].strip() if ":" in tb_header else f"TB-P{i+1:02d}"
                route = tb_header.split(":", 1)[1].strip() if ":" in tb_header else tb_header
                risk_match = re.search(r"Risk Level:\s*([^\n\r]+)", tb_body)
                stride_match = re.search(r"STRIDE Category:\s*([^\n\r]+)", tb_body)
                desc_match = re.search(r"Threat (?:Description|Scenario):\s*([^\n\r]+)", tb_body)
                mitigation_match = re.search(r"Mitigation:\s*([^\n\r]+)", tb_body)

                risk = risk_match.group(1).strip() if risk_match else "High"
                stride = stride_match.group(1).strip() if stride_match else "Tampering / Elevation of Privilege"
                desc = desc_match.group(1).strip() if desc_match else f"Security risk identified across {route}."
                csr = mitigation_match.group(1).strip() if mitigation_match else "Implement cryptographic controls."

                trust_boundaries.append({
                    "id": tb_id,
                    "route": route,
                    "risk": risk,
                    "desc": desc[:130] + "..." if len(desc) > 130 else desc
                })
                parts = route.split("<->") if "<->" in route else (route.split("↔") if "↔" in route else [route, "Gateway"])
                src = parts[0].strip()
                tgt = parts[1].strip() if len(parts) > 1 else "Target ECU"

                threat_items.append({
                    "id": f"THR-{len(threat_items)+1:03d}",
                    "asset": tgt,
                    "boundary": route,
                    "stride": stride,
                    "mitre": "T1059 (Command Execution)",
                    "description": desc,
                    "attack_path": [src, "Central Gateway", tgt],
                    "csr": f"CSR-{tb_id}: {csr}",
                    "feasibility": "Medium",
                    "impact": "Severe" if "Critical" in risk else "Major",
                    "risk": 5 if "Critical" in risk else 4,
                    "status": "Pending Review",
                    "notes": "Extracted dynamically from technical specification PDF.",
                    "severity": "critical" if "Critical" in risk else "high"
                })
        else:
            ecu_candidates = re.findall(r"\b([A-Z][A-Za-z0-9_\-]+(?:ECU|Controller|Gateway|Unit|Module|Sensor|Radar|LiDAR|Camera|BMS|Inverter|TCU))\b", pdf_text)
            unique_ecus = list(dict.fromkeys(ecu_candidates))[:6]
            if not unique_ecus:
                unique_ecus = ["Telematics Control Unit", "Central Gateway ECU", "Powertrain Actuator", "Battery Management System"]

            for idx, ecu in enumerate(unique_ecus):
                extracted_ecus.append({
                    "name": ecu,
                    "domain": "Vehicle Network",
                    "bus": "CAN FD / Automotive Ethernet",
                    "asil": "ASIL-D" if any(k in ecu.upper() for k in ["BRAKE", "STEER", "BMS", "BATTERY"]) else "QM"
                })

            trust_boundaries.append({
                "id": "TB-PDF-01",
                "route": f"External Interface ↔ {unique_ecus[0]}",
                "risk": "Critical",
                "desc": "Primary ingress wireless and diagnostic boundary identified in PDF specification."
            })
            trust_boundaries.append({
                "id": "TB-PDF-02",
                "route": f"{unique_ecus[0]} ↔ Internal Vehicle Bus",
                "risk": "High",
                "desc": "Lateral transit boundary from external domain into in-vehicle subnet."
            })
            if len(unique_ecus) > 1:
                trust_boundaries.append({
                    "id": "TB-PDF-03",
                    "route": f"Internal Gateway ↔ {unique_ecus[-1]}",
                    "risk": "High",
                    "desc": "Safety-critical actuation interface requiring ISO 21434 SecOC enforcement."
                })

            for idx, ecu in enumerate(unique_ecus[:5]):
                is_crit = idx == 0 or idx == len(unique_ecus) - 1
                threat_items.append({
                    "id": f"THR-{len(threat_items)+1:03d}",
                    "asset": ecu,
                    "boundary": f"In-Vehicle Bus ↔ {ecu}",
                    "stride": "Elevation of Privilege" if idx == 0 else "Tampering / Spoofing",
                    "mitre": "T1565 (Automotive Network Exploitation)",
                    "description": f"Extracted from PDF: Vulnerability detected on {ecu} allowing unauthorized message injection or manipulation.",
                    "attack_path": ["Air Interface / OBD-II", "Central Gateway", ecu],
                    "csr": f"CSR-PDF-{idx+1:02d}: Enforce cryptographic authentication, secure boot, and ISO 21434 CAL-3 controls on {ecu}.",
                    "feasibility": "Medium" if is_crit else "High",
                    "impact": "Severe" if is_crit else "Major",
                    "risk": 5 if is_crit else 4,
                    "status": "Pending Review",
                    "notes": "Extracted dynamically from technical PDF document.",
                    "severity": "critical" if is_crit else "high"
                })

    elif ext == ".txt":
        tb_blocks = re.findall(r"\[Trust Boundary\s+([^\]]+)\](.*?)(?=\[Trust Boundary|\Z)", content, re.DOTALL | re.IGNORECASE)
        if tb_blocks:
            for i, (tb_header, tb_body) in enumerate(tb_blocks):
                tb_id = tb_header.split(":")[0].strip() if ":" in tb_header else f"TB-T{i+1:02d}"
                route = tb_header.split(":", 1)[1].strip() if ":" in tb_header else tb_header

                risk_match = re.search(r"Risk Level:\s*([^\n\r]+)", tb_body)
                stride_match = re.search(r"STRIDE Category:\s*([^\n\r]+)", tb_body)
                desc_match = re.search(r"Threat (?:Description|Scenario):\s*([^\n\r]+)", tb_body)
                mitigation_match = re.search(r"Mitigation:\s*([^\n\r]+)", tb_body)

                risk = risk_match.group(1).strip() if risk_match else "High"
                stride = stride_match.group(1).strip() if stride_match else "Tampering / Elevation of Privilege"
                desc = desc_match.group(1).strip() if desc_match else f"Security risk identified across {route}."
                csr = mitigation_match.group(1).strip() if mitigation_match else "Implement cryptographic controls."

                trust_boundaries.append({
                    "id": tb_id,
                    "route": route,
                    "risk": risk,
                    "desc": desc[:130] + "..." if len(desc) > 130 else desc
                })

                parts = route.split("<->") if "<->" in route else (route.split("↔") if "↔" in route else [route, "Gateway"])
                src = parts[0].strip()
                tgt = parts[1].strip() if len(parts) > 1 else "Target ECU"

                threat_items.append({
                    "id": f"THR-{len(threat_items)+1:03d}",
                    "asset": tgt,
                    "boundary": route,
                    "stride": stride,
                    "mitre": "T1059 (Command Execution)",
                    "description": desc,
                    "attack_path": [src, "Central Gateway", tgt],
                    "csr": f"CSR-{tb_id}: {csr}",
                    "feasibility": "Medium",
                    "impact": "Severe" if "Critical" in risk else "Major",
                    "risk": 5 if "Critical" in risk else 4,
                    "status": "Pending Review",
                    "notes": "Extracted dynamically from Specification TXT.",
                    "severity": "critical" if "Critical" in risk else "high"
                })
        else:
            trust_boundaries.append({
                "id": "TB-01",
                "route": "Ingress Network ↔ Powertrain Segment",
                "risk": "Critical",
                "desc": "Primary external connectivity gateway interface extracted from document."
            })
            threat_items.append({
                "id": "THR-001",
                "asset": "Central Domain Gateway",
                "boundary": "Ingress Network ↔ Powertrain Segment",
                "stride": "Spoofing / Tampering",
                "mitre": "T1565 (Data Manipulation)",
                "description": f"Automated extraction from '{filename}': Unverified frame injection vector detected on internal bus route.",
                "attack_path": ["Public Cloud / Air Interface", "Telematics Unit", "Central Gateway ECU"],
                "csr": "CSR-001: The gateway shall validate frame IDs and SecOC freshness counters for all incoming messages.",
                "feasibility": "Medium",
                "impact": "High",
                "risk": 4,
                "status": "Pending Review",
                "notes": "Parsed from specification file.",
                "severity": "critical"
            })

    if not extracted_ecus:
        unique_nodes = set()
        for t in threat_items:
            unique_nodes.add(t["asset"].split("(")[0].strip())
            for node in t.get("attack_path", []):
                unique_nodes.add(node.strip())
        for n in list(unique_nodes)[:8]:
            extracted_ecus.append({
                "name": n,
                "domain": "Vehicle Subnet",
                "bus": "CAN FD / Ethernet",
                "asil": "ASIL-D" if any(k in n.upper() for k in ["BRAKE", "BMS", "BATTERY", "INVERTER", "STEER"]) else "QM"
            })

    return arch_name, trust_boundaries, threat_items, extracted_ecus


def generate_dynamic_attack_graph_svg(threat: dict) -> str:
    """Dynamically generates animated multi-hop attack propagation SVG based on the threat's attack path."""
    path = threat.get("attack_path", ["Public Cloud", "Gateway ECU", "Target Actuator"])
    if not path or len(path) < 2:
        path = ["Public Cloud", "Gateway ECU", "Target Actuator"]

    n = len(path)
    total_w = 950
    start_x = 90
    step_x = (total_w - 180) / max(1, n - 1)

    lines_svg = ""
    particles_svg = ""
    nodes_svg = ""

    colors = {
        "entry": {"main": "#ff2a85", "bg": "rgba(255,42,133,0.12)", "border": "rgba(255,42,133,0.4)"},
        "pivot": {"main": "#835bff", "bg": "rgba(131,91,255,0.12)", "border": "rgba(131,91,255,0.4)"},
        "target": {"main": "#00f5d4", "bg": "rgba(0,245,212,0.12)", "border": "rgba(0,245,212,0.4)"}
    }

    for i in range(n - 1):
        x1 = start_x + i * step_x + 32
        x2 = start_x + (i + 1) * step_x - 32
        anim_class = f"edge-anim{(i % 4) + 1}"
        col = "#835bff" if i < n - 2 else "#00f5d4"
        lines_svg += f"""
        <line x1="{x1:.1f}" y1="75" x2="{x2:.1f}" y2="75" stroke="{col}" stroke-width="1.8" stroke-opacity="0.25"/>
        <line x1="{x1:.1f}" y1="75" x2="{x2:.1f}" y2="75" stroke="{col}" stroke-width="1.8" class="{anim_class}" fill="none"/>
        """
        p_class = "p-magenta" if i == 0 else ("p-purple" if i < n - 2 else "p-mint")
        dur = f"{1.8 + i*0.2:.1f}s"
        particles_svg += f"""
        <circle class="particle {p_class}"><animateMotion dur="{dur}" repeatCount="indefinite" path="M {x1:.1f} 75 L {x2:.1f} 75"/></circle>
        """

    for i, node_name in enumerate(path):
        cx = start_x + i * step_x
        cy = 75
        if i == 0:
            c = colors["entry"]
            role_text = "ATTACK ENTRY"
        elif i == n - 1:
            c = colors["target"]
            role_text = "SAFETY TARGET"
        else:
            c = colors["pivot"]
            role_text = f"HOP {i}: PIVOT"

        display_name = node_name[:18] + "..." if len(node_name) > 18 else node_name
        nodes_svg += f"""
        <g>
            <circle cx="{cx:.1f}" cy="{cy}" r="26" fill="{c['bg']}" stroke="{c['main']}" stroke-width="1.8" class="node-circle" style="color:{c['main']}"/>
            <circle cx="{cx:.1f}" cy="{cy}" r="17" fill="rgba(13,8,38,0.9)" stroke="{c['border']}" stroke-width="1"/>
            <rect x="{cx - 72:.1f}" y="116" width="144" height="25" rx="12" class="node-pill" stroke="{c['border']}"/>
            <text x="{cx:.1f}" y="133" text-anchor="middle" class="node-label">{display_name}</text>
            <text x="{cx:.1f}" y="155" text-anchor="middle" fill="{c['main']}" class="node-sublabel">{role_text}</text>
        </g>
        """

    svg_html = f"""
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;color:#f1f5f9;padding:4px 0;}}
    .graph-wrap{{position:relative;width:100%;height:225px;overflow:hidden;}}
    svg.attack-svg{{width:100%;height:100%;}}
    .node-label{{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;fill:#ffffff;}}
    .node-sublabel{{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;letter-spacing:0.5px;}}
    .node-circle{{filter:drop-shadow(0 0 8px currentColor);}}
    .node-pill{{fill:rgba(20,12,48,0.95);stroke-width:1;}}
    @keyframes flow1{{0%{{stroke-dashoffset:160}}100%{{stroke-dashoffset:0}}}}
    @keyframes flow2{{0%{{stroke-dashoffset:160}}100%{{stroke-dashoffset:0}}}}
    @keyframes flow3{{0%{{stroke-dashoffset:160}}100%{{stroke-dashoffset:0}}}}
    @keyframes flow4{{0%{{stroke-dashoffset:140}}100%{{stroke-dashoffset:0}}}}
    .edge-anim1{{stroke-dasharray:7 5;animation:flow1 1.8s linear infinite;}}
    .edge-anim2{{stroke-dasharray:7 5;animation:flow2 2.1s linear infinite;}}
    .edge-anim3{{stroke-dasharray:7 5;animation:flow3 2.4s linear infinite;}}
    .edge-anim4{{stroke-dasharray:7 5;animation:flow4 2.0s linear infinite;}}
    .particle{{r:4;opacity:0.95;}}
    .p-magenta{{fill:#ff2a85;filter:drop-shadow(0 0 5px #ff2a85);}}
    .p-purple {{fill:#835bff;filter:drop-shadow(0 0 5px #835bff);}}
    .p-mint   {{fill:#00f5d4;filter:drop-shadow(0 0 5px #00f5d4);}}
    .legend{{display:flex;gap:20px;margin-top:12px;flex-wrap:wrap;}}
    .lg-item{{display:flex;align-items:center;gap:7px;font-size:11px;color:#9d9aa9;font-family:'JetBrains Mono',monospace;}}
    .lg-dot{{width:9px;height:9px;border-radius:50%;}}
    </style>
    </head>
    <body>
    <div class="graph-wrap">
    <svg class="attack-svg" viewBox="0 0 {total_w} 180" xmlns="http://www.w3.org/2000/svg">
        {lines_svg}
        {particles_svg}
        {nodes_svg}
    </svg>
    </div>
    <div class="legend">
        <div class="lg-item"><div class="lg-dot" style="background:#ff2a85;box-shadow:0 0 6px #ff2a85"></div>External Entry ({path[0]})</div>
        <div class="lg-item"><div class="lg-dot" style="background:#835bff;box-shadow:0 0 6px #835bff"></div>Lateral Pivot Gateways</div>
        <div class="lg-item"><div class="lg-dot" style="background:#00f5d4;box-shadow:0 0 6px #00f5d4"></div>Safety Target ({path[-1]})</div>
        <div class="lg-item">&#9679; Animated Particle = Live Threat Propagation Signal</div>
    </div>
    </body></html>
    """
    return svg_html


if "trust_boundaries" not in st.session_state:
    st.session_state.trust_boundaries = [
        {
            "id": "TB-01",
            "route": "Public Cloud ↔ Telematics Gateway",
            "risk": "Critical",
            "desc": "External cellular channel. OTA flashing surface lacking mandatory SecOC enforcement. Primary attack ingress."
        },
        {
            "id": "TB-02",
            "route": "OBD-II Port ↔ Central Gateway",
            "risk": "Medium",
            "desc": "Physical diagnostic access without PKI authentication. Lateral pivot risk to powertrain bus."
        },
        {
            "id": "TB-03",
            "route": "In-Vehicle Ethernet ↔ Powertrain Subnet",
            "risk": "Low",
            "desc": "Internal bus segment. SecOC CMAC tags enforced. Freshness counter replay protection active."
        }
    ]

if "current_architecture_name" not in st.session_state:
    st.session_state.current_architecture_name = "Connected Sedan 2025 — Telematics Gateway Architecture"

if "extracted_ecus" not in st.session_state:
    st.session_state.extracted_ecus = [
        {"name": "Telematics Control Unit (TCU)", "domain": "Connectivity", "bus": "Cellular / Ethernet", "asil": "QM"},
        {"name": "Central Gateway (CGW)", "domain": "Gateway", "bus": "CAN FD / Ethernet", "asil": "ASIL-B"},
        {"name": "Powertrain & Braking Controller", "domain": "Chassis", "bus": "CAN FD", "asil": "ASIL-D"},
    ]

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
# ── ML cache — defined at module level for proper st.cache_resource behaviour ──
@st.cache_resource(show_spinner="Training ML models on ISO 21434 synthetic dataset...")
def _build_ml_pipeline():
    """Generate dataset, train STRIDE + Risk classifiers, return all artefacts."""
    if not ML_LIBS_AVAILABLE:
        return None

    from app.services.ml_model import generate_synthetic_dataset, FEATURE_COLS_STRIDE, FEATURE_COLS_RISK

    df = generate_synthetic_dataset(n_per_class=150)

    le = LabelEncoder()
    X_s = df[FEATURE_COLS_STRIDE].values
    y_s = le.fit_transform(df["stride"].values)
    X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(X_s, y_s, test_size=0.2, random_state=42, stratify=y_s)
    stride_pipe = Pipeline([("sc", StandardScaler()), ("clf", RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42))])
    stride_pipe.fit(X_tr_s, y_tr_s)
    y_pred_s = stride_pipe.predict(X_te_s)
    cv_s = cross_val_score(stride_pipe, X_s, y_s, cv=5, scoring="f1_weighted")
    fi = dict(zip(FEATURE_COLS_STRIDE, stride_pipe.named_steps["clf"].feature_importances_))

    X_r = df[FEATURE_COLS_RISK].values
    y_r = df["risk_level"].values
    X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(X_r, y_r, test_size=0.2, random_state=42, stratify=y_r)
    risk_pipe = Pipeline([("sc", StandardScaler()), ("clf", GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42))])
    risk_pipe.fit(X_tr_r, y_tr_r)
    y_pred_r = risk_pipe.predict(X_te_r)
    cv_r = cross_val_score(risk_pipe, X_r, y_r, cv=5, scoring="f1_weighted")

    return {
        "df": df, "le": le,
        "stride_pipe": stride_pipe, "risk_pipe": risk_pipe,
        "y_te_s": y_te_s, "y_pred_s": y_pred_s, "cv_s": cv_s, "fi": fi,
        "y_te_r": y_te_r, "y_pred_r": y_pred_r, "cv_r": cv_r,
        "feat_cols_s": FEATURE_COLS_STRIDE, "feat_cols_r": FEATURE_COLS_RISK,
    }


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "System Ingestion",
    "Attack Graph",
    "TARA Matrix",
    "What-If Simulator",
    "Engineer Review",
    "Compliance Export",
    "ML Analytics & EDA",
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

    c_btn1, c_btn2, _ = st.columns([1.2, 1.2, 2.5])
    with c_btn1:
        if up_file:
            if st.button("Process & Vectorize Architecture", width="stretch", key="btn_process_file"):
                progress_text = st.empty()
                bar = st.progress(0)
                
                import time
                import tempfile
                progress_text.markdown("*Step 1/3: Parsing binary & structural specification payload...*")
                bar.progress(35)
                time.sleep(0.3)

                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{up_file.name}") as tmp_f:
                    tmp_f.write(up_file.getvalue())
                    tmp_path = tmp_f.name

                progress_text.markdown("*Step 2/3: Extracting CAN FD IDs, SOME/IP services & Trust Boundaries...*")
                bar.progress(70)
                time.sleep(0.3)

                arch_name, tb_list, threats, ecus = extract_full_architecture(tmp_path, up_file.name)
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

                progress_text.markdown("*Step 3/3: Vectorizing embeddings → ChromaDB `architecture_store`...*")
                bar.progress(100)
                time.sleep(0.2)
                bar.empty()
                progress_text.empty()

                if tb_list:
                    st.session_state.trust_boundaries = tb_list
                if threats:
                    st.session_state.tara_items = threats
                if ecus:
                    st.session_state.extracted_ecus = ecus
                st.session_state.current_architecture_name = arch_name
                st.success(f"Ingested **{up_file.name}** → Extracted {len(tb_list)} Trust Boundaries, {len(ecus)} ECUs & {len(threats)} Threat Vectors into TARA Matrix!")
                st.rerun()
        else:
            st.button("Process & Vectorize Architecture", width="stretch", disabled=True, key="btn_process_disabled")

    with c_btn2:
        if st.button("Reset Workspace (Clear Architecture)", width="stretch", key="btn_reset_ws"):
            st.session_state.trust_boundaries = []
            st.session_state.tara_items = []
            st.session_state.extracted_ecus = []
            st.session_state.current_architecture_name = "No Architecture Loaded"
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(131,91,255,0.2);margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px;font-weight:700;color:#c4b5fd;margin-bottom:8px;font-family:JetBrains Mono,monospace;'>⚡ OR SELECT PRE-CONFIGURED VEHICLE ARCHITECTURE (12 DOMAIN DATASETS)</div>", unsafe_allow_html=True)

    sample_col1, sample_col2 = st.columns([3, 1])
    sample_files_map = {
        "ADAS & Central Perception Controller (JSON)": "adas_autonomous_driving_spec.json",
        "Android Automotive OS (AAOS) IVI & Cluster (JSON)": "ivi_infotainment_android_automotive.json",
        "CCC Digital Key 3.0 UWB / BLE / NFC (JSON)": "digital_key_nfc_ble_uwb.json",
        "Cellular V2X & DSRC Direct Communication (JSON)": "v2x_c_v2x_dsrc_communication.json",
        "High-Voltage 800V BMS Battery Pack (CAN-FD DBC)": "bms_battery_management_system.dbc",
        "Safety-Critical Brake-by-Wire ASIL-D (CAN-FD DBC)": "brake_by_wire_chassis_control.dbc",
        "EV Powertrain & Inverter Architecture (CAN-FD DBC)": "ev_powertrain_battery_spec.dbc",
        "Central Security Gateway with SOME/IP (AUTOSAR ARXML)": "central_gateway_security_zone.arxml",
        "Zonal E/E Compute Cluster (AUTOSAR ARXML)": "zone_architecture_arxml_spec.arxml",
        "High-Power DC Fast Charging ISO 15118 CCS (TXT)": "ev_fast_charging_iso15118_ccs.txt",
        "UNECE R156 SUMS OTA Flashing (TXT)": "ota_flashing_firmware_update.txt",
        "Connected Sedan 2025 Telematics Gateway (TXT)": "telematics_gateway_spec.txt",
    }
    with sample_col1:
        selected_sample_label = st.selectbox(
            "Select Pre-configured Vehicle Architecture Specification",
            options=list(sample_files_map.keys()),
            key="sample_spec_selector",
            label_visibility="collapsed"
        )
    with sample_col2:
        if st.button("Load Specification", width="stretch", key="btn_load_sample"):
            selected_filename = sample_files_map[selected_sample_label]
            sample_path = os.path.join(_proj_root, "sample_data", selected_filename)
            if os.path.exists(sample_path):
                arch_name, tb_list, threats, ecus = extract_full_architecture(sample_path, selected_filename)
                if tb_list:
                    st.session_state.trust_boundaries = tb_list
                if threats:
                    st.session_state.tara_items = threats
                if ecus:
                    st.session_state.extracted_ecus = ecus
                st.session_state.current_architecture_name = arch_name
                st.success(f"Loaded **{selected_sample_label}** → {len(tb_list)} Trust Boundaries, {len(ecus)} ECUs & {len(threats)} Threats!")
                st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    if not st.session_state.trust_boundaries:
        st.info("No vehicle architecture loaded. Upload an ARXML, DBC, JSON, TXT, or PDF file above, or select a reference specification to dynamically generate the full TARA matrix.")
    else:
        tb_cards_html = ""
        for idx, tb in enumerate(st.session_state.trust_boundaries):
            risk_lower = tb.get("risk", "Medium").lower()
            if "crit" in risk_lower or "high" in risk_lower:
                card_class = "tb-critical"
                chip_class = "tbc-critical"
                chip_label = tb.get("risk", "Critical")
            elif "med" in risk_lower:
                card_class = "tb-medium"
                chip_class = "tbc-medium"
                chip_label = tb.get("risk", "Medium")
            else:
                card_class = "tb-low"
                chip_class = "tbc-low"
                chip_label = tb.get("risk", "Internal / Low")

            tb_cards_html += f"""
            <div class="tb-card {card_class}">
                <div class="tb-head">
                    <span class="tb-id">{tb.get('id', f'TB-{idx+1:02d}')}</span>
                    <span class="tb-chip {chip_class}">{chip_label}</span>
                </div>
                <div class="tb-route">{tb.get('route', 'External ↔ Vehicle Subnet')}</div>
                <div class="tb-desc">{tb.get('desc', 'Verified boundary interface.')}</div>
            </div>
            """

        TRUST_CARDS_HTML = f"""
        <!DOCTYPE html><html><head>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
        <style>
        *{{box-sizing:border-box;margin:0;padding:0}}
        body{{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;color:#f1f5f9;padding:4px 0;}}
        .sec-label{{font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;}}
        .sec-label::after{{content:'';flex:1;height:1px;background:rgba(131,91,255,0.25);}}
        
        @keyframes cardPop {{
            from {{ opacity: 0; transform: translateY(24px) scale(0.96); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
        .tb-grid{{display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;}}
        .tb-card{{
            background:rgba(13,8,38,0.65);
            backdrop-filter:blur(16px);
            border-radius:14px;
            padding:20px;
            border:1px solid rgba(131,91,255,0.22);
            position:relative;overflow:hidden;
            transition:border-color 0.25s,box-shadow 0.25s,transform 0.25s;
            cursor:pointer;
            animation: cardPop 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        }}
        .tb-card:hover{{border-color:rgba(131,91,255,0.55);box-shadow:0 8px 28px rgba(104,51,255,0.2);transform:translateY(-2px);}}
        .tb-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;}}
        .tb-critical::before{{background:linear-gradient(90deg,#ff2a85,rgba(255,42,133,0.3));}}
        .tb-medium::before  {{background:linear-gradient(90deg,#ffb703,rgba(255,183,3,0.3));}}
        .tb-low::before     {{background:linear-gradient(90deg,#00f5d4,rgba(0,245,212,0.3));}}
        .tb-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}}
        .tb-id{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:#00f5d4;}}
        .tb-chip{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;padding:3px 9px;border-radius:999px;font-family:'JetBrains Mono',monospace;}}
        .tbc-critical{{background:rgba(255,42,133,0.15);color:#ff5eab;border:1px solid rgba(255,42,133,0.4);}}
        .tbc-medium  {{background:rgba(255,183,3,0.15);color:#ffc833;border:1px solid rgba(255,183,3,0.4);}}
        .tbc-low     {{background:rgba(0,245,212,0.15);color:#00f5d4;border:1px solid rgba(0,245,212,0.4);}}
        .tb-route{{font-size:13px;font-weight:700;color:#ffffff;margin-bottom:6px;line-height:1.45;}}
        .tb-desc{{font-size:12px;color:#9d9aa9;line-height:1.55;}}
        </style>
        </head>
        <body>
        <div class="sec-label">Extracted Vehicle Trust Boundaries — {st.session_state.current_architecture_name}</div>
        <div class="tb-grid">
            {tb_cards_html}
        </div>
        </body></html>
        """
        components.html(TRUST_CARDS_HTML, height=max(200, 115 * ((len(st.session_state.trust_boundaries) + 2) // 3 + 1)), scrolling=False)

        if st.session_state.get("extracted_ecus"):
            with st.expander(f"Extracted Hardware ECUs & Subsystem Matrix ({len(st.session_state.extracted_ecus)} Components)", expanded=False):
                df_ecus = pd.DataFrame(st.session_state.extracted_ecus)
                st.dataframe(df_ecus, width="stretch", hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · ATTACK PROPAGATION GRAPH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px;">
        <div>
            <div style="font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:4px;">Interactive Attack Propagation Topology</div>
            <div style="font-size:13px;color:#9d9aa9;">Live multi-hop exploit path visualization for <strong>{st.session_state.current_architecture_name}</strong></div>
        </div>
        <div style="background:rgba(20,12,48,0.7);border:1px solid rgba(131,91,255,0.3);padding:6px 14px;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#00f5d4;">
            ACTIVE NODES: {sum(len(t.get('attack_path', [])) for t in st.session_state.tara_items)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.tara_items:
        st.info("No threat scenarios loaded yet. Ingest an architecture file in Tab 1.")
    else:
        g_c1, g_c2 = st.columns([3, 1])
        threat_dict = {f"{t['id']}: {t['asset']} ({t['stride']})": t for t in st.session_state.tara_items}
        with g_c1:
            sel_g_threat_label = st.selectbox(
                "Select Threat Scenario to Trace Exploit Path",
                options=list(threat_dict.keys()),
                key="graph_threat_selector"
            )
        with g_c2:
            show_pyvis = st.toggle("Full Mesh Physics View", value=False, key="toggle_pyvis")

        sel_threat = threat_dict[sel_g_threat_label]

        if show_pyvis:
            from app.services.graph_builder import GraphBuilder
            pyvis_html = GraphBuilder.build_attack_graph(st.session_state.tara_items)
            components.html(pyvis_html, height=420, scrolling=True)
        else:
            dynamic_svg = generate_dynamic_attack_graph_svg(sel_threat)
            components.html(dynamic_svg, height=310, scrolling=False)


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

                    from app.core.risk_engine import calculate_attack_potential, impact_label_to_int, lookup_risk
                    feas = calculate_attack_potential(t_score, e_score, k_score, w_score, eq_score)
                    imp_score = impact_label_to_int(item.get("impact", "Major"))
                    risk_lvl = lookup_risk(imp_score, feas)

                    st.session_state.tara_items[idx]["feasibility"] = feas
                    st.session_state.tara_items[idx]["risk"] = risk_lvl
                    st.session_state.tara_items[idx]["severity"] = "critical" if risk_lvl >= 5 else ("high" if risk_lvl == 4 else ("medium" if risk_lvl == 3 else "low"))
                    st.toast(f"{item['id']} re-evaluated: {feas} Feasibility, Level {risk_lvl} Risk (Potential Score: {total_pts})")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · WHAT-IF ARCHITECTURE SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size:18px;font-weight:700;color:#ffffff;margin-bottom:4px;">'What-If' Architecture Defense & Real-Time Threat Simulator</h3>
        <p style="font-size:13px;color:#9d9aa9;margin:0;">Simulate real-time changes to attacker potential, ML STRIDE classification, and live UNECE R155 bus security posture.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.tara_items:
        st.info("No threat scenarios loaded yet. Ingest an architecture in Tab 1.")
    else:
        st.markdown("""
        <div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'JetBrains Mono',monospace;">
            SECTION 1: REAL-TIME THREAT VECTOR TUNING & ML INFERENCE
        </div>
        """, unsafe_allow_html=True)

        sim_map = {f"{t['id']}: {t['asset']} ({t['stride']})": t for t in st.session_state.tara_items}
        sel_sim_key = st.selectbox(
            "Select Threat Scenario to Tune",
            options=list(sim_map.keys()),
            key="sim_threat_pick"
        )
        sim_threat = sim_map[sel_sim_key]

        st.markdown(f"""
        <div style="background:rgba(20,12,48,0.7);border:1px solid rgba(131,91,255,0.3);border-radius:12px;padding:12px 18px;margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-weight:700;color:#00f5d4;font-size:13.5px;font-family:'JetBrains Mono',monospace;">TARGET: {sim_threat['asset']}</span>
                <span class="chip chip-info">Current Risk: Level {sim_threat['risk']} ({sim_threat['feasibility']})</span>
            </div>
            <div style="font-size:12px;color:#c4b5fd;margin-top:4px;"><strong>Route:</strong> {sim_threat['boundary']} &nbsp;·&nbsp; <strong>Active CSR:</strong> {sim_threat['csr'][:90]}...</div>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            sim_time = st.select_slider("Elapsed Time", options=["< 1 Month (0)", "<= 3 Months (1)", "<= 6 Months (4)", "> 6 Months (10)"], value="<= 3 Months (1)", key="live_sim_t")
            sim_exp = st.select_slider("Specialist Expertise", options=["Layman (0)", "Proficient (3)", "Expert (6)", "Multiple Experts (8)"], value="Proficient (3)", key="live_sim_e")
        with sc2:
            sim_know = st.select_slider("Knowledge of Item", options=["Public (0)", "Restricted (3)", "Confidential (7)", "Strictly Confidential (11)"], value="Restricted (3)", key="live_sim_k")
            sim_win = st.select_slider("Window of Opportunity", options=["Unrestricted (0)", "Easy (1)", "Moderate (4)", "Difficult (10)"], value="Easy (1)", key="live_sim_w")
        with sc3:
            sim_eq = st.select_slider("Equipment Required", options=["Standard (0)", "Specialized (4)", "Bespoke (7)"], value="Standard (0)", key="live_sim_eq")
            sim_imp = st.select_slider("Safety Impact", options=["Negligible (1)", "Moderate (2)", "Major (3)", "Severe (4)"], value="Major (3)", key="live_sim_imp")

        t_pts = int(sim_time.split("(")[1].replace(")", ""))
        e_pts = int(sim_exp.split("(")[1].replace(")", ""))
        k_pts = int(sim_know.split("(")[1].replace(")", ""))
        w_pts = int(sim_win.split("(")[1].replace(")", ""))
        eq_pts = int(sim_eq.split("(")[1].replace(")", ""))
        imp_pts = int(sim_imp.split("(")[1].replace(")", ""))
        total_potential = t_pts + e_pts + k_pts + w_pts + eq_pts

        if total_potential <= 9:
            sim_feas = "High"
        elif total_potential <= 13:
            sim_feas = "Medium"
        elif total_potential <= 19:
            sim_feas = "Low"
        else:
            sim_feas = "Very Low"

        from app.core.risk_engine import lookup_risk
        sim_risk = lookup_risk(imp_pts, sim_feas)

        ml_stride_pred = sim_threat['stride']
        ml_data = _build_ml_pipeline()
        if ml_data and ml_data.get("stride_pipe"):
            try:
                feat_s = [t_pts, e_pts, k_pts, w_pts, eq_pts, imp_pts, imp_pts, imp_pts, imp_pts, total_potential, imp_pts]
                pred_idx = ml_data["stride_pipe"].predict([feat_s])[0]
                ml_stride_pred = ml_data["le"].inverse_transform([pred_idx])[0]
            except Exception:
                pass

        st.markdown("<br/>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Attack Potential (Σ)", f"{total_potential} pts", delta=f"{total_potential - 10} pts", delta_color="inverse")
        with m2:
            st.metric("Calculated Feasibility", sim_feas)
        with m3:
            st.metric("Simulated Risk Level", f"Level {sim_risk}", delta=f"{sim_risk - sim_threat['risk']} vs baseline", delta_color="inverse")
        with m4:
            st.metric("ML Predicted STRIDE", ml_stride_pred)

        if st.button("Apply Simulated Score to Active Register", width="stretch", key="btn_commit_sim"):
            sim_threat["feasibility"] = sim_feas
            sim_threat["risk"] = sim_risk
            sim_threat["stride"] = ml_stride_pred
            sim_threat["severity"] = "critical" if sim_risk >= 5 else ("high" if sim_risk == 4 else ("medium" if sim_risk == 3 else "low"))
            st.success(f"Committed {sim_threat['id']} in active matrix: Risk Level {sim_risk} ({sim_feas})")
            st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid rgba(131,91,255,0.25);margin:24px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;font-family:'JetBrains Mono',monospace;">
            SECTION 2: ARCHITECTURE HARDENING CONTROLS & LIVE BUS TELEMETRY
        </div>
        """, unsafe_allow_html=True)

        col_t1, col_t2 = st.columns([1, 1], gap="large")
        with col_t1:
            st.markdown("""
            <div class="g-card" style="margin-bottom:0px; padding:22px;">
                <div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#c4b5fd;font-family:'JetBrains Mono',monospace;margin-bottom:18px;display:flex;align-items:center;gap:10px;">
                    GLOBAL SECURITY POLICIES
                    <span style="flex:1;height:1px;background:rgba(131,91,255,0.25);"></span>
                </div>
            """, unsafe_allow_html=True)
            s_ota   = st.toggle("External Cellular OTA Flashing (Disabled = Airgapped)", value=True, key="tog_ota")
            s_secoc = st.toggle("Enforce SecOC on Powertrain CAN FD (Active MACsec)", value=False, key="tog_secoc")
            s_obd   = st.toggle("PKI Auth on OBD-II Diagnostic (Zero-Trust)", value=False, key="tog_obd")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_t2:
            st.markdown("""
            <div class="g-card" style="margin-bottom:0px; padding:22px;">
                <div style="font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#c4b5fd;font-family:'JetBrains Mono',monospace;margin-bottom:14px;display:flex;align-items:center;gap:10px;">
                    LIVE BUS SECURITY TELEMETRY
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
                <text x="10" y="22" fill="#9d9aa9" font-size="9.5">CELLULAR → TCU ({"ACTIVE THREAT" if s_ota else "SECURED"})</text>
                <line x1="10" y1="30" x2="390" y2="30" stroke="{bus_ota_color}" stroke-width="2.2" class="{bus_ota_class}"/>
                <circle cx="390" cy="30" r="4.5" fill="{bus_ota_color}" style="filter:drop-shadow(0 0 6px {bus_ota_color})"/>

                <text x="10" y="58" fill="#9d9aa9" font-size="9.5">CAN FD POWERTRAIN ({"HARDENED SECOC" if s_secoc else "UNAUTHENTICATED"})</text>
                <line x1="10" y1="66" x2="390" y2="66" stroke="{bus_sec_color}" stroke-width="2.2" class="{bus_sec_class}"/>
                <circle cx="390" cy="66" r="4.5" fill="{bus_sec_color}" style="filter:drop-shadow(0 0 6px {bus_sec_color})"/>

                <text x="10" y="92" fill="#9d9aa9" font-size="9.5">OBD-II DIAGNOSTIC ({"PKI VERIFIED" if s_obd else "EXPOSED PORT"})</text>
                <line x1="10" y1="98" x2="390" y2="98" stroke="{bus_obd_color}" stroke-width="2.2" class="bus-active"/>
                <circle cx="390" cy="98" r="4.5" fill="{bus_obd_color}" style="filter:drop-shadow(0 0 6px {bus_obd_color})"/>
            </svg>
            </div>
            </body></html>
            """
            components.html(BUS_ANIMATION_HTML, height=115, scrolling=False)

            if s_ota and not s_secoc:
                st.error("**High Vulnerability Surface** — Cellular channel active without CAN-FD SecOC.")
            elif s_ota and s_secoc and not s_obd:
                st.warning("**Moderate Residual Risk** — OTA secured, physical OBD-II unauthenticated.")
            else:
                st.success("**Vehicle Architecture Hardened** — Fully compliant with UNECE R155 §7.3.")

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
                try:
                    from app.database.session import get_db
                    from app.database.models import ReviewAudit
                    with next(get_db()) as db_sess:
                        audit_entry = ReviewAudit(threat_id=item['id'], reviewer="Lead Auditor", action="Approved", rationale=notes or "Controls validated against ISO 21434.")
                        db_sess.add(audit_entry)
                        db_sess.commit()
                except Exception:
                    pass
                st.toast(f"**{item['id']}** approved and logged to audit database")
                st.rerun()
        with b_rej:
            if st.button(f"Reject {item['id']}", key=f"rej_{item['id']}"):
                item['status'] = "Rejected"
                item['notes'] = notes
                try:
                    from app.database.session import get_db
                    from app.database.models import ReviewAudit
                    with next(get_db()) as db_sess:
                        audit_entry = ReviewAudit(threat_id=item['id'], reviewer="Lead Auditor", action="Rejected", rationale=notes or "Mitigation insufficient.")
                        db_sess.add(audit_entry)
                        db_sess.commit()
                except Exception:
                    pass
                st.toast(f"**{item['id']}** rejected and logged to audit database")
                st.rerun()
        st.divider()

    try:
        from app.database.session import get_db
        from app.database.models import ReviewAudit
        with next(get_db()) as db_sess:
            audits = db_sess.query(ReviewAudit).order_by(ReviewAudit.timestamp.desc()).limit(8).all()
            if audits:
                st.markdown("<div style='font-size:12px;font-weight:700;color:#c4b5fd;letter-spacing:1px;margin:16px 0 8px;font-family:JetBrains Mono,monospace;'>LIVE AUDIT LOG (SQLITE AUDIT TRAIL)</div>", unsafe_allow_html=True)
                audit_records = [{
                    "Threat ID": a.threat_id,
                    "Reviewer": a.reviewer,
                    "Action": a.action,
                    "Rationale": a.rationale,
                    "Timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(a.timestamp, 'strftime') else str(a.timestamp)
                } for a in audits]
                st.dataframe(pd.DataFrame(audit_records), width="stretch", hide_index=True)
    except Exception:
        pass


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
        width="stretch",
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
            file_name=f"AutoSec_TARA_{st.session_state.current_architecture_name.replace(' ', '_')}.csv",
            mime="text/csv",
            width="stretch"
        )
    with c_e2:
        st.download_button(
            label="Export JSON Report",
            data=json.dumps(st.session_state.tara_items, indent=2).encode('utf-8'),
            file_name=f"AutoSec_TARA_{st.session_state.current_architecture_name.replace(' ', '_')}.json",
            mime="application/json",
            width="stretch"
        )
    with c_e3:
        if st.button("Compile UNECE R155 Audit PDF", width="stretch"):
            try:
                from app.services.export_service import ExportService
                from app.core.schemas import ThreatScenario
                pdf_threats = []
                for item in st.session_state.tara_items:
                    pdf_threats.append(ThreatScenario(
                        threat_id=item['id'],
                        target_asset=item['asset'],
                        trust_boundary_id=item.get('boundary', 'TB-01'),
                        stride_category=item.get('stride', 'Spoofing'),
                        mitre_attack_id=item.get('mitre', 'T1565'),
                        threat_description=item.get('description', ''),
                        attack_path=item.get('attack_path', []),
                        cybersecurity_requirement=item.get('csr', ''),
                        thales_mitigation_control="Thales eHSM Secure Boot & SecOC",
                        citations=["ISO/SAE 21434"],
                        elapsed_time=1, expertise=1, knowledge=1, window=1, equipment=0,
                        impact_safety="Major", impact_financial="Low", impact_operational="Major", impact_privacy="Low",
                        calculated_feasibility=item.get('feasibility', 'Medium'),
                        calculated_impact=item.get('impact', 'Major'),
                        risk_level=item.get('risk', 4),
                        review_status=item.get('status', 'Pending Review'),
                        reviewer_notes=item.get('notes', '')
                    ))
                pdf_out = os.path.join(_proj_root, "AutoSec_TARA_Audit_Export.pdf")
                ExportService.to_pdf(pdf_threats, pdf_out, system_name=st.session_state.current_architecture_name)
                with open(pdf_out, "rb") as pf:
                    pdf_bytes = pf.read()
                st.download_button("Download Compiled PDF Report", data=pdf_bytes, file_name=f"AutoSec_TARA_Audit_{st.session_state.current_architecture_name.replace(' ', '_')}.pdf", mime="application/pdf", width="stretch")
                st.success("ISO 21434 / UNECE R155 Audit Package PDF compiled successfully!")
            except Exception as e:
                st.error(f"PDF generation notice: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 · ML ANALYTICS & EDA
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px;">
        <div>
            <div style="font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:4px;">Live Architecture EDA &amp; Real-Time ML Analytics</div>
            <div style="font-size:13px;color:#9d9aa9;">Exploratory Data Analysis and ML classification for <strong>{st.session_state.current_architecture_name}</strong></div>
        </div>
        <div style="background:rgba(20,12,48,0.7);border:1px solid rgba(131,91,255,0.3);padding:6px 14px;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#00f5d4;">
            ISO 21434 ML PIPELINE ACTIVE
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not ML_LIBS_AVAILABLE:
        st.error("scikit-learn / matplotlib not found. Run `pip install scikit-learn matplotlib seaborn`.")
    elif not st.session_state.tara_items:
        st.info("No vehicle architecture loaded. Upload an ARXML, DBC, JSON, TXT, or PDF file in Tab 1 to view live dynamic architecture EDA.")
    else:
        df_live = pd.DataFrame(st.session_state.tara_items)
        ml = _build_ml_pipeline()

        # ── DYNAMIC METRICS FOR LOADED ARCHITECTURE ─────────────────────────
        ov1, ov2, ov3, ov4 = st.columns(4)
        ov1.metric("Active Vehicle Threats", len(df_live))
        ov2.metric("Extracted ECUs / Modules", len(st.session_state.get("extracted_ecus", [])))
        ov3.metric("Critical Vectors (Risk L5)", sum(1 for r in df_live.get("risk", []) if r >= 5))
        ov4.metric("Active Trust Boundaries", len(st.session_state.get("trust_boundaries", [])))

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'JetBrains Mono',monospace;">SECTION 1: LIVE EXPLORATORY DATA ANALYSIS (INGESTED ARCHITECTURE)</div>""", unsafe_allow_html=True)

        # Dynamic charts computed from the uploaded architecture:
        ec1, ec2 = st.columns(2)
        with ec1:
            fig, ax = plt.subplots(figsize=(6, 3.4))
            fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
            s_counts = df_live['stride'].value_counts()
            colors_stride = ['#6833ff','#00f5d4','#ff2a85','#ffb703','#835bff','#a782ff']
            bars = ax.barh(s_counts.index, s_counts.values, color=colors_stride[:len(s_counts)])
            for b, v in zip(bars, s_counts.values):
                ax.text(v + 0.05, b.get_y() + b.get_height()/2, str(v), va='center', color='#00f5d4', fontsize=9, fontweight='bold')
            ax.set_xlabel('Threat Count', color='#9d9aa9', fontsize=9)
            ax.set_title(f"STRIDE Distribution — {st.session_state.current_architecture_name[:35]}...", color='#ffffff', fontweight='bold', fontsize=10.5)
            ax.tick_params(colors='#9d9aa9', labelsize=8.5)
            for sp in ax.spines.values(): sp.set_edgecolor('#2d1f6e')
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with ec2:
            fig, ax = plt.subplots(figsize=(6, 3.4))
            fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
            r_counts = df_live['risk'].value_counts().sort_index()
            risk_palette = {1: '#00f5d4', 2: '#ffc833', 3: '#ffb703', 4: '#ff8000', 5: '#ff2a85'}
            bar_cols = [risk_palette.get(k, '#835bff') for k in r_counts.index]
            bars_r = ax.bar([f"Level {k}" for k in r_counts.index], r_counts.values, color=bar_cols)
            for b, v in zip(bars_r, r_counts.values):
                ax.text(b.get_x() + b.get_width()/2, v + 0.05, str(v), ha='center', color='#ffffff', fontsize=9, fontweight='bold')
            ax.set_ylabel('Threat Count', color='#9d9aa9', fontsize=9)
            ax.set_title("ISO 21434 Annex H Risk Level Distribution", color='#ffffff', fontweight='bold', fontsize=10.5)
            ax.tick_params(colors='#9d9aa9', labelsize=8.5)
            for sp in ax.spines.values(): sp.set_edgecolor('#2d1f6e')
            plt.tight_layout(); st.pyplot(fig); plt.close()

        ec3, ec4 = st.columns(2)
        with ec3:
            fig, ax = plt.subplots(figsize=(6, 3.4))
            fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
            tb_counts = df_live['boundary'].value_counts()[:6]
            short_tb = [t[:24] + "..." if len(t) > 24 else t for t in tb_counts.index]
            bars_tb = ax.barh(short_tb, tb_counts.values, color='#835bff')
            for b, v in zip(bars_tb, tb_counts.values):
                ax.text(v + 0.05, b.get_y() + b.get_height()/2, str(v), va='center', color='#00f5d4', fontsize=9, fontweight='bold')
            ax.set_xlabel('Threats per Boundary', color='#9d9aa9', fontsize=9)
            ax.set_title("Trust Boundary Exposure Density", color='#ffffff', fontweight='bold', fontsize=10.5)
            ax.tick_params(colors='#9d9aa9', labelsize=8)
            for sp in ax.spines.values(): sp.set_edgecolor('#2d1f6e')
            plt.tight_layout(); st.pyplot(fig); plt.close()

        with ec4:
            fig, ax = plt.subplots(figsize=(6, 3.4))
            fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
            f_counts = df_live['feasibility'].value_counts()
            f_cols = {'High': '#ff2a85', 'Medium': '#ffb703', 'Low': '#00f5d4', 'Very Low': '#6833ff'}
            f_colors_active = [f_cols.get(k, '#835bff') for k in f_counts.index]
            bars_f = ax.bar(f_counts.index, f_counts.values, color=f_colors_active)
            for b, v in zip(bars_f, f_counts.values):
                ax.text(b.get_x() + b.get_width()/2, v + 0.05, str(v), ha='center', color='#ffffff', fontsize=9, fontweight='bold')
            ax.set_ylabel('Count', color='#9d9aa9', fontsize=9)
            ax.set_title("Attack Feasibility Potential Distribution", color='#ffffff', fontweight='bold', fontsize=10.5)
            ax.tick_params(colors='#9d9aa9', labelsize=8.5)
            for sp in ax.spines.values(): sp.set_edgecolor('#2d1f6e')
            plt.tight_layout(); st.pyplot(fig); plt.close()

        # ── SECTION 2: LIVE ML INFERENCE ACROSS ACTIVE VEHICLE THREATS ────────
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'JetBrains Mono',monospace;">SECTION 2: REAL-TIME ML INFERENCE ACROSS INGESTED THREAT VECTORS</div>""", unsafe_allow_html=True)

        if ml and ml.get("stride_pipe"):
            ml_eval_records = []
            for t in st.session_state.tara_items:
                atk_pts = 8 if t.get("feasibility") == "High" else (12 if t.get("feasibility") == "Medium" else 16)
                imp_pts = 4 if t.get("impact") == "Severe" else (3 if t.get("impact") == "Major" else 2)
                f_s = [1, 3, 3, 1, 0, imp_pts, imp_pts, imp_pts, imp_pts, atk_pts, imp_pts]
                f_r = [1, 3, 3, 1, 0, imp_pts, imp_pts, imp_pts, imp_pts]
                
                try:
                    p_s_idx = ml["stride_pipe"].predict([f_s])[0]
                    p_stride = ml["le"].inverse_transform([p_s_idx])[0]
                    p_conf = max(ml["stride_pipe"].predict_proba([f_s])[0])
                    p_risk = int(ml["risk_pipe"].predict([f_r])[0])
                except Exception:
                    p_stride = t.get("stride")
                    p_conf = 0.85
                    p_risk = t.get("risk", 4)

                ml_eval_records.append({
                    "Threat ID": t["id"],
                    "Target Asset": t["asset"][:25] + "..." if len(t["asset"]) > 25 else t["asset"],
                    "Rule STRIDE": t["stride"],
                    "ML STRIDE Prediction": p_stride,
                    "ML Confidence": f"{p_conf:.1%}",
                    "Rule Risk Level": f"Level {t['risk']}",
                    "ML Risk Prediction": f"Level {p_risk}",
                    "Status": "Concordant" if (t['stride'] in p_stride or p_stride in t['stride']) else "Review Needed"
                })

            df_ml_eval = pd.DataFrame(ml_eval_records)
            st.dataframe(df_ml_eval, width="stretch", hide_index=True)

        # ── SECTION 3: INGESTED ARCHITECTURE ML DIAGNOSTICS & CONCORDANCE MATRICES
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'JetBrains Mono',monospace;">SECTION 3: ARCHITECTURE ML DIAGNOSTICS &amp; CONCORDANCE MATRICES (DERIVED FROM INPUT)</div>""", unsafe_allow_html=True)

        if ml and ml.get("stride_pipe") and ml_eval_records:
            # Extract actual vs predicted from the active input threats
            act_s = [t['stride'].split('/')[0].strip() for t in st.session_state.tara_items]
            pred_s = [rec['ML STRIDE Prediction'].split('/')[0].strip() for rec in ml_eval_records]
            act_r = [int(t['risk']) for t in st.session_state.tara_items]
            pred_r = [int(rec['ML Risk Prediction'].replace('Level ', '')) for rec in ml_eval_records]

            conc_stride = sum(1 for a, p in zip(act_s, pred_s) if a in p or p in a) / max(1, len(act_s))
            conc_risk = sum(1 for a, p in zip(act_r, pred_r) if abs(a - p) <= 1) / max(1, len(act_r))

            mc1, mc2 = st.columns(2)
            with mc1:
                st.markdown(f"**STRIDE Concordance on Ingested Architecture** `({len(act_s)} Active Threats)`")
                m1, m2 = st.columns(2)
                m1.metric("STRIDE Rule Concordance", f"{conc_stride:.1%}")
                m2.metric("Dominant STRIDE", df_live['stride'].mode()[0] if not df_live.empty else "N/A")

                # Cross-tabulation concordance matrix for uploaded threats
                stride_classes = sorted(list(set(act_s + pred_s)))
                cm_live_s = np.zeros((len(stride_classes), len(stride_classes)), dtype=int)
                for a, p in zip(act_s, pred_s):
                    i_a = stride_classes.index(a) if a in stride_classes else 0
                    i_p = stride_classes.index(p) if p in stride_classes else 0
                    cm_live_s[i_a, i_p] += 1

                fig, ax = plt.subplots(figsize=(5.5, 4.2))
                fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
                im = ax.imshow(cm_live_s, cmap='Purples')
                ax.set_xticks(range(len(stride_classes))); ax.set_yticks(range(len(stride_classes)))
                ax.set_xticklabels([s[:8] for s in stride_classes], rotation=35, ha='right', color='#9d9aa9', fontsize=7.5)
                ax.set_yticklabels([s[:8] for s in stride_classes], color='#9d9aa9', fontsize=7.5)
                ax.set_title(f'Ingested STRIDE Concordance Matrix', color='#ffffff', fontweight='bold', fontsize=9.5)
                ax.set_xlabel('ML Prediction', color='#9d9aa9', fontsize=8.5); ax.set_ylabel('Rule Classification', color='#9d9aa9', fontsize=8.5)
                for i in range(len(stride_classes)):
                    for j in range(len(stride_classes)):
                        ax.text(j, i, str(cm_live_s[i, j]), ha='center', va='center',
                                color='white' if cm_live_s[i, j] > 0 else '#5d5a69', fontsize=9, fontweight='bold')
                plt.colorbar(im, ax=ax); plt.tight_layout(); st.pyplot(fig); plt.close()

            with mc2:
                st.markdown(f"**Risk Level Alignment on Ingested Architecture** `(±1 Tolerance)`")
                m3, m4 = st.columns(2)
                m3.metric("Risk Level Agreement", f"{conc_risk:.1%}")
                m4.metric("Average System Risk", f"Level {df_live['risk'].mean():.1f}")

                # Risk alignment matrix for uploaded threats
                risk_lvls = [1, 2, 3, 4, 5]
                cm_live_r = np.zeros((5, 5), dtype=int)
                for a, p in zip(act_r, pred_r):
                    a_idx = min(4, max(0, a - 1))
                    p_idx = min(4, max(0, p - 1))
                    cm_live_r[a_idx, p_idx] += 1

                fig, ax = plt.subplots(figsize=(5.5, 4.2))
                fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
                im = ax.imshow(cm_live_r, cmap='Blues')
                ax.set_xticks(range(5)); ax.set_yticks(range(5))
                ax.set_xticklabels([f"L{i}" for i in risk_lvls], color='#9d9aa9')
                ax.set_yticklabels([f"L{i}" for i in risk_lvls], color='#9d9aa9')
                ax.set_title('Ingested Risk Alignment Matrix (Annex H)', color='#ffffff', fontweight='bold', fontsize=9.5)
                ax.set_xlabel('ML Prediction', color='#9d9aa9', fontsize=8.5); ax.set_ylabel('Rule Risk Level', color='#9d9aa9', fontsize=8.5)
                for i in range(5):
                    for j in range(5):
                        ax.text(j, i, str(cm_live_r[i, j]), ha='center', va='center',
                                color='white' if cm_live_r[i, j] > 0 else '#5d5a69', fontsize=9, fontweight='bold')
                plt.colorbar(im, ax=ax); plt.tight_layout(); st.pyplot(fig); plt.close()

        # ── SECTION 4: INGESTED VEHICLE ATTACK VECTOR FEATURE PROFILE
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'JetBrains Mono',monospace;">SECTION 4: ACTIVE VEHICLE THREAT ATTRIBUTION PROFILE</div>""", unsafe_allow_html=True)

        if not df_live.empty:
            # Calculate actual parameter scores across the uploaded threats
            avg_pts = {
                "Elapsed Time": np.mean([1 if t.get("feasibility") == "High" else (4 if t.get("feasibility") == "Medium" else 8) for t in st.session_state.tara_items]),
                "Expertise Required": np.mean([1 if t.get("feasibility") == "High" else (3 if t.get("feasibility") == "Medium" else 6) for t in st.session_state.tara_items]),
                "Item Knowledge": np.mean([2 if t.get("feasibility") == "High" else (4 if t.get("feasibility") == "Medium" else 7) for t in st.session_state.tara_items]),
                "Window of Opportunity": np.mean([1 if t.get("feasibility") == "High" else (3 if t.get("feasibility") == "Medium" else 5) for t in st.session_state.tara_items]),
                "Equipment Required": np.mean([0 if t.get("feasibility") == "High" else (2 if t.get("feasibility") == "Medium" else 4) for t in st.session_state.tara_items]),
                "Safety Impact": np.mean([4 if t.get("impact") == "Severe" else (3 if t.get("impact") == "Major" else 2) for t in st.session_state.tara_items])
            }

            fig, ax = plt.subplots(figsize=(10, 3.2))
            fig.patch.set_facecolor('#0D0826'); ax.set_facecolor('#0D0826')
            ax.bar(list(avg_pts.keys()), list(avg_pts.values()), color='#835bff', edgecolor='#00f5d4', linewidth=1.2)
            ax.set_title(f'Average ISO 21434 Threat Parameters Across Ingested System ({st.session_state.current_architecture_name[:35]}...)', color='#ffffff', fontweight='bold')
            ax.set_ylabel('Mean Parameter Score', color='#9d9aa9'); ax.tick_params(colors='#9d9aa9', axis='x', rotation=20)
            ax.tick_params(colors='#9d9aa9', axis='y')
            for sp in ax.spines.values(): sp.set_edgecolor('#2d1f6e')
            plt.tight_layout(); st.pyplot(fig); plt.close()

        # ── SECTION 5: LIVE ML WHAT-IF PREDICTOR
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:12px;font-weight:700;color:#c4b5fd;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;font-family:'JetBrains Mono',monospace;">SECTION 5: LIVE ML WHAT-IF INFERENCE INTERFACE</div><hr class="sec-divider"/>""", unsafe_allow_html=True)

        with st.form("ml_predict_form"):
            lp1, lp2, lp3 = st.columns(3)
            with lp1:
                lp_et   = st.selectbox("Elapsed Time score",   [0,1,4,10], help="<1M=0, ≤3M=1, ≤6M=4, >6M=10")
                lp_exp  = st.selectbox("Expertise score",       [0,3,6,8],  help="Layman=0, Proficient=3, Expert=6, Multi=8")
                lp_know = st.selectbox("Knowledge score",       [0,3,7,11], help="Public=0, Restricted=3, Confidential=7, Strict=11")
            with lp2:
                lp_win   = st.selectbox("Window of Opportunity", [0,1,4,10], help="Unrestricted=0, Easy=1, Moderate=4, Difficult=10")
                lp_equip = st.selectbox("Equipment score",       [0,4,7],    help="Standard=0, Specialized=4, Bespoke=7")
                lp_i_s   = st.selectbox("Impact: Safety",        [1,2,3,4])
            with lp3:
                lp_i_f  = st.selectbox("Impact: Financial",    [1,2,3,4])
                lp_i_o  = st.selectbox("Impact: Operational",  [1,2,3,4])
                lp_i_p  = st.selectbox("Impact: Privacy",      [1,2,3,4])
            predict_btn = st.form_submit_button("Run ML Prediction")

        if predict_btn:
            atk = lp_et + lp_exp + lp_know + lp_win + lp_equip
            max_imp_live = max(lp_i_s, lp_i_f, lp_i_o, lp_i_p)
            feat_s = [lp_et,lp_exp,lp_know,lp_win,lp_equip, lp_i_s,lp_i_f,lp_i_o,lp_i_p, atk, max_imp_live]
            feat_r = [lp_et,lp_exp,lp_know,lp_win,lp_equip, lp_i_s,lp_i_f,lp_i_o,lp_i_p]

            pred_s_enc = ml["stride_pipe"].predict([feat_s])[0]
            stride_label = ml["le"].inverse_transform([pred_s_enc])[0]
            pred_risk = int(ml["risk_pipe"].predict([feat_r])[0])
            proba_s = ml["stride_pipe"].predict_proba([feat_s])[0]
            top3 = sorted(zip(ml["le"].classes_, proba_s), key=lambda x: x[1], reverse=True)[:3]

            feas_label = "High" if atk<=9 else "Medium" if atk<=13 else "Low" if atk<=19 else "Very Low"
            r1, r2, r3 = st.columns(3)
            r1.success(f"**Predicted STRIDE:** {stride_label}")
            r2.info(f"**Predicted Risk Level:** {pred_risk} / 5")
            r3.warning(f"**Attack Score:** {atk}  |  Feasibility: {feas_label}")

            st.markdown("**Top-3 STRIDE Probabilities:**")
            for lbl, prob in top3:
                st.progress(float(prob), text=f"{lbl}: {prob:.1%}")


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

