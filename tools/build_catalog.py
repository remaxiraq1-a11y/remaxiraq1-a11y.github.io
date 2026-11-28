# يبني صفحات المنتجات والأقسام (تظهر بجوجل) + ملف sitemap.xml + كتالوج فيسبوك/انستغرام
# Generates: p/<id>.html (full product pages for Google), c/<cat>.html (category pages),
# sitemap.xml, robots.txt and catalog.csv (Meta catalog feed).
# Run from the repo root:  python3 tools/build_catalog.py
import csv, json, os, html, re, datetime, urllib.parse

SITE = "https://remaxiraq.net"
WA = "9647836644721"
WA_SHOW = "0783 664 4721"
CATS = {"bt": "سماعات بلوتوث", "wired": "سماعات سلكية", "cables": "كيبلات شحن", "home": "شواحن منزلية",
        "car": "شواحن سيارة", "powerbank": "باور بانك", "watches": "ساعات ذكية", "bags": "حقائب",
        "fans": "مراوح", "memory": "رامات وذواكر", "misc": "متنوعة"}
CAT_INTRO = {
    "bt": "سماعات بلوتوث REMAX الأصلية في العراق: ايربودز، سماعات رأس وسماعات رياضية بضمان 12 شهر.",
    "wired": "سماعات سلكية REMAX الأصلية في العراق بضمان 12 شهر من الوكيل الحصري.",
    "cables": "كيبلات شحن REMAX الأصلية في العراق: Type-C وآيفون (Lightning) وشحن سريع بضمان 12 شهر.",
    "home": "شواحن منزلية REMAX الأصلية في العراق: شحن سريع PD و GaN بضمان 12 شهر.",
    "car": "شواحن سيارة REMAX الأصلية في العراق بشحن سريع وضمان 12 شهر.",
    "powerbank": "باور بانك REMAX الأصلي في العراق بكل السعات: 10000 و 20000 و 30000 و 50000 و 100000mAh، بشحن سريع وضمان 12 شهر.",
    "watches": "ساعات ذكية REMAX الأصلية في العراق بضمان 12 شهر.",
    "bags": "حقائب REMAX الأصلية في العراق.",
    "fans": "مراوح REMAX المحمولة الأصلية في العراق.",
    "memory": "رامات وذواكر REMAX الأصلية في العراق.",
    "misc": "منتجات REMAX متنوعة أصلية في العراق بضمان 12 شهر.",
}
E = lambda s: html.escape(str(s if s is not None else ""), quote=True)

def priced(p):
    try: return float(p.get("price") or 0) > 0
    except (TypeError, ValueError): return False
def num(n): return f"{int(float(n)):,}"
def in_stock(p):
    q = p.get("qty")
    try: return q in (None, "") or float(q) > 0
    except (TypeError, ValueError): return True
def title_of(p): return f"REMAX {p.get('model','')} - {p.get('name','')}".strip()
def imgs_of(p): return [i for i in (p.get("images") or []) if i]

P = json.load(open("products.json", encoding="utf-8"))
INDEX = open("index.html", encoding="utf-8").read()
m = re.search(r"const LOGO = `(.*?)`;", INDEX, re.S)
LOGO = m.group(1) if m else "REMAX"
# copy the ad pixels (Meta + TikTok) so ads tracking keeps working on these pages
PIX = "\n".join(re.findall(r"<!-- TikTok Pixel Code Start -->.*?<!-- TikTok Pixel Code End -->|<!-- Meta Pixel Code -->.*?<!-- End Meta Pixel Code -->", INDEX, re.S))
TODAY = datetime.date.today().isoformat()

