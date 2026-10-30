#!/usr/bin/env python3
"""Builds the site served by GitHub Pages.

  src/index.html            -> index.html
  src/case-carvetrack.html  -> case/carvetrack.html
  src/case-template.html + cases/cases.json -> case/<slug>.html  (one page per case)
  + sitemap.xml, robots.txt, llms.txt

Sources carry no document skeleton (the landing source is also the claude.ai artifact).
Shared CSS, the embedded fonts and the SVG symbol defs are taken from src/index.html, so the
case template only holds what is specific to a case page.
"""
import json, os, re, sys, html, datetime
sys.path.insert(0, os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages"))
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
SITE = "https://01plus.github.io"
TODAY = datetime.date.today().isoformat()

land = open("src/index.html", encoding="utf-8").read()
carve = open("src/case-carvetrack.html", encoding="utf-8").read()
tpl = open("src/case-template.html", encoding="utf-8").read()
cases = json.load(open("cases/cases.json", encoding="utf-8"))

# ---------- pieces shared from the landing source ----------
css_all = re.search(r"<style>\n(.*?)</style>", land, re.S).group(1)
fonts = re.search(r"/\*FONTS-START\*/.*?/\*FONTS-END\*/", css_all, re.S).group(0)
base_css = css_all[css_all.index(":root{"):css_all.index("/* hero */")]
cta_css = css_all[css_all.index("/* cta */"):]
defs = re.search(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true">.*?</svg>\n', land, re.S).group(0)
head_links = re.search(r'(<link rel="preconnect".*?display=swap">\n)', land, re.S).group(1)

ICONS = {
 "product": '<path d="M12 2.5 3.5 7v10L12 21.5l8.5-4.5V7z"/><path d="M3.5 7 12 11.5 20.5 7M12 11.5v10"/>',
 "internship": '<path d="M9 3h6M10 3v6.5L4.5 20h15L14 9.5V3"/><path d="M7 15.5h10"/>',
 "competition": '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3"/>',
 "paper": '<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
 "patent": '<path d="M12 3 4.5 6v6c0 4.8 3.2 8 7.5 9 4.3-1 7.5-4.2 7.5-9V6z"/><path d="m9 12 2 2 4-4"/>',
 "launch": '<path d="M12 2.5c3 2.2 5 6.2 5 10.5l-5 4-5-4c0-4.3 2-8.3 5-10.5z"/><path d="M12 21.5V17M7 13l-3 2.5 3 1.5M17 13l3 2.5-3 1.5"/><circle cx="12" cy="10" r="1.6"/>',
 "brand": '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.5"/>',
 "impact": '<path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z"/>',
 "letter": '<path d="M3 6h18v12H3z"/><path d="m3 7 9 6 9-6"/>',
}
STEPS = [("internship","实习","INTERNSHIP"),("paper","论文","PAPER"),("competition","竞赛","COMPETITION"),("patent","专利","PATENT"),
         ("product","产品","PRODUCT"),("launch","发布","LAUNCH"),("brand","品牌","BRAND"),("impact","社会","IMPACT"),("letter","推荐","LETTER")]

# ---------- images: generated PNGs -> web JPGs ----------
def jpg(src_png, dst_jpg, width=1400, q=80):
    if not os.path.exists(src_png): return False
    if os.path.exists(dst_jpg) and os.path.getmtime(dst_jpg) >= os.path.getmtime(src_png): return True
    from PIL import Image
    im = Image.open(src_png).convert("RGB")
    im.thumbnail((width, width))
    im.save(dst_jpg, quality=q, optimize=True, progressive=True)
    return True

def og_image(src, dst):
    """1200x630 share image from a case hero."""
    if not os.path.exists(src): return False
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src): return True
    from PIL import Image
    im = Image.open(src).convert("RGB"); w, h = im.size; th = round(w * 630 / 1200)
    im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th)).resize((1200, 630), Image.LANCZOS)
    im.save(dst, quality=82, optimize=True); return True

# ---------- fonts: inline in the sources (artifact), shared files on the built site ----------
FACES = [("DOUYU", 400, "douyu-400"), ("PuHui", 300, "puhui-300"), ("PuHui", 700, "puhui-700")]
def font_ver(fn):
    import hashlib
    p = f"assets/fonts/{fn}.woff2"
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else "0"
def font_css(root):
    return "".join(f'@font-face{{font-family:"{fam}";font-weight:{wt};font-style:normal;font-display:swap;src:url({root}assets/fonts/{fn}.woff2?v={font_ver(fn)}) format("woff2")}}\n' for fam, wt, fn in FACES)
