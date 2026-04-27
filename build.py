import os, base64, json
from PIL import Image, ImageOps
import io

# ── 폴더 설정 ──────────────────────────
PHOTOS_DIR = 'photos'   # 사진 업로드 폴더
OUTPUT_DIR = 'docs'     # 앨범 출력 폴더

# ── 이미지 → base64 변환 ────────────────
def encode_image(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)        # 방향 자동 교정
    img.thumbnail((1100, 1100), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=74, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

# ── 앨범 1개 빌드 ───────────────────────
def build_album(event_name, image_paths):
    items = []
    for path in sorted(image_paths):
        print(f"  처리 중: {os.path.basename(path)}")
        src = encode_image(path)
        cap = os.path.basename(path).rsplit('.', 1)[0].replace('_', ' ')
        items.append({
            'src':   src,
            'cap':   cap,
            'fname': os.path.basename(path)
        })

    # 폴더명에서 제목 파싱
    # 예) 2026_04_Fishing → title=Fishing, date=2026.04
    parts = event_name.split('_')
    if len(parts) >= 3:
        title    = ' '.join(parts[2:])
        date     = parts[0] + '.' + parts[1]
    else:
        title    = event_name
        date     = ''
    location = 'Geoje, South Korea'

    html = build_html(title, date, location, items)

    out_dir = os.path.join(OUTPUT_DIR, event_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"완료: {event_name} ({len(items)}장) → {out_path}")

# ── HTML 생성 ───────────────────────────
def build_html(title, date, location, items):
    gallery_js = json.dumps(items)

    cards = ''
    for i, item in enumerate(items):
        cards += (
            f'<div class="mitem" onclick="openLB({i})">'
            f'<img src="{item["src"]}" alt="{item["cap"]}" loading="lazy">'
            f'<div class="veil"></div>'
            f'<div class="info"><div class="info-cap">{item["cap"]}</div></div>'
            f'<a class="dl" onclick="event.stopPropagation()" '
            f'href="{item["src"]}" download="SHI_{item["fname"]}" target="_blank">&#8595;</a>'
            f'</div>'
        )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="SHI — {title}">
<meta property="og:description" content="Samsung Heavy Industries · Official Photo Album">
<title>SHI — {title}</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@300;400;600&display=swap" rel="stylesheet">
<style>
:root{{--ink:#070d18;--deep:#0b1a2e;--gold:#c8a020;--gold2:#e8c84a;--rule:rgba(200,160,32,0.22);}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{background:var(--ink);color:#fff;font-family:"Barlow Condensed",sans-serif;overflow-x:hidden;}}
.cover{{height:100vh;min-height:600px;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;}}
#cover-bg{{position:absolute;inset:0;background-size:cover;background-position:center;background-repeat:no-repeat;filter:brightness(0.18) saturate(0.6);transform:scale(1.04);}}
.cover-grad{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 80%,rgba(14,53,96,.5) 0%,transparent 65%),linear-gradient(to top,rgba(7,13,24,1) 0%,transparent 40%);}}
.cover-body{{position:relative;z-index:2;text-align:center;padding:0 32px;}}
.cover-eyebrow{{font-size:10px;letter-spacing:.6em;color:var(--gold);text-transform:uppercase;margin-bottom:22px;animation:up .9s ease both;}}
.cover-h1{{font-family:"Bebas Neue";font-size:clamp(72px,13vw,156px);line-height:.9;letter-spacing:.03em;animation:up .9s .12s ease both;}}
.cover-h1 em{{display:block;font-style:normal;color:var(--gold);font-size:.55em;letter-spacing:.1em;}}
.cover-rule{{width:100px;height:1px;margin:30px auto;background:linear-gradient(to right,transparent,var(--gold),transparent);animation:up .9s .24s ease both;}}
.cover-meta{{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;animation:up .9s .36s ease both;}}
.cover-meta span{{font-size:12px;letter-spacing:.28em;color:rgba(255,255,255,.4);text-transform:uppercase;}}
.cover-meta .sep{{margin:0 14px;color:var(--gold);opacity:.5;}}
.scroll-hint{{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:10px;animation:up .9s .8s ease both;}}
.scroll-hint span{{font-size:9px;letter-spacing:.4em;color:rgba(255,255,255,.2);text-transform:uppercase;}}
.scroll-line{{width:1px;height:46px;background:linear-gradient(to bottom,var(--gold),transparent);animation:blink 2s infinite;}}
.gallery{{max-width:1320px;margin:0 auto;padding:80px 24px 100px;}}
.gallery-header{{text-align:center;margin-bottom:60px;}}
.gallery-header h2{{font-family:"Bebas Neue";font-size:clamp(40px,6vw,76px);letter-spacing:.04em;}}
.gallery-header p{{margin-top:10px;font-size:13px;letter-spacing:.22em;color:rgba(255,255,255,.3);text-transform:uppercase;}}
.masonry{{columns:3 300px;column-gap:10px;}}
.mitem{{break-inside:avoid;margin-bottom:10px;position:relative;overflow:hidden;border-radius:3px;cursor:pointer;background:var(--deep);display:block;}}
.mitem img{{width:100%;display:block;transition:transform .55s cubic-bezier(.25,.46,.45,.94),filter .3s;filter:brightness(0.88);}}
.mitem:hover img{{transform:scale(1.04);filter:brightness(1);}}
.veil{{position:absolute;inset:0;background:linear-gradient(to top,rgba(7,13,24,.88) 0%,transparent 55%);opacity:0;transition:opacity .3s;pointer-events:none;}}
.mitem:hover .veil{{opacity:1;}}
.info{{position:absolute;bottom:0;left:0;right:0;padding:16px 14px;transform:translateY(5px);opacity:0;transition:all .3s;pointer-events:none;}}
.mitem:hover .info{{transform:translateY(0);opacity:1;}}
.info-cap{{font-size:13px;font-weight:600;letter-spacing:.04em;line-height:1.3;}}
.dl{{position:absolute;top:10px;right:10px;width:32px;height:32px;border-radius:50%;background:rgba(7,13,24,.75);backdrop-filter:blur(6px);border:1px solid rgba(200,160,32,.4);color:var(--gold2);font-size:13px;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .25s;text-decoration:none;z-index:10;}}
.mitem:hover .dl{{opacity:1;}}
.dl:hover{{background:rgba(200,160,32,.25);}}
.lb{{display:none;position:fixed;inset:0;z-index:900;background:rgba(4,8,14,.97);flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:24px;}}
.lb.open{{display:flex;}}
.lb>img{{max-width:90vw;max-height:80vh;object-fit:contain;border-radius:3px;box-shadow:0 40px 100px rgba(0,0,0,.9);}}
.lb-cap{{font-size:12px;letter-spacing:.18em;color:rgba(255,255,255,.3);text-transform:uppercase;text-align:center;max-width:600px;}}
.lb-bar{{display:flex;gap:10px;}}
.lb-btn{{padding:9px 24px;border-radius:3px;font-family:"Barlow Condensed";font-size:12px;letter-spacing:.2em;text-transform:uppercase;cursor:pointer;border:none;text-decoration:none;display:inline-flex;align-items:center;gap:7px;transition:background .2s;}}
.lb-close{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);color:rgba(255,255,255,.55);}}
.lb-close:hover{{background:rgba(255,255,255,.15);color:#fff;}}
.lb-dl{{background:var(--gold);color:var(--ink);font-weight:700;}}
.lb-dl:hover{{background:var(--gold2);}}
.lb-prev,.lb-next{{position:fixed;top:50%;transform:translateY(-50%);width:48px;height:48px;border-radius:50%;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);color:rgba(255,255,255,.6);font-size:20px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:background .2s;z-index:10;}}
.lb-prev{{left:16px;}}.lb-next{{right:16px;}}
.lb-prev:hover,.lb-next:hover{{background:rgba(200,160,32,.2);color:#fff;}}
footer{{background:#030609;border-top:1px solid var(--rule);padding:52px 28px;text-align:center;}}
.footer-logo{{font-family:"Bebas Neue";font-size:38px;color:var(--gold);letter-spacing:.1em;margin-bottom:10px;}}
.footer-sub{{font-size:10px;letter-spacing:.3em;color:rgba(255,255,255,.2);text-transform:uppercase;line-height:2;}}
@keyframes up{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes blink{{0%,100%{{opacity:.4;}}50%{{opacity:1;}}}}
.fi{{opacity:0;transform:translateY(24px);transition:opacity .6s ease,transform .6s ease;}}
.fi.vis{{opacity:1;transform:translateY(0);}}
@media(max-width:900px){{.masonry{{columns:2 200px;}}}}
@media(max-width:480px){{.masonry{{columns:1;}}.mitem{{margin-bottom:6px;border-radius:0;}}.lb-prev{{left:6px;}}.lb-next{{right:6px;}}}}
</style>
</head>
<body>
<section class="cover">
  <div id="cover-bg"></div>
  <div class="cover-grad"></div>
  <div class="cover-body">
    <div class="cover-eyebrow">Samsung Heavy Industries · Official Photo Album</div>
    <h1 class="cover-h1">SHI<br><em>{title}</em></h1>
    <div class="cover-rule"></div>
    <div class="cover-meta">
      <span>{date}</span><span class="sep">·</span><span>{location}</span>
    </div>
  </div>
  <div class="scroll-hint"><span>Scroll</span><div class="scroll-line"></div></div>
</section>
<section class="gallery fi" id="gallery">
  <div class="gallery-header">
    <h2>{title}</h2>
    <p>Samsung Heavy Industries &nbsp;·&nbsp; {date} &nbsp;·&nbsp; {location}</p>
  </div>
  <div class="masonry" id="masonry">{cards}</div>
</section>
<footer>
  <div class="footer-logo">SHI · {title}</div>
  <div class="footer-sub">Samsung Heavy Industries<br>{date} · {location}<br>Internal Commemorative Use Only</div>
</footer>
<div class="lb" id="lb">
  <button class="lb-prev" onclick="navLB(-1)">&#8592;</button>
  <button class="lb-next" onclick="navLB(1)">&#8594;</button>
  <img id="lb-img" src="" alt="">
  <div class="lb-cap" id="lb-cap"></div>
  <div class="lb-bar">
    <button class="lb-btn lb-close" onclick="closeLB()">&#x2715;&nbsp;Close</button>
    <a class="lb-btn lb-dl" id="lb-dl" href="" download="" target="_blank">&#8595;&nbsp;Download</a>
  </div>
</div>
<script>
var GALLERY={gallery_js};
var cur=0;
document.getElementById("cover-bg").style.backgroundImage='url("'+GALLERY[0].src+'")';
function openLB(i){{cur=i;renderLB();document.getElementById("lb").classList.add("open");document.body.style.overflow="hidden";}}
function closeLB(){{document.getElementById("lb").classList.remove("open");document.body.style.overflow="";}}
function navLB(d){{cur=(cur+d+GALLERY.length)%GALLERY.length;renderLB();}}
function renderLB(){{var g=GALLERY[cur];document.getElementById("lb-img").src=g.src;document.getElementById("lb-cap").textContent=(cur+1)+" / "+GALLERY.length+" — "+g.cap;var dl=document.getElementById("lb-dl");dl.href=g.src;dl.download="SHI_"+g.fname;}}
document.addEventListener("keydown",function(e){{if(!document.getElementById("lb").classList.contains("open"))return;if(e.key==="Escape")closeLB();if(e.key==="ArrowRight")navLB(1);if(e.key==="ArrowLeft")navLB(-1);}});
document.getElementById("lb").addEventListener("click",function(e){{if(e.target===this)closeLB();}});
var ob=new IntersectionObserver(function(entries){{entries.forEach(function(e){{if(e.isIntersecting)e.target.classList.add("vis");}});}},{{threshold:0.06}});
document.querySelectorAll(".fi").forEach(function(el){{ob.observe(el);}});
</script>
</body>
</html>'''

# ── 메인 실행 ───────────────────────────
if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(PHOTOS_DIR):
        print(f"photos 폴더가 없습니다.")
        exit(0)

    events = [
        d for d in os.listdir(PHOTOS_DIR)
        if os.path.isdir(os.path.join(PHOTOS_DIR, d))
    ]

    if not events:
        print("처리할 행사 폴더가 없습니다.")
        exit(0)

    for event in sorted(events):
        event_path = os.path.join(PHOTOS_DIR, event)
        images = [
            os.path.join(event_path, f)
            for f in os.listdir(event_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if images:
            print(f"\n[{event}] {len(images)}장 처리 시작...")
            build_album(event, images)

    print("\n전체 완료!")