CSS = """:root{--ink:#111113;--ink2:#3a3a40;--muted:#86868e;--line:#ececef;--soft:#f5f5f7;--acc:#ff5b14;--ok:#14a052;--bad:#d92d20}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'IBM Plex Sans Arabic',system-ui,sans-serif;color:var(--ink);line-height:1.7;background:#fff}
a{color:inherit;text-decoration:none}.wrap{max-width:1100px;margin:auto;padding:0 18px}.en{font-family:'Inter',sans-serif;direction:ltr;unicode-bidi:isolate}
header{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.95);border-bottom:1px solid var(--line)}
.hd{display:flex;align-items:center;justify-content:space-between;height:62px}.lg svg{height:22px;width:auto;display:block}
.hd nav a{font-size:.95rem;margin-inline-start:16px;color:var(--ink2)}
.crumb{font-size:.85rem;color:var(--muted);margin:18px 0}.crumb a{color:var(--ink2)}.crumb a:after{content:" › ";color:var(--muted)}
.pg{display:grid;grid-template-columns:1fr 1fr;gap:34px}@media(max-width:800px){.pg{grid-template-columns:1fr;gap:18px}}
.gal img{width:100%;border-radius:18px;background:var(--soft);display:block;margin-bottom:10px;aspect-ratio:1/1;object-fit:contain}
.mdl{color:var(--acc);font-weight:700;font-family:'Inter',sans-serif}h1{font-size:1.6rem;line-height:1.4;margin:4px 0 12px}
.pr{font-size:1.7rem;font-weight:700}.pr s{font-size:1rem;color:var(--muted);margin-inline-start:10px;font-weight:400}
.st{display:inline-block;font-size:.85rem;margin:6px 0 14px;color:var(--ok)}.st.out{color:var(--bad)}
.desc{color:var(--ink2);margin:10px 0}.specs{margin:12px 0 18px;padding-inline-start:20px;color:var(--ink2)}
.btn{display:block;text-align:center;padding:14px;border-radius:14px;font-weight:700;margin-bottom:10px;background:var(--ink);color:#fff}
.btn.w{background:#25d366}.perks{list-style:none;background:var(--soft);border-radius:14px;padding:14px 16px;font-size:.92rem;margin-top:8px}.perks li{margin:3px 0}
h2{font-size:1.25rem;margin:40px 0 14px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:16px;padding:10px;display:block}.card img{width:100%;aspect-ratio:1/1;object-fit:contain;background:var(--soft);border-radius:12px}
.card .m{color:var(--acc);font-size:.8rem;font-weight:700;font-family:'Inter',sans-serif;margin-top:6px}.card .n{font-size:.9rem;line-height:1.5;height:2.9em;overflow:hidden}.card b{display:block;margin-top:4px}
.intro{color:var(--ink2);margin-bottom:18px}.cats{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 30px}.cats a{background:var(--soft);padding:6px 14px;border-radius:999px;font-size:.9rem}
footer{border-top:1px solid var(--line);margin-top:50px;padding:26px 0;color:var(--muted);font-size:.88rem}"""

