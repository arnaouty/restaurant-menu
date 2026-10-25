# Restaurant Table QR Codes

Static QR codes for restaurant tables. Scanning opens one page with **Menu**, **Location** and **Payment methods**.

The printed QR code never changes. It points to `index.html`, which reads `restaurant.json`.
To change the menu link, address or payment methods later, edit `restaurant.json`. You don't need to reprint anything.

## Setup
1. Fill in your details: open `admin.html` (see below) or edit `restaurant.json` by hand.
2. Host the site. For example, enable GitHub Pages (Settings → Pages → branch `main`, folder `/`).
   Put the resulting URL in `base_url`.
3. Generate the codes:
   ```bash
   pip install qrcode pillow
   python3 generate_qr.py
   ```
4. Open `qr/table-cards.html` in a browser and print it (4 cards per A4 page).

## Admin panel (`admin.html`)
Edit the restaurant name, phone, currency, address, Maps link, payment methods and the full menu here.
That covers categories, items, descriptions, prices and sold-out status. You can also reorder and delete anything.

1. Open `https://<your-site>/admin.html`.
2. Sign in with a GitHub **fine-grained personal access token**.
   Create it at <https://github.com/settings/personal-access-tokens/new>.
   Give it access to **only this repository**, with permission **Contents: Read and write**.
3. Edit, then click **Save changes**. This commits `restaurant.json` to the repo, and the live menu updates within 1–2 minutes.

The admin page is public, but without your token it can't read or change anything. Keep the token private.
If it leaks, revoke it on GitHub.

## What the QR codes open
| QR file | Opens |
|---|---|
| `qr/table-XX.png` | Landing page showing "Table XX" with Menu / Location / Payment |
| `qr/menu.png` | Landing page with the menu open |
| `qr/location.png` | Goes straight to Google Maps |
| `qr/pay.png` | Landing page with the payment methods open |
