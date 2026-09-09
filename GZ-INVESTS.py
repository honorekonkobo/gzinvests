#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GZ INVESTS - Tableau de Bord des Cours
=======================================
Double-cliquez sur ce fichier pour demarrer.
Python 3 doit etre installe (python.org)
"""

import http.server
import urllib.request
import urllib.error
import json
import threading
import time
import sys
import os
import datetime

PORT = int(os.environ.get('PORT', 8080))

# ─── PAGE HTML (embarquee) ────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GZ INVESTS - Cours des Metaux</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --gold: #C49A0A; --gold-2: #E8B800; --gold-3: #F5D060;
  --gold-bg: #FDF8EC; --dark: #1C1408; --dark-2: #3A2C10;
  --dark-3: #5C4820; --mid: #8C7440; --light: #F9F5EB;
  --white: #FFFFFF; --green: #1A7A45; --red: #C02030;
  --border: #E8DDB8;
}
html, body { width:100%; height:100%; background:var(--gold-bg); color:var(--dark); font-family:'Inter',sans-serif; overflow:hidden; }
.board { display:grid; grid-template-rows:64px 1fr 38px; height:100vh; }
.header { background:var(--dark); display:flex; align-items:center; padding:0 28px; gap:16px; position:relative; }
.header::after { content:''; position:absolute; bottom:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--gold) 0%,var(--gold-3) 50%,var(--gold) 100%); }
.header-logo-wrap { display:flex; align-items:center; gap:14px; }
.gz-logo-svg { width:40px; height:40px; filter:drop-shadow(0 0 8px rgba(196,154,10,0.4)); }
.header-brand { display:flex; flex-direction:column; }
.header-brand-gz { font-family:'Playfair Display',serif; font-size:20px; font-weight:700; color:var(--gold-2); letter-spacing:1px; line-height:1; }
.header-brand-sub { font-size:8.5px; font-weight:500; letter-spacing:3.5px; color:var(--mid); text-transform:uppercase; line-height:1; margin-top:3px; }
.header-sep { width:1px; height:28px; background:var(--dark-2); margin:0 8px; }
.header-tagline { font-size:10px; letter-spacing:2px; color:var(--mid); text-transform:uppercase; }
.header-right { margin-left:auto; display:flex; align-items:center; gap:20px; }
.live-pill { display:flex; align-items:center; gap:6px; padding:4px 12px; border:1px solid rgba(196,154,10,0.4); border-radius:20px; background:rgba(196,154,10,0.1); }
.live-dot { width:7px; height:7px; border-radius:50%; background:#4ECA80; animation:blink 2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(78,202,128,0.5);} 50%{opacity:0.6;box-shadow:0 0 0 5px rgba(78,202,128,0);} }
.live-text { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:600; letter-spacing:2px; color:#4ECA80; }
.hdr-clock { font-family:'JetBrains Mono',monospace; font-size:24px; font-weight:600; color:var(--white); letter-spacing:2px; }
.hdr-clock .ss { color:var(--mid); font-weight:400; }
.hdr-date-box { display:flex; flex-direction:column; align-items:flex-end; }
.hdr-day { font-size:11px; font-weight:600; color:var(--gold-2); letter-spacing:2px; text-transform:uppercase; }
.hdr-date-str { font-size:10px; color:var(--mid); letter-spacing:0.5px; margin-top:1px; }
.body { display:grid; grid-template-columns:1fr 300px; overflow:hidden; }
.left { padding:20px 24px; display:flex; flex-direction:column; gap:18px; overflow-y:auto; }
.spot-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.spot-card { background:var(--white); border:1px solid var(--border); border-radius:8px; overflow:hidden; box-shadow:0 2px 12px rgba(100,80,0,0.06); }
.spot-card-head { display:flex; align-items:center; justify-content:space-between; padding:10px 16px 9px; border-bottom:1px solid var(--border); background:var(--light); }
.spot-metal-name { font-size:13px; font-weight:700; letter-spacing:1.5px; color:var(--dark); }
.spot-metal-name span { color:var(--gold); }
.spot-usd-pill { font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--mid); background:var(--gold-bg); border:1px solid var(--border); padding:2px 8px; border-radius:4px; }
.spot-src { font-size:9px; font-weight:700; letter-spacing:2px; padding:2px 8px; border-radius:3px; background:rgba(196,154,10,0.12); color:var(--gold-2); border:1px solid rgba(196,154,10,0.25); }
.spot-usd-main { padding:12px 16px 10px; border-bottom:1px solid var(--border); background:var(--dark); display:flex; flex-direction:column; align-items:center; gap:3px; }
.spot-usd-label { font-size:8px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; color:var(--mid); }
.spot-usd-row { display:flex; align-items:baseline; gap:7px; }
.spot-usd-arrow { font-size:22px; font-weight:700; color:var(--gold-2); transition:color 0.5s; line-height:1; }
.spot-usd-arrow.up { color:#4ECA80; }
.spot-usd-arrow.dn { color:#E05060; }
.spot-usd-price { font-family:'JetBrains Mono',monospace; font-size:34px; font-weight:700; color:var(--white); letter-spacing:-1px; font-variant-numeric:tabular-nums; transition:color 0.5s; line-height:1; }
.spot-usd-price.up { color:#4ECA80; }
.spot-usd-price.dn { color:#E05060; }
.spot-usd-unit { font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--mid); }
.spot-usd-chg { font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:600; color:var(--gold-2); transition:color 0.5s; letter-spacing:0.5px; }
.spot-usd-chg.up { color:#4ECA80; }
.spot-usd-chg.dn { color:#E05060; }
.spot-cols { display:grid; grid-template-columns:1fr 1fr; }
.spot-side { padding:14px 16px; display:flex; flex-direction:column; gap:4px; }
.spot-side.buy-side { border-right:1px solid var(--border); }
.spot-side-label { font-size:9px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--mid); }
.spot-price { font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:700; line-height:1; font-variant-numeric:tabular-nums; letter-spacing:-0.5px; }
.spot-price.buy { color:var(--green); }
.spot-price.sell { color:var(--red); }
.spot-chg { display:inline-flex; align-items:center; gap:3px; font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:600; margin-top:2px; }
.spot-chg.up { color:var(--green); }
.spot-chg.dn { color:var(--red); }
.table-wrap { background:var(--white); border:1px solid var(--border); border-radius:8px; overflow:hidden; box-shadow:0 2px 12px rgba(100,80,0,0.06); flex:1; }
.table-head-bar { display:flex; align-items:center; justify-content:space-between; padding:11px 18px; background:var(--dark); }
.table-head-bar span { font-size:10px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:var(--gold-2); }
.table-head-bar .thb-right { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--mid); letter-spacing:1px; }
table.ctable { width:100%; border-collapse:collapse; }
table.ctable thead th { font-size:9px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--mid); padding:9px 18px; text-align:left; background:var(--light); border-bottom:1px solid var(--border); }
table.ctable thead th.r { text-align:right; }
table.ctable tbody tr { border-bottom:1px solid #F2EDD8; transition:background 0.15s; }
table.ctable tbody tr:last-child { border-bottom:none; }
table.ctable tbody tr:hover { background:var(--gold-bg); }
table.ctable tbody td { padding:11px 18px; font-size:13px; vertical-align:middle; }
.com-name { font-weight:600; color:var(--dark); display:flex; align-items:center; gap:8px; }
.com-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.com-tag { font-size:9.5px; font-weight:600; padding:1px 7px; border-radius:3px; background:var(--gold-bg); color:var(--gold); border:1px solid var(--border); letter-spacing:0.5px; }
.wt-cell { font-size:11px; color:var(--mid); letter-spacing:0.5px; }
.price-buy { font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; color:var(--green); text-align:right; font-variant-numeric:tabular-nums; }
.price-sell { font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; color:var(--red); text-align:right; font-variant-numeric:tabular-nums; }
.right { background:var(--dark); display:flex; flex-direction:column; align-items:center; padding:22px 18px; gap:18px; position:relative; overflow:hidden; }
.right::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--gold),var(--gold-3),var(--gold)); }
.right-logo-area { display:flex; flex-direction:column; align-items:center; gap:6px; }
.right-gz-ring { width:70px; height:70px; border:2px solid var(--gold); border-radius:50%; display:flex; align-items:center; justify-content:center; background:rgba(196,154,10,0.08); box-shadow:0 0 24px rgba(196,154,10,0.2),inset 0 0 16px rgba(196,154,10,0.06); }
.right-gz-text { font-family:'Playfair Display',serif; font-size:26px; font-weight:700; color:var(--gold-2); letter-spacing:1px; line-height:1; }
.right-invests { font-size:9px; font-weight:500; letter-spacing:5px; color:var(--mid); text-transform:uppercase; }
.right-clock-box { width:100%; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center; }
.rc-time { font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:600; color:var(--white); letter-spacing:2px; line-height:1; }
.rc-time .rc-ss { color:var(--mid); font-weight:400; font-size:20px; }
.rc-date { text-align:right; }
.rc-day { font-size:11px; font-weight:600; letter-spacing:2px; color:var(--gold-2); text-transform:uppercase; }
.rc-dmy { font-size:10px; color:var(--mid); margin-top:2px; letter-spacing:0.5px; }
.team-photo { width:100%; flex:1; min-height:0; border-radius:8px; border:1px solid rgba(196,154,10,0.2); background:rgba(255,255,255,0.03); display:flex; align-items:center; justify-content:center; max-height:120px; }
.team-photo-inner { display:flex; flex-direction:column; align-items:center; gap:6px; }
.team-icon { display:flex; gap:3px; }
.t-fig { width:14px; height:28px; background:var(--dark-2); border-radius:7px 7px 3px 3px; position:relative; }
.t-fig::before { content:''; position:absolute; top:-9px; left:50%; transform:translateX(-50%); width:10px; height:10px; background:var(--dark-2); border-radius:50%; }
.team-label-txt { font-size:8px; letter-spacing:2px; color:var(--dark-3); text-transform:uppercase; }
.bs-row { width:100%; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 16px; display:flex; flex-direction:column; gap:8px; }
.bs-title { font-size:9px; font-weight:600; letter-spacing:2px; color:var(--mid); text-transform:uppercase; text-align:center; }
.bs-bar-wrap { position:relative; height:10px; background:rgba(255,255,255,0.05); border-radius:5px; overflow:hidden; }
.bs-buy-fill { position:absolute; left:0; top:0; bottom:0; background:linear-gradient(90deg,var(--green) 0%,#2ECC80 100%); border-radius:5px 0 0 5px; width:62%; transition:width 2s ease; }
.bs-sell-fill { position:absolute; right:0; top:0; bottom:0; background:linear-gradient(270deg,var(--red) 0%,#E05060 100%); border-radius:0 5px 5px 0; width:38%; transition:width 2s ease; }
.bs-labels { display:flex; justify-content:space-between; align-items:center; }
.bs-buy-label { font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; color:var(--green); }
.bs-mid-label { font-size:9px; color:var(--mid); letter-spacing:1px; }
.bs-sell-label { font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; color:var(--red); }
.fx-strip { width:100%; display:flex; flex-direction:column; gap:5px; }
.fx-row { display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.04); }
.fx-row:last-child { border:none; }
.fx-pair { font-size:9px; color:var(--mid); letter-spacing:1.5px; text-transform:uppercase; }
.fx-val { font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:600; color:var(--gold-2); }
.ticker { background:var(--dark); border-top:2px solid var(--gold); display:flex; align-items:center; overflow:hidden; }
.ticker-tag { flex-shrink:0; padding:0 16px; height:100%; background:var(--gold); display:flex; align-items:center; font-size:10px; font-weight:700; letter-spacing:2px; color:var(--dark); }
.ticker-sep { width:0; height:0; border-top:38px solid var(--gold); border-right:16px solid transparent; flex-shrink:0; }
.ticker-track { flex:1; overflow:hidden; }
.ticker-inner { display:inline-flex; gap:0; white-space:nowrap; animation:tscroll 55s linear infinite; align-items:center; height:38px; }
@keyframes tscroll { from{transform:translateX(0);} to{transform:translateX(-50%);} }
.t-item { display:inline-flex; align-items:center; gap:6px; padding:0 28px 0 0; font-size:12px; }
.t-item-key { color:var(--gold-2); font-weight:600; font-size:10px; letter-spacing:1px; }
.t-item-val { font-family:'JetBrains Mono',monospace; font-size:12px; color:#C8C0A0; font-variant-numeric:tabular-nums; }
.t-dot { width:3px; height:3px; border-radius:50%; background:var(--dark-3); margin-left:28px; flex-shrink:0; }
</style>
</head>
<body>
<div class="board">
  <header class="header">
    <div class="header-logo-wrap">
      <svg class="gz-logo-svg" viewBox="0 0 40 40" fill="none">
        <circle cx="20" cy="20" r="19" stroke="#C49A0A" stroke-width="1.5" fill="rgba(196,154,10,0.06)"/>
        <text x="20" y="26" text-anchor="middle" font-family="Playfair Display,serif" font-size="15" font-weight="700" fill="#E8B800" letter-spacing="1">GZ</text>
      </svg>
      <div class="header-brand">
        <div class="header-brand-gz">GZ INVESTS</div>
        <div class="header-brand-sub">Gold &middot; Silver &middot; Precious Metals</div>
      </div>
    </div>
    <div class="header-sep"></div>
    <div class="header-tagline">Tableau de Bord des Cours</div>
    <div class="header-right">
      <div class="live-pill"><div class="live-dot"></div><span class="live-text">EN DIRECT</span></div>
      <div class="hdr-date-box"><div class="hdr-day" id="h-day"></div><div class="hdr-date-str" id="h-date"></div></div>
      <div class="hdr-clock" id="h-clock">--:--<span class="ss">:--</span></div>
    </div>
  </header>
  <div class="body">
    <div class="left">
      <div class="spot-row">
        <div class="spot-card">
          <div class="spot-card-head">
            <span class="spot-metal-name"><span>&#9670;</span> OR / GOLD</span>
            <span class="spot-src" id="g-src">SPOT</span>
          </div>
          <div class="spot-usd-main">
            <span class="spot-usd-label">Cours Dollar</span>
            <div class="spot-usd-row">
              <span class="spot-usd-arrow" id="g-arrow">&#8212;</span>
              <span class="spot-usd-price" id="g-usd-big">--</span>
              <span class="spot-usd-unit">/oz</span>
            </div>
            <span class="spot-usd-chg" id="g-usd-chg">&#177;0.00 USD</span>
          </div>
          <div class="spot-cols">
            <div class="spot-side buy-side">
              <span class="spot-side-label">Achat XOF</span>
              <span class="spot-price buy" id="g-buy-xof">--</span>
              <span class="spot-chg up">XOF / kg</span>
            </div>
            <div class="spot-side">
              <span class="spot-side-label">Vente XOF</span>
              <span class="spot-price sell" id="g-sell-xof">--</span>
              <span class="spot-chg dn">XOF / kg</span>
            </div>
          </div>
        </div>
        <div class="spot-card">
          <div class="spot-card-head">
            <span class="spot-metal-name" style="color:var(--dark-3)"><span style="color:#607080">&#9670;</span> ARGENT / SILVER</span>
            <span class="spot-src" id="s-src">SPOT</span>
          </div>
          <div class="spot-usd-main">
            <span class="spot-usd-label">Cours Dollar</span>
            <div class="spot-usd-row">
              <span class="spot-usd-arrow" id="s-arrow">&#8212;</span>
              <span class="spot-usd-price" id="s-usd-big">--</span>
              <span class="spot-usd-unit">/oz</span>
            </div>
            <span class="spot-usd-chg" id="s-usd-chg">&#177;0.00 USD</span>
          </div>
          <div class="spot-cols">
            <div class="spot-side buy-side">
              <span class="spot-side-label">Achat XOF</span>
              <span class="spot-price buy" id="s-buy-xof">--</span>
              <span class="spot-chg up">XOF / kg</span>
            </div>
            <div class="spot-side">
              <span class="spot-side-label">Vente XOF</span>
              <span class="spot-price sell" id="s-sell-xof">--</span>
              <span class="spot-chg dn">XOF / kg</span>
            </div>
          </div>
        </div>
      </div>
      <div class="table-wrap">
        <div class="table-head-bar">
          <span>Cours des M&eacute;taux Pr&eacute;cieux</span>
          <span class="thb-right" id="table-ts">XOF</span>
        </div>
        <table class="ctable">
          <thead><tr><th>Commodit&eacute;</th><th>Poids</th><th class="r">Achat XOF</th><th class="r">Vente XOF</th></tr></thead>
          <tbody id="ctbody"></tbody>
        </table>
      </div>
    </div>
    <div class="right">
      <div class="right-logo-area">
        <div class="right-gz-ring">
          <svg viewBox="0 0 60 60" width="60" height="60" fill="none">
            <circle cx="30" cy="30" r="29" stroke="#C49A0A" stroke-width="1" fill="none"/>
            <text x="30" y="38" text-anchor="middle" font-family="Playfair Display,serif" font-size="22" font-weight="700" fill="#E8B800">GZ</text>
          </svg>
        </div>
        <div style="text-align:center">
          <div class="right-gz-text">GZ INVESTS</div>
          <div class="right-invests">Precious Metals Trading</div>
        </div>
      </div>
      <div class="right-clock-box">
        <div class="rc-time" id="rc-time">--:--<span class="rc-ss">:--</span></div>
        <div class="rc-date"><div class="rc-day" id="rc-day"></div><div class="rc-dmy" id="rc-dmy"></div></div>
      </div>
      <div class="team-photo">
        <div class="team-photo-inner">
          <div class="team-icon">
            <div class="t-fig"></div><div class="t-fig"></div><div class="t-fig"></div>
            <div class="t-fig"></div><div class="t-fig"></div><div class="t-fig"></div>
          </div>
          <div class="team-label-txt">Notre &Eacute;quipe</div>
        </div>
      </div>
      <div class="bs-row">
        <div class="bs-title">Acheteurs &middot; Vendeurs</div>
        <div class="bs-bar-wrap"><div class="bs-buy-fill" id="bs-buy"></div><div class="bs-sell-fill" id="bs-sell"></div></div>
        <div class="bs-labels">
          <span class="bs-buy-label" id="bs-buy-pct">62%</span>
          <span class="bs-mid-label">March&eacute;</span>
          <span class="bs-sell-label" id="bs-sell-pct">38%</span>
        </div>
      </div>
      <div class="fx-strip">
        <div class="fx-row"><span class="fx-pair">USD / XOF</span><span class="fx-val" id="fx-usdxof">--</span></div>
        <div class="fx-row"><span class="fx-pair">EUR / XOF</span><span class="fx-val">655.957</span></div>
        <div class="fx-row"><span class="fx-pair">EUR / USD</span><span class="fx-val" id="fx-eurusd">--</span></div>
      </div>
    </div>
  </div>
  <div class="ticker">
    <div class="ticker-tag">GZ INVESTS NEWS</div>
    <div class="ticker-sep"></div>
    <div class="ticker-track"><div class="ticker-inner" id="ticker-inner"></div></div>
  </div>
</div>
<script>
const METALS_URL  = '/api/metals';
const FX_URL      = '/api/fx';
const METALS_MS   = 3000;    // cours or/argent : toutes les 3 secondes
const FX_MS       = 3000;    // taux de change  : toutes les 3 secondes
const DISPLAY_MS  = 1000;    // recalcul XOF    : chaque seconde (pas d'API)

let goldBid=4403.14, goldAsk=4404.26, goldUSD=4403.14;
let silverBid=66.29, silverAsk=66.30, silverUSD=66.29;
let eurUsd=1.16;

const EUR_XOF=655.957, OZ_PER_KG=32.1507, TTB_OZ=3.7493;
function xofPerUsd(){return EUR_XOF/eurUsd;}
function gKg(p=0.9999){return goldBid*xofPerUsd()*OZ_PER_KG*(p/0.9999);}
function gKgS(p=0.9999){return goldAsk*xofPerUsd()*OZ_PER_KG*(p/0.9999);}
function gTtb(){return goldBid*xofPerUsd()*TTB_OZ;}
function gTtbS(){return goldAsk*xofPerUsd()*TTB_OZ;}
function gG(){return gKg()/1000;}
function gGS(){return gKgS()/1000;}
function sKg(){return silverBid*xofPerUsd()*OZ_PER_KG;}
function sKgS(){return silverAsk*xofPerUsd()*OZ_PER_KG;}
function fmt(n){if(!isFinite(n)||n<=0)return '--'; return Math.round(n).toLocaleString('fr-FR');}
function fmtD(n,d){if(!isFinite(n))return '--'; return n.toLocaleString('fr-FR',{minimumFractionDigits:d,maximumFractionDigits:d});}

function setLive(on){
  const pill=document.querySelector('.live-pill');
  const txt=document.querySelector('.live-text');
  const dot=document.querySelector('.live-dot');
  if(on){
    pill.style.borderColor='rgba(78,202,128,0.4)';
    pill.style.background='rgba(78,202,128,0.1)';
    txt.textContent='EN DIRECT'; txt.style.color='#4ECA80';
    dot.style.background='#4ECA80';
  } else {
    pill.style.borderColor='rgba(255,150,0,0.4)';
    pill.style.background='rgba(255,150,0,0.08)';
    txt.textContent='HORS LIGNE'; txt.style.color='#F5A020';
    dot.style.background='#F5A020';
  }
}

let _goldOk = false;
let _prevGoldUSD = 0, _prevSilverUSD = 0;

function setUsdDir(idPrice, idArrow, idChg, newP, oldP){
  const pEl=document.getElementById(idPrice);
  const aEl=document.getElementById(idArrow);
  const cEl=document.getElementById(idChg);
  if(!pEl) return;
  const diff = oldP > 0 ? newP - oldP : 0;
  let cls='', arrow='—', chgTxt='±0.00 USD';
  if(diff > 0.005){
    cls='up'; arrow='▲';
    chgTxt='+'+diff.toFixed(2)+' USD';
  } else if(diff < -0.005){
    cls='dn'; arrow='▼';
    chgTxt=diff.toFixed(2)+' USD';
  }
  pEl.className='spot-usd-price'+(cls?' '+cls:'');
  if(aEl){ aEl.textContent=arrow; aEl.className='spot-usd-arrow'+(cls?' '+cls:''); }
  if(cEl){ cEl.textContent=chgTxt; cEl.className='spot-usd-chg'+(cls?' '+cls:''); }
}

async function fetchMetals(){
  const oldGold=goldUSD, oldSilver=silverUSD;
  try {
    const r=await fetch(METALS_URL);
    const md=await r.json();
    if(md.error){ console.warn('Metals API erreur:', md.error); _goldOk=false; }
    else {
      const gp=parseFloat(md.gold_price), gb=parseFloat(md.gold_bid), ga=parseFloat(md.gold_ask);
      const sp=parseFloat(md.silver_price), sb=parseFloat(md.silver_bid), sa=parseFloat(md.silver_ask);
      if(isFinite(gp)&&gp>100){
        goldBid=isFinite(gb)&&gb>100?gb:gp-0.5;
        goldAsk=isFinite(ga)&&ga>100?ga:gp+1.0;
        goldUSD=gp; _goldOk=true;
        setUsdDir('g-usd-big','g-arrow','g-usd-chg', goldUSD, oldGold);
      }
      if(isFinite(sp)&&sp>1){
        silverBid=isFinite(sb)&&sb>0?sb:sp-0.02;
        silverAsk=isFinite(sa)&&sa>0?sa:sp+0.05;
        silverUSD=sp;
        setUsdDir('s-usd-big','s-arrow','s-usd-chg', silverUSD, oldSilver);
      }
      // Badge source API
      if(md.source){
        const srcEl=document.getElementById('g-src');
        if(srcEl) srcEl.textContent=md.source.toUpperCase().replace('TRADINGVIEW-SPOT','TV SPOT').replace('YAHOO-FUTURES','YF FUT').replace('YAHOO-SPOT','YF SPOT');
      }
    }
  } catch(e){ console.warn('Metals erreur:',e.message); _goldOk=false; }
  setLive(_goldOk);
  updateSpot(); renderTable();
}

async function fetchFx(){
  try {
    const r=await fetch(FX_URL); const fxr=await r.json();
    if(fxr.rates&&fxr.rates.USD&&isFinite(fxr.rates.USD)) eurUsd=fxr.rates.USD;
  } catch(e){ console.warn('FX erreur:',e.message); }
  updateFx();
  updateSpot(); renderTable();
}

function updateFx(){
  const el0=document.getElementById('fx-usdxof');
  const el2=document.getElementById('fx-eurusd');
  if(el0) el0.textContent=fmtD(xofPerUsd(),2);
  if(el2) el2.textContent=fmtD(eurUsd,4);
}

const DAYS=['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'];
const MONTHS=['Jan','Fev','Mar','Avr','Mai','Juin','Juil','Aout','Sep','Oct','Nov','Dec'];
const DAYSH=['DIM','LUN','MAR','MER','JEU','VEN','SAM'];
function clock(){
  const n=new Date();
  const hh=String(n.getHours()).padStart(2,'0');
  const mm=String(n.getMinutes()).padStart(2,'0');
  const ss=String(n.getSeconds()).padStart(2,'0');
  const ts=hh+':'+mm+'<span class="ss">:'+ss+'</span>';
  const ds=n.getDate()+' '+MONTHS[n.getMonth()]+' '+n.getFullYear();
  document.getElementById('h-clock').innerHTML=ts;
  document.getElementById('h-day').textContent=DAYS[n.getDay()].toUpperCase();
  document.getElementById('h-date').textContent=ds;
  document.getElementById('rc-time').innerHTML=ts;
  document.getElementById('rc-day').textContent=DAYSH[n.getDay()];
  document.getElementById('rc-dmy').textContent=ds;
  document.getElementById('table-ts').textContent=hh+':'+mm+':'+ss+' - XOF';
}
setInterval(clock,1000); clock();

function updateSpot(){
  // Grands prix USD (texte seulement, la couleur est geree par setUsdDir)
  const gBig=document.getElementById('g-usd-big');
  const sBig=document.getElementById('s-usd-big');
  if(gBig&&goldUSD>0) gBig.textContent='$'+fmtD(goldUSD,2);
  if(sBig&&silverUSD>0) sBig.textContent='$'+fmtD(silverUSD,2);
  // Prix XOF
  document.getElementById('g-buy-xof').textContent=fmt(gKg());
  document.getElementById('g-sell-xof').textContent=fmt(gKgS());
  document.getElementById('s-buy-xof').textContent=fmt(sKg());
  document.getElementById('s-sell-xof').textContent=fmt(sKgS());
}

const ROWS=[
  {n:'GOLD',t:'9999',w:'1 KG',b:()=>gKg(0.9999),s:()=>gKgS(0.9999)},
  {n:'GOLD',t:'TTB',w:'116.64 g',b:()=>gTtb(),s:()=>gTtbS()},
  {n:'GOLD',t:'999',w:'1 KG',b:()=>gKg(0.999),s:()=>gKgS(0.999)},
  {n:'GOLD',t:'995',w:'1 KG',b:()=>gKg(0.995),s:()=>gKgS(0.995)},
  {n:'GOLD',t:'1 GM',w:'1 G',b:()=>gG(),s:()=>gGS()},
  {n:'SILVER',t:'9999',w:'1 KG',b:()=>sKg(),s:()=>sKgS()},
];
function renderTable(){
  document.getElementById('ctbody').innerHTML=ROWS.map(r=>{
    const dc=r.n==='GOLD'?'var(--gold)':'#607080';
    return '<tr><td><div class="com-name"><div class="com-dot" style="background:'+dc+'"></div>'+r.n+'<span class="com-tag">'+r.t+'</span></div></td><td class="wt-cell">'+r.w+'</td><td class="price-buy">'+fmt(r.b())+'</td><td class="price-sell">'+fmt(r.s())+'</td></tr>';
  }).join('');
}

function updateBs(){
  const b=55+Math.round(Math.random()*20), s=100-b;
  document.getElementById('bs-buy').style.width=b+'%';
  document.getElementById('bs-sell').style.width=s+'%';
  document.getElementById('bs-buy-pct').textContent=b+'%';
  document.getElementById('bs-sell-pct').textContent=s+'%';
}
setInterval(updateBs,8000); updateBs();

function buildTicker(){
  const items=[
    {k:'OR 9999',v:()=>fmt(gKg())+' XOF/kg'},
    {k:'OR TTB',v:()=>fmt(gTtb())+' XOF'},
    {k:'OR 999',v:()=>fmt(gKg(0.999))+' XOF/kg'},
    {k:'OR 995',v:()=>fmt(gKg(0.995))+' XOF/kg'},
    {k:'OR 1G',v:()=>fmt(gG())+' XOF/g'},
    {k:'ARGENT',v:()=>fmt(sKg())+' XOF/kg'},
    {k:'SPOT OR',v:()=>'$ '+fmtD(goldUSD,2)+'/oz'},
    {k:'SPOT AG',v:()=>'$ '+fmtD(silverUSD,2)+'/oz'},
    {k:'USD/XOF',v:()=>fmtD(xofPerUsd(),2)},
    {k:'CONTACT DXB',v:()=>'+971 568 174 541'},
    {k:'CONTACT CI',v:()=>'+225 07 97 97 12 97'},
    {k:'CONTACT BF',v:()=>'+226 65 39 30 32'},
    {k:'EMAIL',v:()=>'gztreasureinfo@gmail.com'},
  ];
  function render(){
    const h=items.map(it=>'<span class="t-item"><span class="t-item-key">'+it.k+'</span><span class="t-item-val">'+it.v()+'</span><span class="t-dot"></span></span>').join('');
    document.getElementById('ticker-inner').innerHTML=h+h;
  }
  render(); setInterval(render,10000);
}

updateSpot(); renderTable(); buildTicker(); updateFx();
fetchMetals();
fetchFx();
setInterval(fetchMetals, METALS_MS);
setInterval(fetchFx, FX_MS);
// Recalcul XOF chaque seconde (pas d'appel API - juste calcul en memoire)
setInterval(()=>{ updateSpot(); renderTable(); updateFx(); }, DISPLAY_MS);
</script>
</body>
</html>"""