def page(title, desc, canon, body, og_img, og_type="website", extra_head="", ld=None):
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in (ld or []))
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc[:300])}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="ريماكس العراق">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc[:300])}">
<meta property="og:image" content="{og_img}">
<meta property="og:url" content="{canon}">
{extra_head}<link rel="icon" type="image/png" href="/icons/favicon-48.png">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;700&family=Inter:wght@700&display=swap" rel="stylesheet">
<style>{CSS}</style>
{lds}{PIX}
</head><body>
<header><div class="wrap hd"><a class="lg" href="/" aria-label="ريماكس العراق">{LOGO}</a>
<nav><a href="/#all">المنتجات</a><a href="/#warranty">الضمان</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">
<div class="cats">{"".join(f'<a href="/c/{k}.html">{v}</a>' for k, v in CATS.items() if any(p.get("cat") == k for p in P))}</div>
ريماكس العراق — شركة وميض الذهب، الوكيل الحصري لماركة REMAX في العراق. منتجات أصلية بضمان 12 شهر، توصيل لكل المحافظات بـ 5,000 دينار.
واتساب: <a class="en" href="https://wa.me/{WA}">{WA_SHOW}</a></div></footer>
</body></html>
"""

def card(p):
    im = imgs_of(p)
    pr = f"{num(p['price'])} د.ع" if priced(p) else "السعر عند الاستفسار"
    img = f'<img src="/{E(im[0])}" alt="{E(title_of(p))}" loading="lazy">' if im else ""
    return f'<a class="card" href="/p/{p["id"]}.html">{img}<div class="m">{E(p.get("model",""))}</div><div class="n">{E(p.get("name",""))}</div><b>{pr}</b></a>'

ORG = {"@type": "Organization", "name": "ريماكس العراق - شركة وميض الذهب", "url": SITE + "/"}

# ---------- product pages ----------
os.makedirs("p", exist_ok=True)
for f in os.listdir("p"):
    if f.endswith(".html"): os.remove(os.path.join("p", f))
for p in P:
    im = imgs_of(p); cat = p.get("cat") if p.get("cat") in CATS else "misc"; cname = CATS[cat]
    title = title_of(p); canon = f"{SITE}/p/{p['id']}.html"
    desc = (p.get("desc") or p.get("name") or "").strip()
    og_img = f"{SITE}/{im[0]}" if im else f"{SITE}/icons/icon-512.png"
    pr_html = ""
    if priced(p):
        old = p.get("old")
        pr_html = f'<div class="pr">{num(p["price"])} د.ع' + (f'<s>{num(old)} د.ع</s>' if old and float(old) > float(p["price"]) else "") + "</div>"
    else:
        pr_html = '<div class="pr" style="font-size:1.1rem">السعر عند الاستفسار</div>'
    stock = '<span class="st">متوفر</span>' if in_stock(p) else '<span class="st out">نفذت الكمية</span>'
    specs = "".join(f"<li>{E(s)}</li>" for s in (p.get("specs") or []) if s)
    wa_txt = urllib.parse.quote(f"مرحبا ريماكس العراق، أريد أطلب: REMAX {p.get('model','')} - {p.get('name','')}" + (f" بسعر {num(p['price'])} د.ع" if priced(p) else "") + f"\n{canon}")
    rel = [x for x in P if x.get("cat") == p.get("cat") and x["id"] != p["id"]][:8]
    body = f"""<div class="crumb"><a href="/">الرئيسية</a><a href="/c/{cat}.html">{cname}</a><span class="en">{E(p.get('model',''))}</span></div>
<div class="pg"><div class="gal">{"".join(f'<img src="/{E(i)}" alt="{E(title)} - صورة {n+1}"' + (' loading="lazy"' if n else '') + '>' for n, i in enumerate(im))}</div>
<div><div class="mdl">REMAX {E(p.get('model',''))}</div><h1>{E(p.get('name',''))}</h1>{pr_html}{stock}
<p class="desc">{E(desc)}</p>{f'<ul class="specs">{specs}</ul>' if specs else ''}
<a class="btn" href="/#p-{p['id']}">اطلب الآن من المتجر</a>
<a class="btn w" href="https://wa.me/{WA}?text={wa_txt}" target="_blank" rel="noopener">اطلب عبر واتساب</a>
<ul class="perks"><li>✔ منتج REMAX أصلي من الوكيل الحصري في العراق (شركة وميض الذهب)</li><li>✔ ضمان 12 شهر واستبدال فوري لأي خلل مصنعي</li><li>✔ توصيل لكل المحافظات بـ 5,000 دينار والدفع عند الاستلام</li></ul></div></div>
{f'<h2>منتجات مشابهة من قسم {cname}</h2><div class="grid">' + "".join(card(x) for x in rel) + '</div>' if rel else ''}"""
    ld = [{"@context": "https://schema.org", "@type": "Product", "name": title, "sku": p["id"], "mpn": p.get("model", ""),
           "brand": {"@type": "Brand", "name": "REMAX"}, "description": desc, "category": cname,
           "image": [f"{SITE}/{i}" for i in im] or [og_img], "url": canon},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": cname, "item": f"{SITE}/c/{cat}.html"},
              {"@type": "ListItem", "position": 3, "name": title, "item": canon}]}]
    if priced(p):
        ld[0]["offers"] = {"@type": "Offer", "price": int(float(p["price"])), "priceCurrency": "IQD", "url": canon,
                           "availability": "https://schema.org/" + ("InStock" if in_stock(p) else "OutOfStock"),
                           "itemCondition": "https://schema.org/NewCondition", "seller": ORG}
    extra = f'<meta property="product:brand" content="REMAX">\n<meta property="product:retailer_item_id" content="{p["id"]}">\n'
    if priced(p):
        extra += f'<meta property="product:price:amount" content="{int(float(p["price"]))}"><meta property="product:price:currency" content="IQD">\n'
    meta_desc = (f"{num(p['price'])} د.ع · " if priced(p) else "") + desc
    with open(f"p/{p['id']}.html", "w", encoding="utf-8") as fh:
        fh.write(page(f"{title} | ريماكس العراق", meta_desc, canon, body, og_img, "product", extra, ld))

# ---------- category pages ----------
os.makedirs("c", exist_ok=True)
for f in os.listdir("c"):
    if f.endswith(".html"): os.remove(os.path.join("c", f))
used = [k for k in CATS if any(p.get("cat") == k for p in P)]
for k in used:
    items = [p for p in P if p.get("cat") == k]
    canon = f"{SITE}/c/{k}.html"
    first = next((imgs_of(p)[0] for p in items if imgs_of(p)), "icons/icon-512.png")
    body = f"""<div class="crumb"><a href="/">الرئيسية</a><span>{CATS[k]}</span></div>
