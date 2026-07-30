#!/usr/bin/env python3
"""Print-ready physical business card (front + back) for a print shop.

Colours come from the same card.json theme as the web card, so the two can never
drift apart.

    ./.venv/bin/python print_card.py
    weasyprint \
        print/card.html print/business-card-PRINT.pdf

Trim 3.5x2in (US standard) + 0.125in bleed on all sides = 3.75x2.25in page.
Everything important stays inside a 0.125in safety margin from trim.
"""
import json
import pathlib

import qrcode
from qrcode.constants import ERROR_CORRECT_Q

import theme

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "print"
FONTS = ROOT / "fonts"
C, T = theme.load()
OUT.mkdir(exist_ok=True)

full_name = " ".join(p for p in [C["first_name"], C["last_name"]] if p)

# High error-correction so the code still scans if the print is scuffed or the
# card is picked up off a table at an angle.
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=40, border=2)
qr.add_data(C["card_url"])
qr.make(fit=True)
qr.make_image(fill_color=T["ink"], back_color="white").save(OUT / "qr-print.png")

# Same code, big and standalone — for slides, badges, email signatures, a phone
# lock screen. Pure black so it scans off any background.
qr2 = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=60, border=2)
qr2.add_data(C["card_url"])
qr2.make(fit=True)
qr2.make_image(fill_color="black", back_color="white").save(OUT / "qr-standalone.png")

logo = ROOT / "logo.png"
if not logo.exists():
    logo = ROOT / "dist" / C["logo"]

HTML = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
  @font-face {{ font-family:Inter; font-weight:400; src:url("file://{FONTS}/Inter-400.ttf"); }}
  @font-face {{ font-family:Inter; font-weight:700; src:url("file://{FONTS}/Inter-700.ttf"); }}
  @font-face {{ font-family:Inter; font-weight:900; src:url("file://{FONTS}/Inter-900.ttf"); }}
  @font-face {{ font-family:JBMono; font-weight:400; src:url("file://{FONTS}/JetBrainsMono-400.ttf"); }}
  @font-face {{ font-family:JBMono; font-weight:500; src:url("file://{FONTS}/JetBrainsMono-500.ttf"); }}
  @font-face {{ font-family:JBMono; font-weight:700; src:url("file://{FONTS}/JetBrainsMono-700.ttf"); }}

  @page {{ size:3.75in 2.25in; margin:0; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  .face {{
    width:3.75in; height:2.25in; page-break-after:always;
    position:relative; overflow:hidden;
  }}
  /* 0.125in bleed + 0.125in safety = 0.25in of breathing room from page edge */
  /* No flexbox and no `inset` here — WeasyPrint supports neither, and silently
     falling back to block layout left-aligns the images. table-cell centring is
     the reliable print-engine idiom. And a table with left/right offsets still
     shrink-wraps its content, so the safe area gets explicit dimensions:
     3.75-0.5 wide x 2.25-0.5 tall. */
  .safe {{ position:absolute; top:0.25in; left:0.25in;
          display:table; width:3.25in; height:1.75in; }}
  .mid {{ display:table-cell; vertical-align:middle; text-align:center; }}

  .front {{ background:{T["ink"]}; }}
  .front .logo {{ width:1.15in; display:inline-block; }}
  .rule {{ width:0.85in; height:0.75pt; background:{T["accent_deep"]};
           margin:6.5pt auto 7pt; }}
  .name {{ font-family:Inter; font-weight:900; text-transform:uppercase;
           font-size:13pt; letter-spacing:-0.3pt; color:{T["dark_ink"]}; line-height:1;
           white-space:nowrap; }}
  .role {{ font-family:JBMono; font-weight:500; text-transform:uppercase;
           font-size:5.4pt; letter-spacing:1.5pt; color:{T["accent"]}; margin-top:5pt; }}
  .what {{ font-family:JBMono; font-weight:400; font-size:5pt; letter-spacing:0.35pt;
           color:{T["dark_muted"]}; margin-top:4pt; }}
  .contact {{ position:absolute; left:0.25in; right:0.25in; bottom:0.235in;
              font-family:JBMono; font-weight:400; font-size:5.2pt;
              letter-spacing:0.3pt; color:{T["dark_ink"]}; text-align:center; }}
  .contact span {{ color:{T["accent_deep"]}; padding:0 3pt; }}

  .back {{ background:{T["paper"]}; }}
  .back .qr {{ width:1.02in; height:1.02in; display:inline-block; }}
  .cta {{ font-family:JBMono; font-weight:700; text-transform:uppercase;
          font-size:5.6pt; letter-spacing:1.5pt; color:{T["accent_text"]}; margin-top:7pt; }}
  .sub {{ font-family:JBMono; font-weight:400; font-size:4.8pt; letter-spacing:0.5pt;
          color:{T["muted"]}; margin-top:3.5pt; }}
  .backmark {{ position:absolute; left:0; right:0; bottom:0.235in;
               font-family:Inter; font-weight:400; font-size:6.5pt;
               letter-spacing:3pt; color:{T["accent_deep"]}; text-align:center; }}
</style></head>
<body>

  <section class="face front">
    <div class="safe"><div class="mid">
      <img class="logo" src="file://{logo}">
      <div class="rule"></div>
      <div class="name">{full_name}</div>
      <div class="role">{C['title']}</div>
      <div class="what">{C['tagline']}</div>
    </div></div>
    <div class="contact">
      {C['phone_display']}<span>·</span>{C['email']}<span>·</span>{C['website_display']}
    </div>
  </section>

  <section class="face back">
    <div class="safe"><div class="mid">
      <img class="qr" src="file://{OUT}/qr-print.png">
      <div class="cta">Scan to save my contact</div>
      <div class="sub">{C['card_url'].replace('https://', '').rstrip('/')}</div>
    </div></div>
    <div class="backmark">{C['company'].upper()}</div>
  </section>

</body></html>
"""

(OUT / "card.html").write_text(HTML)
print(f"wrote print/card.html + qr-print.png + qr-standalone.png")
print(f"logo used: {logo}")