def externalize_fonts(body, root):
    return re.sub(r"/\*FONTS-START\*/.*?/\*FONTS-END\*/", lambda m: font_css(root), body, flags=re.S)
def font_preloads(root):
    return "".join(f'<link rel="preload" href="{root}assets/fonts/{fn}.woff2?v={font_ver(fn)}" as="font" type="font/woff2" crossorigin>\n' for _, _, fn in FACES)

# ---------- document skeleton with SEO head ----------
def shell(body, *, title, desc, path, root, og, jsonld=None, ogtype="website"):
    url = SITE + path
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n' for j in (jsonld or []))
    return (
        '<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        f'<title>{html.escape(title)}</title>\n'
        f'<meta name="description" content="{html.escape(desc)}">\n'
        f'<link rel="canonical" href="{url}">\n'
        '<meta name="robots" content="index,follow,max-image-preview:large">\n'
        '<meta name="theme-color" content="#5040bf">\n'
        f'<meta property="og:type" content="{ogtype}">\n<meta property="og:site_name" content="01+ 名校背景提升">\n'
        f'<meta property="og:locale" content="zh_CN">\n<meta property="og:title" content="{html.escape(title)}">\n'
        f'<meta property="og:description" content="{html.escape(desc)}">\n<meta property="og:url" content="{url}">\n'
        f'<meta property="og:image" content="{SITE}/{og}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{html.escape(title)}">\n<meta name="twitter:description" content="{html.escape(desc)}">\n'
        f'<meta name="twitter:image" content="{SITE}/{og}">\n'
        f'<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">\n'
        f'<link rel="icon" href="{root}assets/favicon-32.png" type="image/png" sizes="32x32">\n'
        f'<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">\n'
        + font_preloads(root) + ld +
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        '</head>\n<body>\n' + externalize_fonts(body, root) + '\n</body>\n</html>\n')

ORG = {"@context":"https://schema.org","@type":"EducationalOrganization","name":"01+ 名校背景提升","alternateName":"01plus",
       "url":SITE,"logo":SITE+"/assets/apple-touch-icon.png","description":"01+ 通过「一个项目 × 多元成果」培养模式，陪伴学员从一个真实项目出发，产出实习、论文、竞赛、专利、产品、发布、品牌、社会影响与推荐信等多元成果，申请世界名校。",
       "address":{"@type":"PostalAddress","streetAddress":"920 Roosevelt, Suite 200","addressLocality":"Irvine","addressRegion":"CA","addressCountry":"US"},
       "founder":{"@type":"Person","name":"孙宇","jobTitle":"创始人 · 计算机系终身教授"},"areaServed":["US","CN","CA"],"sameAs":["https://01plus.ai"]}

# ---------- landing ----------
faq = re.findall(r'<details class="q">\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>', land, re.S)
land_ld = [ORG, {"@context":"https://schema.org","@type":"WebSite","name":"01+ 名校背景提升","url":SITE,"inLanguage":"zh-CN"}]
if faq:
    land_ld.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":re.sub("<.*?>","",q).strip(),
        "acceptedAnswer":{"@type":"Answer","text":re.sub("<.*?>","",a).strip()}} for q,a in faq]})
og_image("assets/hero.jpg", "assets/og-home.jpg") if not os.path.exists("assets/og-home.jpg") else None
open("index.html","w",encoding="utf-8").write(shell(land, title="01+ 名校背景提升 · 一个项目，多元成果",
    desc="01+ 名校背景提升：陪伴学员从一个真实项目出发，产出实习、论文、竞赛、专利、产品、发布、品牌、社会影响与推荐信等多元成果。哈耶普斯麻录取率 20%+，Top 30 名校录取率 90%+。",
    path="/", root="", og="assets/og-home.jpg", jsonld=land_ld))
print("built index.html")

# ---------- CarveTrack film page ----------
og_image("assets/m-admit.jpg", "assets/og-carvetrack.jpg")
open("case/carvetrack.html","w",encoding="utf-8").write(shell(carve, title="示例项目计划：一个滑雪少年的 30 个月 · 01+",
    desc="以 CarveTrack 多模态滑雪传感器为例，按月展示一个项目如何从一个真实的问题出发，产出实习、产品、竞赛、论文、专利、品牌、社会影响与推荐信，最终叩开名校大门。",
    path="/case/carvetrack.html", root="../", og="assets/og-carvetrack.jpg", ogtype="article",
    jsonld=[{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"首页","item":SITE+"/"},{"@type":"ListItem","position":2,"name":"示例项目计划 · CarveTrack","item":SITE+"/case/carvetrack.html"}]}]))