<h1>{CATS[k]} REMAX الأصلية في العراق</h1><p class="intro">{E(CAT_INTRO.get(k,''))} من شركة وميض الذهب، الوكيل الحصري لماركة REMAX في العراق — توصيل لكل المحافظات.</p>
<div class="grid">{"".join(card(p) for p in items)}</div>"""
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": CATS[k],
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/p/{p['id']}.html"} for i, p in enumerate(items)]}]
    with open(f"c/{k}.html", "w", encoding="utf-8") as fh:
        fh.write(page(f"{CATS[k]} ريماكس الأصلية في العراق | REMAX Iraq", CAT_INTRO.get(k, ""), canon, body, f"{SITE}/{first}", ld=ld))

# ---------- sitemap + robots ----------
urls = [(SITE + "/", "1.0")] + [(f"{SITE}/c/{k}.html", "0.8") for k in used] + [(f"{SITE}/p/{p['id']}.html", "0.7") for p in P]
with open("sitemap.xml", "w", encoding="utf-8") as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    fh.write("".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n" for u, pr in urls))
    fh.write("</urlset>\n")
with open("robots.txt", "w", encoding="utf-8") as fh:
    fh.write(f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n")

# ---------- Meta catalog feed ----------
rows = []
for p in P:
    im = imgs_of(p)
    if not priced(p) or not im: continue
    price = int(float(p["price"])); old = p.get("old")
    rows.append({
        "id": p["id"], "title": title_of(p)[:150], "description": (p.get("desc") or p.get("name") or "").strip()[:5000],
        "availability": "in stock" if in_stock(p) else "out of stock", "condition": "new",
        "price": f"{int(float(old)) if old and float(old) > price else price} IQD",
        "sale_price": f"{price} IQD" if old and float(old) > price else "",
        "link": f"{SITE}/p/{p['id']}.html", "image_link": f"{SITE}/{im[0]}",
        "additional_image_link": ",".join(f"{SITE}/{i}" for i in im[1:]),
        "brand": "REMAX", "product_type": CATS.get(p.get("cat"), "متنوعة"),
        "google_product_category": "Electronics", "custom_label_0": "جديد" if p.get("new") else "",
    })
with open("catalog.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"catalog.csv: {len(rows)} products; p/: {len(P)} pages; c/: {len(used)} pages; sitemap: {len(urls)} urls")