# ─── SERVEUR HTTP ─────────────────────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/api/metals':
            self.proxy_metals()
        elif self.path == '/api/fx':
            self.proxy_fx()
        else:
            self.serve_page()

    def _log(self, msg):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        print(f'  [{t}] {msg}')

    def proxy_metals(self):
        """
        Essaie plusieurs APIs gratuites pour obtenir le cours de l'or et de l'argent.
        Ordre: 1) metals.live  2) goldprice.org  3) swissquote
        """
        xau = 0.0
        xag = 0.0
        source = None

        # ── API 0 : TradingView SPOT (meme source que tradingview.com) ───────
        try:
            req_g = urllib.request.Request(
                'https://scanner.tradingview.com/symbol?symbol=OANDA%3AXAUUSD&fields=close%2Cbid%2Cask&no_404=1',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer':    'https://www.tradingview.com/',
                    'Origin':     'https://www.tradingview.com',
                    'Accept':     'application/json',
                }
            )
            with urllib.request.urlopen(req_g, timeout=10) as r:
                data_g = json.loads(r.read())
            v_xau = float(data_g.get('close') or data_g.get('bid') or 0)
            if v_xau > 100:
                xau = v_xau
                source = 'tradingview-spot'
                self._log(f'/api/metals OK  TradingView SPOT (XAUUSD)  XAU={xau:.2f}')
                # Argent SPOT
                try:
                    req_s = urllib.request.Request(
                        'https://scanner.tradingview.com/symbol?symbol=OANDA%3AXAGUSD&fields=close%2Cbid%2Cask&no_404=1',
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Referer':    'https://www.tradingview.com/',
                            'Origin':     'https://www.tradingview.com',
                            'Accept':     'application/json',
                        }
                    )
                    with urllib.request.urlopen(req_s, timeout=8) as r2:
                        data_s = json.loads(r2.read())
                    v_xag = float(data_s.get('close') or data_s.get('bid') or 0)
                    if v_xag > 0:
                        xag = v_xag
                        self._log(f'                                   XAG={xag:.3f}')
                except Exception as e2:
                    self._log(f'                TradingView argent ERREUR: {e2}')
            else:
                self._log(f'/api/metals TradingView -> valeur invalide: {data_g}')
        except Exception as e:
            self._log(f'/api/metals TradingView ERREUR: {e}')

        # ── API 1 : metals.live ──────────────────────────────────────────────
        try:
            req = urllib.request.Request(
                'https://metals.live/api/spot',
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) GZInvests/3.0'}
            )
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
            spot = data[0] if isinstance(data, list) else data
            v_xau = float(spot.get('XAU', 0))
            v_xag = float(spot.get('XAG', 0))
            if v_xau > 100:
                xau = v_xau
                xag = v_xag
                source = 'metals.live'
                self._log(f'/api/metals OK  metals.live  XAU={xau:.2f}  XAG={xag:.3f}')
            else:
                self._log(f'/api/metals metals.live -> valeur invalide: XAU={v_xau}')
        except Exception as e:
            self._log(f'/api/metals metals.live ERREUR: {e}')

        # ── API 2 : goldprice.org ────────────────────────────────────────────
        if xau < 100:
            try:
                req = urllib.request.Request(
                    'https://data-asg.goldprice.org/GetData/XAU-USD,XAG-USD/1',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Referer':    'https://goldprice.org/',
                        'Accept':     'application/json',
                    }
                )
                with urllib.request.urlopen(req, timeout=12) as r:
                    raw = json.loads(r.read())
                # Format attendu: ["XAU-USD,3023.45,0.12", "XAG-USD,30.45,0.01"]
                if isinstance(raw, list):
                    for item in raw:
                        parts = str(item).split(',')
                        if len(parts) >= 2:
                            try:
                                val = float(parts[1])
                            except:
                                continue
                            if 'XAU' in parts[0] and val > 100:
                                xau = val
                            elif 'XAG' in parts[0] and val > 0:
                                xag = val
                if xau > 100:
                    source = 'goldprice.org'
                    self._log(f'/api/metals OK  goldprice.org  XAU={xau:.2f}  XAG={xag:.3f}')
                else:
                    self._log(f'/api/metals goldprice.org -> valeur invalide: {raw}')
            except Exception as e:
                self._log(f'/api/metals goldprice.org ERREUR: {e}')

        # ── API 2b : stooq.com (cours SPOT reel, CSV simple) ────────────────
        if xau < 100:
            try:
                # Or SPOT USD: stooq.com retourne directement le prix de cloture
                req_g = urllib.request.Request(
                    'https://stooq.com/q/l/?s=xauusd&f=c&e=csv',
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req_g, timeout=12) as r:
                    txt = r.read().decode('utf-8').strip()
                # Format: "Close\n4371.53"
                lines = [l.strip() for l in txt.split('\n') if l.strip()]
                if len(lines) >= 2:
                    v_xau = float(lines[-1])
                    if v_xau > 100:
                        xau = v_xau
                        source = 'stooq-spot'
                        self._log(f'/api/metals OK  stooq.com SPOT (xauusd)  XAU={xau:.2f}')
                        # Argent SPOT
                        try:
                            req_s = urllib.request.Request(
                                'https://stooq.com/q/l/?s=xagusd&f=c&e=csv',
                                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                            )
                            with urllib.request.urlopen(req_s, timeout=10) as r2:
                                txt2 = r2.read().decode('utf-8').strip()
                            lines2 = [l.strip() for l in txt2.split('\n') if l.strip()]
                            if len(lines2) >= 2:
                                v_xag = float(lines2[-1])
                                if v_xag > 0:
                                    xag = v_xag
                                    self._log(f'                                   XAG={xag:.3f}')
                        except Exception as e2:
                            self._log(f'                stooq argent ERREUR: {e2}')
                    else:
                        self._log(f'/api/metals stooq.com -> valeur invalide: {v_xau}')
                else:
                    self._log(f'/api/metals stooq.com -> reponse vide: {txt}')
            except Exception as e:
                self._log(f'/api/metals stooq.com ERREUR: {e}')

        # ── API 3 : swissquote (or seulement) ───────────────────────────────
        if xau < 100:
            try:
                req = urllib.request.Request(
                    'https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD',
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, timeout=12) as r:
                    data = json.loads(r.read())
                if isinstance(data, list) and data:
                    for entry in data:
                        prices = entry.get('spreadProfilePrices', [])
                        if prices:
                            bid = float(prices[0].get('fBid', 0))
                            ask = float(prices[0].get('fAsk', 0))
                            if bid > 100:
                                xau = round((bid + ask) / 2, 2)
                                source = 'swissquote'
                                self._log(f'/api/metals OK  swissquote  XAU={xau:.2f} (bid={bid} ask={ask})')
                                break
                if xau < 100:
                    self._log(f'/api/metals swissquote -> valeur invalide')
            except Exception as e:
                self._log(f'/api/metals swissquote ERREUR: {e}')

        # ── API 4 : Yahoo Finance (SPOT XAU=X, puis Futures GC=F) ───────────
        if xau < 100:
            for ticker_g, ticker_s, label in [
                ('XAU=X', 'XAG=X', 'SPOT'),
                ('GC=F',  'SI=F',  'Futures'),
            ]:
                if xau >= 100:
                    break
                try:
                    req_g = urllib.request.Request(
                        f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker_g}?interval=1d&range=1d',
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'application/json',
                        }
                    )
                    with urllib.request.urlopen(req_g, timeout=12) as r:
                        d = json.loads(r.read())
                    v_xau = float(d['chart']['result'][0]['meta']['regularMarketPrice'])
                    if v_xau > 100:
                        xau = v_xau
                        source = f'yahoo-{label.lower()}'
                        self._log(f'/api/metals OK  Yahoo {label} ({ticker_g})  XAU={xau:.2f}')
                        try:
                            req_s = urllib.request.Request(
                                f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker_s}?interval=1d&range=1d',
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                    'Accept': 'application/json',
                                }
                            )
                            with urllib.request.urlopen(req_s, timeout=10) as r2:
                                d2 = json.loads(r2.read())
                            v_xag = float(d2['chart']['result'][0]['meta']['regularMarketPrice'])
                            if v_xag > 0:
                                xag = v_xag
                                self._log(f'                                   XAG={xag:.3f}')
                        except Exception as e2:
                            self._log(f'                Yahoo argent ERREUR: {e2}')
                    else:
                        self._log(f'/api/metals Yahoo {label} ({ticker_g}) invalide: {v_xau}')
                except Exception as e:
                    self._log(f'/api/metals Yahoo {label} ({ticker_g}) ERREUR: {e}')

        # ── Reponse finale ───────────────────────────────────────────────────
        if xau < 100:
            self._log('/api/metals ECHEC - toutes les APIs sont inaccessibles')
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Toutes les APIs de cours sont inaccessibles depuis votre reseau'
            }).encode())
            return

        result = {
            'gold_price':   xau,
            'gold_bid':     round(xau - 0.50, 2),
            'gold_ask':     round(xau + 1.00, 2),
            'silver_price': round(xag, 4) if xag > 0 else 0,
            'silver_bid':   round(xag - 0.02, 3) if xag > 1 else 0,
            'silver_ask':   round(xag + 0.05, 3) if xag > 1 else 0,
            'source':       source,
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def proxy_fx(self):
        try:
            req = urllib.request.Request(
                'https://api.frankfurter.dev/v1/latest?from=EUR&to=USD',
                headers={'User-Agent': 'GZInvests/3.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            self._log('/api/fx OK  frankfurter.dev  EUR/USD mis a jour')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._log(f'/api/fx ERREUR: {e} - taux de repli 1.16')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'rates': {'USD': 1.16}}).encode())

    def serve_page(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))

    def log_message(self, format, *args):
        # Supprimer les logs HTTP par defaut (on gere nos propres logs)
        pass


# ─── LANCEMENT ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 55)
    print('  GZ INVESTS - Tableau de Bord des Cours  v3.9')
    print('=' * 55)
    print()
    print(f'  Serveur demarre sur http://localhost:{PORT}/')
    print()
    print('  APIs or/argent (essayees dans l\'ordre):')
    print('    0. TradingView SPOT (XAUUSD) <- NOUVEAU')
    print('    1. metals.live')
    print('    2. goldprice.org')
    print('    2b. stooq.com (SPOT)')
    print('    3. swissquote.com')
    print('    4. Yahoo XAU=X (SPOT) puis GC=F (Futures)')
    print()
    print('  Les tentatives de connexion s\'affichent ci-dessous.')
    print()
    print('  [NE PAS FERMER CETTE FENETRE]')
    print('  Pour arreter : CTRL + C')
    print()
    print('-' * 55)

    try:
        server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
        print(f'  Serveur demarre sur le port {PORT}')
        print('  [CTRL+C pour arreter]')
        print('-' * 55)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Arret du serveur. Au revoir!')
        sys.exit(0)
    except OSError as e:
        print(f'\n  ERREUR port {PORT}: {e}')
        sys.exit(1)