print("built case/carvetrack.html")

# ---------- case pages ----------
def esc(s): return html.escape(s, quote=True)
def card(c, root):
    return (f'<a class="card" href="{root}case/{c["slug"]}.html"><div class="pic"><img src="{root}assets/cases/{c["slug"]}-hero-720.jpg" srcset="{root}assets/cases/{c["slug"]}-hero-720.jpg 720w, {root}assets/cases/{c["slug"]}-hero.jpg 1400w" sizes="(max-width:860px) 100vw, 33vw" alt="{esc(c["project"])}" loading="lazy" width="1400" height="933"></div>'
            f'<div class="t"><i>{esc(c["major"])}</i><h3>{esc(c["project"])}</h3><em style="--c:{c["color"]}">{esc(c["school"])}</em></div></a>')

for i, c in enumerate(cases):
    for k in ("hero","cover","s1","s2","s3"):
        jpg(f"assets/cases/{c['slug']}-{k}.png", f"assets/cases/{c['slug']}-{k}.jpg")
    og_image(f"assets/cases/{c['slug']}-hero.jpg", f"assets/cases/{c['slug']}-og.jpg")
    src720 = f"assets/cases/{c['slug']}-hero.png"; src720 = src720 if os.path.exists(src720) else f"assets/cases/{c['slug']}-hero.jpg"
    jpg(src720, f"assets/cases/{c['slug']}-hero-720.jpg", width=720, q=78)
    srccov = f"assets/cases/{c['slug']}-cover.png"; srccov = srccov if os.path.exists(srccov) else f"assets/cases/{c['slug']}-cover.jpg"
    jpg(srccov, f"assets/cases/{c['slug']}-cover-720.jpg", width=720, q=82)
    steps = []
    for n, (key, zh, en) in enumerate(STEPS):
        steps.append(f'<li class="st"><span class="ic"><svg viewBox="0 0 24 24">{ICONS[key]}</svg></span><div><div class="hd"><h3>{zh}</h3><i>{n+1:02d} · {en}</i></div><p>{esc(c["outcomes"][key])}</p></div></li>')
    scenes = []
    for k, zh in (("s1","科研与开发"),("s2","竞赛与展示"),("s3","落地与影响")):
        if os.path.exists(f"assets/cases/{c['slug']}-{k}.jpg"):
            scenes.append(f'<figure><img src="../assets/cases/{c["slug"]}-{k}.jpg" alt="{esc(c["project"])} · {zh}" loading="lazy" width="1400" height="933"><figcaption>{zh}</figcaption></figure>')
    stats = "".join(f'<div class="stat"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in c["stats"])
    nine = "".join(f'<li><span class="ic"><svg viewBox="0 0 24 24">{ICONS[key]}</svg></span>{zh}</li>' for key, zh, en in STEPS)
    outcomes = (f'<div class="hd"><b>9<i>/9</i></b><span>种成果全部达成</span></div><ul class="nine">{nine}</ul>'
                f'<div class="hl"><small>亮点数据</small><div class="row">{stats}</div></div>')
    seals = f'<img src="../assets/logos/{c["logo"]}.png" alt="{esc(c["schoolEn"])}">' + (f'<img src="../assets/logos/{c["logo2"]}.png" alt="">' if c.get("logo2") else "")
    others = "".join(card(cases[(i + d) % len(cases)], "../") for d in (1, 2, 3))
    page = tpl
    for k, v in {
        "FONTS": fonts, "BASE_CSS": base_css, "CTA_CSS": cta_css, "DEFS": defs, "HEAD_LINKS": head_links,
        "PROJECT": esc(c["project"]), "PROJECT_EN": esc(c["en"]), "NAME": esc(c["name"]), "MAJOR": esc(c["major"]), "MAJOR_LABEL": esc(c["major"] + ("" if c["major"].endswith("学院") else "专业")),
        "SCHOOL": esc(c["school"]), "SCHOOL_EN": esc(c["schoolEn"]), "COLOR": c["color"], "SLUG": c["slug"],
        "SUMMARY": esc(c["summary"]), "PROBLEM": esc(c["problem"]), "PROBLEM_TITLE": esc(c.get("problemTitle","从一个真实的问题开始")), "STEPS": "".join(steps), "SCENES": "".join(scenes), "STATS": stats, "OUTCOMES": outcomes,
        "SEALS": seals, "OTHERS": others,
    }.items():
        page = page.replace("{{" + k + "}}", v)
    assert "{{" not in page, re.findall(r"\{\{\w+\}\}", page)[:3]
    title = f"{c['project']} · {c['name']} 录取{c['school']} · 01+ 案例"
    desc = f"{c['name']}，{c['major']}方向，{c['school']}录取。{c['summary'][:70]}…"
    ld = [{"@context":"https://schema.org","@type":"Article","headline":title,"inLanguage":"zh-CN","image":f"{SITE}/assets/cases/{c['slug']}-og.jpg",
           "author":{"@type":"Organization","name":"01+ 名校背景提升"},"publisher":ORG,"description":c["summary"],"mainEntityOfPage":f"{SITE}/case/{c['slug']}.html","datePublished":"2026-10-29"},
          {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"首页","item":SITE+"/"},{"@type":"ListItem","position":2,"name":"具体案例","item":SITE+"/#cases"},{"@type":"ListItem","position":3,"name":c["project"],"item":f"{SITE}/case/{c['slug']}.html"}]}]
    open(f"case/{c['slug']}.html","w",encoding="utf-8").write(shell(page, title=title, desc=desc, path=f"/case/{c['slug']}.html", root="../",
        og=f"assets/cases/{c['slug']}-og.jpg", jsonld=ld, ogtype="article"))
