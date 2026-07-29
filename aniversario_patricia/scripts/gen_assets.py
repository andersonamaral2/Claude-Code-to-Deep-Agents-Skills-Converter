"""Gera os assets estáticos da landing de aniversário.

1. `site/assets/patricia.png` — redimensiona a foto de 600px para 192px (chip 64px @3x).
2. `site/assets/og-image.png` — 1200x630 renderizado via Playwright com as fontes
   reais da marca (Familjen Grotesk + Instrument Serif), não com fallback DejaVu.

Uso: python3 scripts/gen_assets.py
"""

import base64
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "site" / "assets"
FOTO = ASSETS / "patricia.png"
OG = ASSETS / "og-image.png"


def resize_foto() -> None:
    """O chip renderiza a 64px; 192px cobre telas 3x sem carregar 436 KB."""
    img = Image.open(FOTO).convert("RGBA")
    if img.width <= 192:
        print(f"[foto] já otimizada ({img.size})")
        return
    antes = FOTO.stat().st_size
    img.resize((192, 192), Image.LANCZOS).save(FOTO, optimize=True)
    print(f"[foto] {antes // 1024} KB -> {FOTO.stat().st_size // 1024} KB (192x192)")


def og_html() -> str:
    foto_b64 = base64.b64encode(FOTO.read_bytes()).decode()
    return f"""<!doctype html>
<html><head><meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet" />
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{width:1200px;height:630px;background:#000;overflow:hidden;position:relative;
       font-family:'Familjen Grotesk',sans-serif;color:#F6F6F6}}
  .glow{{position:absolute;border-radius:50%;filter:blur(110px);pointer-events:none}}
  .g1{{width:620px;height:620px;background:rgba(101,44,242,.42);top:-230px;right:-140px}}
  .g2{{width:480px;height:480px;background:rgba(51,217,213,.20);bottom:-240px;left:-130px}}
  .wrap{{position:relative;z-index:2;padding:56px 68px 168px;height:100%;
         display:flex;flex-direction:column;justify-content:center}}
  .eyebrow{{font-family:'JetBrains Mono',monospace;font-size:16px;letter-spacing:.2em;
            text-transform:uppercase;color:#33D9D5;margin-bottom:22px}}
  h1{{font-size:64px;line-height:1.06;font-weight:700;letter-spacing:-.02em;max-width:720px}}
  .serif{{font-family:'Instrument Serif',serif;font-style:italic;font-weight:400}}
  .grad{{background:linear-gradient(120deg,#33D9D5 0%,#652CF2 62%);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
  .sub{{margin-top:24px;font-size:23px;line-height:1.45;color:rgba(246,246,246,.78);max-width:660px}}
  .sub b{{color:#F6F6F6;font-weight:600}}
  .foot{{position:absolute;left:68px;bottom:52px;display:flex;align-items:center;gap:16px}}
  .foot img{{width:62px;height:62px;border-radius:50%;border:2px solid rgba(101,44,242,.85)}}
  .foot .nm{{font-size:20px;font-weight:600;line-height:1.25}}
  .foot .rl{{font-family:'JetBrains Mono',monospace;font-size:12.5px;letter-spacing:.1em;
             text-transform:uppercase;color:rgba(246,246,246,.55);margin-top:3px}}
  .dom{{position:absolute;right:68px;bottom:56px;font-family:'JetBrains Mono',monospace;
        font-size:15px;letter-spacing:.06em;color:rgba(246,246,246,.5)}}
  .rule{{position:absolute;left:0;top:0;width:100%;height:3px;
         background:linear-gradient(90deg,#33D9D5 0%,#652CF2 55%,#4400A5 100%)}}
</style></head>
<body>
  <div class="rule"></div>
  <div class="glow g1"></div><div class="glow g2"></div>
  <div class="wrap">
    <div class="eyebrow">29 de julho · Campanha de aniversário</div>
    <h1>Dia 29 é meu aniversário.<br/>O <span class="serif grad">presente</span> é seu.</h1>
    <div class="sub">Manual <b>Automação com Critério</b> + a skill do método no seu Claude,
      na hora. E o desconto exclusivo no dia 29.</div>
  </div>
  <div class="foot">
    <img src="data:image/png;base64,{foto_b64}" alt="" />
    <div>
      <div class="nm">Patricia Costa</div>
      <div class="rl">CPO Scoras Digital · Scoras Academy</div>
    </div>
  </div>
  <div class="dom">aniversario-patricia.scorasacademy.com.br</div>
</body></html>"""


def gerar_og() -> None:
    tmp = ROOT / "scripts" / "_og.html"
    tmp.write_text(og_html(), encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        page.goto(tmp.as_uri())
        page.wait_for_timeout(2500)  # dá tempo das webfonts baixarem e trocarem
        page.screenshot(path=str(OG))
        browser.close()
    tmp.unlink()
    print(f"[og] {OG} ({OG.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    resize_foto()
    gerar_og()
