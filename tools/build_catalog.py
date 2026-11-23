# Generates the Meta (Facebook/Instagram) product catalog feed + a shareable page per product.
# Run from the repo root:  python3 tools/build_catalog.py
import csv, json, os, html

SITE = "https://remaxiraq.net"
CATS = {"bt": "سماعات بلوتوث", "wired": "سماعات سلكية", "cables": "كيبلات شحن", "home": "شواحن منزلية",
        "car": "شواحن سيارة", "powerbank": "باور بانك", "watches": "ساعات ذكية", "bags": "حقائب",
        "fans": "مراوح", "memory": "رامات وذواكر", "misc": "متنوعة"}

def priced(p):
    try: return float(p.get("price") or 0) > 0
    except (TypeError, ValueError): return False

P = json.load(open("products.json", encoding="utf-8"))
os.makedirs("p", exist_ok=True)
for f in os.listdir("p"):
    if f.endswith(".html"): os.remove(os.path.join("p", f))

rows = []
for p in P:
    imgs = [i for i in (p.get("images") or []) if i]
    title = f"REMAX {p.get('model','')} - {p.get('name','')}".strip()
    desc = (p.get("desc") or p.get("name") or "").strip()
    page = f"{SITE}/p/{p['id']}.html"
    img = f"{SITE}/{imgs[0]}" if imgs else f"{SITE}/icons/icon-512.png"

    # shareable page: proper preview on Facebook/WhatsApp, then opens the product in the store
    price_txt = f"{int(float(p['price'])):,} د.ع" if priced(p) else ""
    og_desc = html.escape(f"{price_txt} · {desc}" if price_txt else desc, quote=True)
    with open(f"p/{p['id']}.html", "w", encoding="utf-8") as fh:
        fh.write(f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | ريماكس العراق</title>
<link rel="canonical" href="{page}">
<meta property="og:type" content="product">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="{img}">
<meta property="og:url" content="{page}">
<meta property="product:retailer_item_id" content="{p['id']}">
{f'<meta property="product:price:amount" content="{int(float(p["price"]))}"><meta property="product:price:currency" content="IQD">' if priced(p) else ''}
<meta http-equiv="refresh" content="0; url=/#p-{p['id']}">
<script>location.replace("/#p-{p['id']}")</script>
</head><body><a href="/#p-{p['id']}">{html.escape(title)}</a></body></html>
""")

    if not priced(p) or not imgs:
        continue
    qty = p.get("qty")
    avail = "out of stock" if (qty not in (None, "") and float(qty) <= 0) else "in stock"
    price = int(float(p["price"]))
    old = p.get("old")
    row = {
        "id": p["id"], "title": title[:150], "description": desc[:5000],
        "availability": avail, "condition": "new",
        "price": f"{int(float(old)) if old and float(old) > price else price} IQD",
        "sale_price": f"{price} IQD" if old and float(old) > price else "",
        "link": page, "image_link": img,
        "additional_image_link": ",".join(f"{SITE}/{i}" for i in imgs[1:]),
        "brand": "REMAX", "product_type": CATS.get(p.get("cat"), "متنوعة"),
        "google_product_category": "Electronics", "custom_label_0": "جديد" if p.get("new") else "",
    }
    rows.append(row)

with open("catalog.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print(f"catalog.csv: {len(rows)} products; p/: {len(P)} pages")
