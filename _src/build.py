#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ตัวสร้างหน้าคู่มือติดตั้งแอพแบบ multi-brand.

วิธีใช้:
    python build.py <brand-folder-name>     # สร้างเจ้าเดียว
    python build.py --all                    # สร้างทุกเจ้าใน _src/brands/

แต่ละเจ้าอยู่ที่ _src/brands/<Name>/ ประกอบด้วย:
    brand.json           ← config (ชื่อ, ข้อความ, caption แต่ละสเต็ป)
    ios.pdf              ← สไลด์ iOS (หน้า 1 = ปก, หน้า 2..N = สเต็ป)
    android.pdf          ← สไลด์ Android (หน้า 1 = ปก, หน้า 2..N = สเต็ป)

ผลลัพธ์: <repo>/<Name>/index.html + <repo>/<Name>/img/*.jpg  (self-contained)
"""
import sys, os, io, json, html, shutil

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError:
    sys.exit("ต้องติดตั้ง dependency ก่อน — รันผ่าน ./build.sh (จะสร้าง venv ให้เอง)")

SRC   = os.path.dirname(os.path.abspath(__file__))
REPO  = os.path.dirname(SRC)                       # โฟลเดอร์ที่ GitHub Pages เสิร์ฟ
BRANDS= os.path.join(SRC, "brands")
TEMPLATE = os.path.join(SRC, "template.html")
DPI = 170
JPEG_Q = 86


def render_pages(pdf_path, out_dir, prefix):
    """render หน้า 2..N ของ pdf เป็น img/<prefix>_<k>.jpg ; คืนจำนวนสเต็ป (N-1)."""
    doc = fitz.open(pdf_path)
    n = doc.page_count
    if n < 2:
        doc.close()
        raise SystemExit(f"{pdf_path}: ต้องมีอย่างน้อย 2 หน้า (ปก + สเต็ป)")
    for k in range(2, n + 1):
        pix = doc[k - 1].get_pixmap(dpi=DPI)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        img.save(os.path.join(out_dir, f"{prefix}_{k}.jpg"),
                 "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
    doc.close()
    return n - 1


def render_logo(cfg, brand_dir, out_dir):
    """crop โลโก้จากปกของ pdf ที่ระบุ → img/logo.jpg"""
    lg = cfg.get("logo", {})
    src = os.path.join(brand_dir, lg.get("source", "ios.pdf"))
    page = lg.get("page", 1)
    crop = lg.get("crop", [0.305, 0.35, 0.695, 0.83])   # ค่าเริ่มต้นที่จูนไว้กับสไลด์ปกทรงสี่เหลี่ยม
    doc = fitz.open(src)
    pix = doc[page - 1].get_pixmap(dpi=DPI)
    doc.close()
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    w, h = im.size
    box = (int(w*crop[0]), int(h*crop[1]), int(w*crop[2]), int(h*crop[3]))
    im.crop(box).save(os.path.join(out_dir, "logo.jpg"), "JPEG", quality=90, optimize=True)


def steps_html(steps, count, prefix, plat_label):
    """สร้าง HTML การ์ดสเต็ป ; caption จาก config, จำนวนอิงตามหน้า PDF จริง."""
    out = []
    for i in range(count):
        n = i + 1
        step = steps[i] if i < len(steps) else {}
        cap = step.get("caption") or f"ຂັ້ນຕອນທີ {n}"     # ถ้าไม่มี caption ใช้ค่า default
        alt = html.escape(step.get("alt", f"{plat_label} step {n}"), quote=True)
        img = f"img/{prefix}_{n+1}.jpg"                    # หน้า PDF = n+1 (หน้า1=ปก)
        out.append(
            f'    <div class="step">\n'
            f'      <div class="step-head"><div class="num">{n}</div>\n'
            f'        <h3>{cap}</h3></div>\n'
            f'      <a class="shot" href="{img}"><img src="{img}" alt="{alt}" loading="lazy"></a>\n'
            f'    </div>'
        )
    return "\n\n".join(out)


def build(brand_name):
    brand_dir = os.path.join(BRANDS, brand_name)
    cfg_path = os.path.join(brand_dir, "brand.json")
    if not os.path.isfile(cfg_path):
        raise SystemExit(f"ไม่พบ {cfg_path}")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)

    slug = cfg.get("slug", brand_name)                # path ที่จะ deploy: /<slug>/
    out_root = os.path.join(REPO, slug)
    out_img = os.path.join(out_root, "img")
    if os.path.isdir(out_img):
        shutil.rmtree(out_img)
    os.makedirs(out_img, exist_ok=True)

    # 1) รูป
    ios_n = render_pages(os.path.join(brand_dir, cfg["ios"].get("pdf", "ios.pdf")),   out_img, "ios")
    and_n = render_pages(os.path.join(brand_dir, cfg["android"].get("pdf", "android.pdf")), out_img, "and")
    render_logo(cfg, brand_dir, out_img)

    # 2) เติม template
    ios_steps = steps_html(cfg["ios"].get("steps", []),     ios_n, "ios", "iOS")
    and_steps = steps_html(cfg["android"].get("steps", []), and_n, "and", "Android")

    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()

    brand = cfg["name"]
    repl = {
        "LANG":        cfg.get("lang", "lo"),
        "THEME_COLOR": cfg.get("themeColor", "#0a1327"),
        "TITLE":       cfg.get("title",  f"ຄູ່ມືຕິດຕັ້ງແອັບ {brand} — iOS & Android"),
        "DESC":        cfg.get("desc",   f"ຄູ່ມືການຕິດຕັ້ງແອັບ {brand} ສຳລັບ iOS ແລະ Android"),
        "OG_TITLE":    cfg.get("ogTitle", f"ຄູ່ມືຕິດຕັ້ງແອັບ {brand}"),
        "OG_DESC":     cfg.get("ogDesc",  cfg.get("heroSub", "")),
        "BRAND":       brand,
        "SUBTITLE":    cfg.get("subtitle", "ຄູ່ມືຕິດຕັ້ງແອັບ"),
        "HERO_TITLE":  cfg.get("heroTitle", f"ຄູ່ມືການຕິດຕັ້ງແອັບ {brand}"),
        "HERO_SUB":    cfg.get("heroSub", "ຕິດຕັ້ງງ່າຍໆ ພຽງບໍ່ກີ່ຂັ້ນຕອນ — ເລືອກລະບົບຂອງທ່ານດ້ານລຸ່ມ"),
        "ZOOM_HINT":   cfg.get("zoomHint", "🔍 ແຕະເພື່ອຂະຫຍາຍ"),
        "IOS_TAB":     cfg.get("ios", {}).get("tab", "iPhone / iOS"),
        "AND_TAB":     cfg.get("android", {}).get("tab", "Android"),
        "IOS_INTRO":   cfg["ios"].get("intro", f"ຕິດຕັ້ງແອັບ {brand} ເທິງ iPhone (iOS) ຕາມ {ios_n} ຂັ້ນຕອນລຸ່ມນີ້"),
        "AND_INTRO":   cfg["android"].get("intro", f"ຕິດຕັ້ງແອັບ {brand} ເທິງ Android ຕາມ {and_n} ຂັ້ນຕອນລຸ່ມນີ້"),
        "IOS_STEPS":   ios_steps,
        "AND_STEPS":   and_steps,
        "IOS_DONE":    cfg["ios"].get("done", "✅ ຕິດຕັ້ງສຳເລັດ! ເປີດແອັບໃຊ້ງານໄດ້ເລີຍ"),
        "AND_DONE":    cfg["android"].get("done", "✅ ຕິດຕັ້ງສຳເລັດ! ເປີດແອັບໃຊ້ງານໄດ້ເລີຍ"),
        "SUPPORT":     cfg.get("support", "🕐 ຫາກພົບບັນຫາ ຕິດຕໍ່ແອັດມິນໄດ້ຕະຫຼອດ 24 ຊົ່ວໂມງ"),
        "FOOTER":      cfg.get("footer", f"© {brand} · ຄູ່ມືການຕິດຕັ້ງແອັບ"),
    }
    for k, v in repl.items():
        tpl = tpl.replace(f"%%{k}%%", str(v))

    if "%%" in tpl:
        leftover = [w for w in tpl.split("%%")[1::2]][:5]
        raise SystemExit(f"ยังมี placeholder ค้าง: {leftover}")

    with open(os.path.join(out_root, "index.html"), "w", encoding="utf-8") as f:
        f.write(tpl)

    print(f"✓ {brand}: /{slug}/  (iOS {ios_n} สเต็ป, Android {and_n} สเต็ป)  → {out_root}")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--all":
        names = sorted(d for d in os.listdir(BRANDS)
                       if os.path.isfile(os.path.join(BRANDS, d, "brand.json")))
        if not names:
            sys.exit("ไม่พบเจ้าใดใน _src/brands/")
        for n in names:
            build(n)
    else:
        for n in args:
            build(n)


if __name__ == "__main__":
    main()
