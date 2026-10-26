"""Generate static table QR codes from restaurant.json.

Usage: python3 generate_qr.py
Output: qr/table-XX.png (one per table), qr/menu.png, qr/location.png, qr/pay.png,
        qr/table-cards.html (designed printable cards, 4 per A4 page),
        qr/all-tables.png and qr/all-tables-cards.html (one shared code for every table).
"""
import json
from html import escape
from pathlib import Path
from urllib.parse import urlencode

import qrcode
from qrcode.constants import ERROR_CORRECT_H

ROOT = Path(__file__).parent
OUT = ROOT / "qr"

NAVY = "#1e3a5f"
GOLD = "#9a7b4f"


def build_qr(url):
    # High error correction so a scratched or dirty card still scans.
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    return qr


def make_qr(url, path):
    """Plain black-and-white PNG, for use anywhere."""
    qr = build_qr(url)
    qr.border = 2
    qr.box_size = 12
    qr.make_image(fill_color="black", back_color="white").save(path)


def qr_svg(url):
    """Styled QR as SVG: round navy dots and rounded eyes."""
    qr = build_qr(url)
    m = qr.get_matrix()
    n = len(m)

    eyes = [(0, 0), (n - 7, 0), (0, n - 7)]

    def in_eye(r, c):
        return any(er <= r < er + 7 and ec <= c < ec + 7 for er, ec in eyes)

    dots = "".join(
        f'<circle cx="{c + .5}" cy="{r + .5}" r=".44"/>'
        for r in range(n) for c in range(n)
        if m[r][c] and not in_eye(r, c)
    )
    eye_svg = "".join(
        f'<path fill-rule="evenodd" d="M{c + 2} {r}h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-3a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2z'
        f'M{c + 2} {r + 1}a1 1 0 0 0-1 1v3a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1z"/>'
        f'<rect x="{c + 2}" y="{r + 2}" width="3" height="3" rx=".9"/>'
        for r, c in eyes
    )
    return f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg"><g fill="{NAVY}">{dots}{eye_svg}</g></svg>'


def link(base, **query):
    return f"{base}?{urlencode(query)}"


def card(config, url, label):
    return f"""<div class="card">
  <div class="photo"></div>
  <div class="eyebrow">Welcome to</div>
  <div class="name">{escape(config["name"])}</div>
  <div class="tile">{qr_svg(url)}</div>
  <div class="cta">Scan for Menu · Location · Payments</div>
  <div class="rule"><span></span><i></i><span></span></div>
  <div class="label">{escape(label)}</div>
</div>"""


def write_cards(path, cards):
    path.write_text(
        f"""<!doctype html><html><head><meta charset="utf-8"><title>Table QR cards</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600&family=Inter:wght@400;500;600&family=Playfair+Display:wght@500;700&display=swap" rel="stylesheet">
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #ddd; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .sheet {{ display: grid; grid-template-columns: 105mm 105mm; width: 210mm; margin: 0 auto; }}
  /* One A6 card; four fill an A4 page. Cut along the hairlines. */
  .card {{ position: relative; width: 105mm; height: 148.5mm; overflow: hidden; break-inside: avoid;
           display: flex; flex-direction: column; align-items: center; padding: 11mm 0 13mm;
           background: #0f1f35; font-family: "Inter", "Cairo", sans-serif; color: #fff; text-align: center; }}
  .card::after {{ content: ""; position: absolute; inset: 0; border: .2mm solid rgba(255,255,255,.35); pointer-events: none; }}
  .photo {{ position: absolute; inset: 0 0 auto; height: 122mm; background: url("../images/background.jpg") center 40% / cover; }}
  .photo::after {{ content: ""; position: absolute; inset: -1px;
                   background: linear-gradient(180deg, rgba(15,31,53,.55) 0%, rgba(15,31,53,.1) 30%, rgba(15,31,53,.45) 60%, #0f1f35 92%); }}
  .eyebrow, .name, .tile, .cta, .rule, .label {{ position: relative; }}
  .eyebrow {{ font-size: 2.5mm; font-weight: 600; letter-spacing: .35em; text-transform: uppercase; opacity: .9; }}
  .name {{ margin: 1.5mm 6mm 0; font: 500 8mm/1.05 "Playfair Display", "Cairo", serif; letter-spacing: -.02em;
           text-shadow: 0 .6mm 4mm rgba(2,8,23,.5); }}
  .tile {{ width: 66mm; margin: auto 0; padding: 5.5mm; background: #fff; border-radius: 5mm;
           box-shadow: 0 2mm 8mm rgba(2,8,23,.45), inset 0 0 0 .7mm #fff, inset 0 0 0 .95mm {GOLD}; }}
  .tile svg {{ display: block; width: 100%; height: auto; }}
  .cta {{ font-size: 2.6mm; font-weight: 500; letter-spacing: .2em; text-transform: uppercase; opacity: .85; }}
  .rule {{ display: flex; align-items: center; justify-content: center; gap: 2mm; margin-top: 4.5mm; }}
  .rule span {{ width: 14mm; height: .3mm; background: {GOLD}; }}
  .rule i {{ width: 1.6mm; height: 1.6mm; background: {GOLD}; transform: rotate(45deg); }}
  .label {{ margin-top: 3.5mm; font: 700 9mm/1 "Playfair Display", "Cairo", serif; }}
  .label:empty::before {{ content: "Bon appétit"; font-weight: 500; font-style: italic; }}
  @media screen {{ .sheet {{ gap: 6mm; padding: 6mm; width: auto; justify-content: center; }} }}
</style></head><body><div class="sheet">{"".join(cards)}</div></body></html>""",
        encoding="utf-8",
    )


def main():
    config = json.loads((ROOT / "restaurant.json").read_text(encoding="utf-8"))
    base = config["base_url"]
    OUT.mkdir(exist_ok=True)

    # Single-purpose QR codes that skip the landing page.
    for name in ("menu", "location", "pay"):
        make_qr(link(base, go=name), OUT / f"{name}.png")

    make_qr(base, OUT / "all-tables.png")
    write_cards(OUT / "all-tables-cards.html", [card(config, base, "")] * 4)

    cards = []
    for n in range(1, config["tables"] + 1):
        url = link(base, t=n)
        make_qr(url, OUT / f"table-{n:02d}.png")
        cards.append(card(config, url, f"Table {n}"))
    write_cards(OUT / "table-cards.html", cards)

    print(f"Generated {config['tables']} table QR codes + 1 shared code in {OUT}/ (open the *-cards.html files to print)")


if __name__ == "__main__":
    main()