print(f"built {len(cases)} case pages")

# ---------- 404 ----------
nf = ('<nav class="nav wrap" id="nav"><div class="in"><a class="brand" href="/" aria-label="01+"><svg viewBox="0 0 425.2 425.2"><use href="#mark"/></svg><svg viewBox="0 0 505 312" fill="currentColor"><use href="#word"/></svg></a><a class="btn" href="/#contact">预约咨询</a></div></nav>'
      '<section class="wrap" style="min-height:100svh;display:grid;place-items:center;text-align:center;padding-block:6rem"><div class="in"><div class="eyebrow">404</div>'
      '<h1 style="font-size:clamp(2rem,6vw,4.5rem);margin:.6rem 0 1rem">这一页还没有从 0 走到 1</h1><p style="color:var(--fg-2);margin:0 0 1.8rem">你要找的页面不存在，或者已经移动。</p>'
      '<a class="btn p" href="/">回到首页<span class="ar"></span></a></div></section>')
open("404.html","w",encoding="utf-8").write(shell('<style>'+fonts+'\n'+base_css+cta_css+'</style>\n'+defs+nf, title="页面不存在 · 01+", desc="页面不存在。", path="/404.html", root="/", og="assets/og-home.jpg"))
print("built 404.html")

# ---------- sitemap, robots, llms.txt ----------
urls = ["/", "/case/carvetrack.html"] + [f"/case/{c['slug']}.html" for c in cases]
open("sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{'weekly' if u=='/' else 'monthly'}</changefreq><priority>{'1.0' if u=='/' else '0.8'}</priority></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt","w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
open("llms.txt","w",encoding="utf-8").write("# 01+ 名校背景提升\n\n> 01+ 通过「一个项目 × 多元成果」培养模式，陪伴学员从一个真实项目出发，产出实习、论文、竞赛、专利、产品、发布、品牌、社会影响与推荐信等多元成果，申请世界名校。总校位于美国加州 Irvine。\n\n"
    "## 核心数据\n- 10+ 年科创项目经验，700+ 位学员\n- 哈耶普斯麻录取率 20%+；Top 30 名校录取率 90%+；Top 50 名校录取率 100%\n- 2024–2026 录取名单覆盖 35 所院校，见首页\n\n## 方法\n开展调研 → 明确选题 → 制定计划 → 全程陪跑；围绕一个项目持续产出：产品、实习、竞赛、论文、专利、发布、品牌、社会影响、推荐信。\n\n## 案例\n" +
    "".join(f"- [{c['project']} · {c['name']} → {c['school']}]({SITE}/case/{c['slug']}.html)\n" for c in cases) +
    f"- [示例项目计划：CarveTrack 多模态滑雪传感器]({SITE}/case/carvetrack.html)\n\n## 联系\n微信扫码预约免费名校背景规划，获得定制策划书。地址：920 Roosevelt, Suite 200, Irvine, CA。官网 https://01plus.ai\n")
print("wrote sitemap.xml, robots.txt, llms.txt")
