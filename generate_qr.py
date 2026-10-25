"""Generate static table QR codes from restaurant.json.

Usage: python3 generate_qr.py
Output: qr/table-XX.png (one per table), qr/menu.png, qr/location.png, qr/pay.png,
        and qr/table-cards.html (printable cards, 4 per A4 page).
"""
import base64
import io
import json
from html import escape
from pathlib import Path
from urllib.parse import urlencode

import qrcode
from qrcode.constants import ERROR_CORRECT_H

ROOT = Path(__file__).parent
OUT = ROOT / "qr"


def make_qr(url, path):
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=12, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def link(base, **query):
    return f"{base}?{urlencode(query)}"


def main():
    config = json.loads((ROOT / "restaurant.json").read_text(encoding="utf-8"))
    base = config["base_url"]
    OUT.mkdir(exist_ok=True)

    # Single-purpose QR codes that skip the landing page.
    for name in ("menu", "location", "pay"):
        make_qr(link(base, go=name), OUT / f"{name}.png")

    cards = []
    for n in range(1, config["tables"] + 1):
        url = link(base, t=n)
        png = make_qr(url, OUT / f"table-{n:02d}.png")
        cards.append(
            f'<div class="card"><h2>{escape(config["name"])}</h2>'
            f'<img src="data:image/png;base64,{png}" alt="QR for table {n}">'
            f"<p>Scan for Menu · Location · Payment</p>"
            f'<div class="table">Table {n}</div></div>'
        )

    (OUT / "table-cards.html").write_text(
        f"""<!doctype html><html><head><meta charset="utf-8"><title>Table QR cards</title>
<style>
  @page {{ size: A4; margin: 10mm; }}
  body {{ font-family: system-ui, sans-serif; margin: 0; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; }}
  .card {{ border: 1px dashed #999; padding: 8mm; text-align: center; break-inside: avoid; }}
  .card h2 {{ margin: 0 0 4mm; }}
  .card img {{ width: 60mm; height: 60mm; }}
  .card p {{ margin: 3mm 0; color: #444; }}
  .table {{ font-size: 1.4rem; font-weight: 700; }}
</style></head><body><div class="grid">{"".join(cards)}</div></body></html>""",
        encoding="utf-8",
    )
    print(f"Generated {config['tables']} table QR codes in {OUT}/ (open table-cards.html to print)")


if __name__ == "__main__":
    main()
