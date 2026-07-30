#!/usr/bin/env python3
"""Build a virtual business card: one static page + a vCard + a QR code.

Edit card.json, then:  ./.venv/bin/python build.py   -> writes dist/

Everything user-specific — details, links, colours, fonts — lives in card.json.
The defaults below are a neutral slate palette; set "theme" to rebrand.
"""
import io
import json
import pathlib
import html as _html

import qrcode
import qrcode.image.svg

import theme

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
C = json.loads((ROOT / "card.json").read_text())

E = lambda s: _html.escape(str(s or ""), quote=True)
full_name = " ".join(p for p in [C["first_name"], C["last_name"]] if p)
monogram = (C["first_name"][:1] + (C["last_name"][:1] or "")).upper()

_, T = theme.load()   # palette + fonts, see theme.py


# ---------------------------------------------------------------- vCard 3.0
# 3.0 (not 4.0) because iOS Contacts and Android import it most reliably.
def vcard() -> str:
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{C['last_name']};{C['first_name']};;;",
        f"FN:{full_name}",
    ]
    if C["company"]:
        lines.append(f"ORG:{C['company']}")
    if C["title"]:
        lines.append(f"TITLE:{C['title']}")
    if C["phone"]:
        lines.append(f"TEL;TYPE=CELL,VOICE:{C['phone']}")
    if C["email"]:
        lines.append(f"EMAIL;TYPE=INTERNET,WORK:{C['email']}")
    if C["website"]:
        lines.append(f"URL:{C['website']}")
    if C["linkedin"]:
        lines.append(f"URL;TYPE=LinkedIn:{C['linkedin']}")
    if C["location"]:
        lines.append(f"ADR;TYPE=WORK:;;{C['location']};;;;")
    note = " · ".join(p for p in [C["tagline"], f"Digital card: {C['card_url']}"] if p)
    if note:
        lines.append(f"NOTE:{note}")
    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def qr_svg() -> str:
    img = qrcode.make(
        C["card_url"] or C["website"],
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=10,
        border=2,
    )
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode()
    svg = svg[svg.index("<svg"):]  # drop the xml declaration
    return svg.replace("<svg ", '<svg class="qrsvg" ', 1)


# ------------------------------------------------------------------ icons
I_PHONE = '<svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1l-2.3 2.2Z"/></svg>'
I_MSG = '<svg viewBox="0 0 24 24"><path d="M12 3c5 0 9 3.4 9 7.5S17 18 12 18c-.9 0-1.7-.1-2.5-.3L4 20l1.4-3.7C3.9 15 3 12.9 3 10.5 3 6.4 7 3 12 3Z"/></svg>'
I_MAIL = '<svg viewBox="0 0 24 24"><path d="M3 6.5C3 5.7 3.7 5 4.5 5h15c.8 0 1.5.7 1.5 1.5v11c0 .8-.7 1.5-1.5 1.5h-15C3.7 19 3 18.3 3 17.5v-11Zm2.2.5 6.8 5 6.8-5H5.2Z"/></svg>'
I_GLOBE = '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.9 9h-3a15 15 0 0 0-1.3-5.5A8 8 0 0 1 18.9 11ZM12 4.2c.8 1.2 1.6 3.5 1.8 6.8h-3.6c.2-3.3 1-5.6 1.8-6.8ZM5.1 11a8 8 0 0 1 4.3-5.5A15 15 0 0 0 8.1 11h-3Zm0 2h3a15 15 0 0 0 1.3 5.5A8 8 0 0 1 5.1 13Zm6.9 6.8c-.8-1.2-1.6-3.5-1.8-6.8h3.6c-.2 3.3-1 5.6-1.8 6.8Zm2.6-1.3a15 15 0 0 0 1.3-5.5h3a8 8 0 0 1-4.3 5.5Z"/></svg>'
I_IN = '<svg viewBox="0 0 24 24"><path d="M4.98 3.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5ZM3 9h4v12H3V9Zm6 0h3.8v1.7h.05A4.2 4.2 0 0 1 16.6 8.7c4 0 4.7 2.6 4.7 6V21h-4v-5.5c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9V21H9V9Z"/></svg>'
I_PIN = '<svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/></svg>'


def action(href, label, icon):
    return (f'      <a class="act" href="{E(href)}">\n'
            f'        <span class="ico">{icon}</span><span>{E(label)}</span>\n'
            f'      </a>')


acts = []
if C["phone"]:
    acts.append(action(f"tel:{C['phone']}", "Call", I_PHONE))
    acts.append(action(f"sms:{C['phone']}", "Text", I_MSG))
if C["email"]:
    acts.append(action(f"mailto:{C['email']}", "Email", I_MAIL))

links = []
if C["website"]:
    links.append((C["website"], I_GLOBE, "Website", C["website_display"] or C["website"], True))
if C["linkedin"]:
    links.append((C["linkedin"], I_IN, "LinkedIn", C["linkedin_display"] or "View profile", True))
if C["email"]:
    links.append((f"mailto:{C['email']}", I_MAIL, "Email", C["email"], False))
if C["phone"]:
    links.append((f"tel:{C['phone']}", I_PHONE, "Mobile", C["phone_display"] or C["phone"], False))
if C["location"]:
    links.append(("", I_PIN, "Based in", C["location"], False))

def link_row(url, icon, label, sub, external):
    tag_open = f'<a class="row" href="{E(url)}"' + (' target="_blank" rel="noopener"' if external else "") + ">"
    if not url:
        tag_open, tag_close = '<div class="row">', "</div>"
        chev = ""
    else:
        tag_close = "</a>"
        chev = '<span class="chev">&rsaquo;</span>'
    return (f"      {tag_open}\n"
            f'        <span class="ico">{icon}</span>\n'
            f'        <span class="rowtxt"><b>{E(label)}</b><em>{E(sub)}</em></span>\n'
            f"        {chev}\n      {tag_close}")

link_html = "\n".join(link_row(*l) for l in links)

avatar = (f'<img class="avatar" src="{E(C["photo"])}" alt="{E(full_name)}">'
          if C["photo"] else f'<div class="avatar mono">{E(monogram)}</div>')


def png_size(path: pathlib.Path):
    """Width/height straight out of the PNG IHDR chunk — avoids a Pillow dep."""
    b = path.read_bytes()[:33]
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")


# Drop a new logo at ~/bizcard/logo.png (or point logo_src somewhere) and it's picked
# up automatically; wide wordmarks and squarish marks get different widths.
logo_file, logo_w = C.get("logo"), 158
src = ROOT / C["logo_src"] if C.get("logo_src") else None
if src and src.exists():
    DIST.mkdir(exist_ok=True)
    (DIST / src.name).write_bytes(src.read_bytes())
    logo_file = src.name
    dims = png_size(src)
    if dims and dims[1]:
        logo_w = 158 if dims[0] / dims[1] >= 2 else 112

brandmark = (f'<img class="logo" src="{E(logo_file)}" alt="{E(C["company"])}" '
             f'style="width:{logo_w}px">'
             if logo_file else f'<div class="wordmark">{E(C["company"])}</div>')


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{{NAME}} — {{COMPANY}}</title>
<meta name="description" content="{{NAME}}, {{TITLE}} at {{COMPANY}}. Tap to save my contact.">
<meta name="theme-color" content="{{INK}}">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="{{FIRST}}">
<meta property="og:title" content="{{NAME}} — {{COMPANY}}">
<meta property="og:description" content="{{TITLE}} · Tap to save my contact">
<meta property="og:type" content="profile">
<link rel="icon" href="icon.svg">
<link rel="apple-touch-icon" href="icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={{GOOGLE_FONTS}}&display=swap" rel="stylesheet">
<style>
  :root{
    --gold:{{ACCENT}}; --gold-deep:{{ACCENT_DEEP}}; --gold-bright:{{ACCENT_BRIGHT}};
    --gold-ink:{{ACCENT_TEXT}};            /* accent dark enough to read on paper */
    --ink:{{INK}}; --paper:{{PAPER}}; --card:{{SURFACE}};
    --mut:{{MUTED}}; --line:{{LINE}};
    --sans:{{SANS}};
    --mono:{{MONO}};
  }
  @media (prefers-color-scheme:dark){
    :root{ --ink:{{DK_INK}}; --paper:{{DK_PAPER}}; --card:{{DK_SURFACE}};
           --mut:{{DK_MUTED}}; --line:{{DK_LINE}}; --gold-ink:var(--gold-bright); }
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;min-height:100%}
  body{
    font-family:var(--mono); color:var(--ink); background:var(--paper);
    background-image:
      radial-gradient(760px 420px at 50% -8%, color-mix(in srgb,var(--gold) 16%,transparent), transparent 68%),
      linear-gradient(color-mix(in srgb,var(--ink) 3%,transparent) 1px, transparent 1px),
      linear-gradient(90deg, color-mix(in srgb,var(--ink) 3%,transparent) 1px, transparent 1px);
    background-size:auto, 44px 44px, 44px 44px;
    background-attachment:fixed;
    display:flex; justify-content:center;
    padding:max(18px,env(safe-area-inset-top)) 16px calc(26px + env(safe-area-inset-bottom));
  }
  .wrap{width:100%;max-width:420px}
  .card{
    background:var(--card); border:1px solid var(--line); border-radius:10px;
    box-shadow:0 1px 2px rgba(26,26,26,.05), 0 18px 44px -22px rgba(26,26,26,.28);
    overflow:hidden;
  }

  /* ---- header band carrying the company wordmark ---- */
  .band{background:var(--ink);padding:22px 20px 44px;text-align:center;position:relative}
  .band::after{content:"";position:absolute;inset:auto 0 0;height:2px;
    background:linear-gradient(90deg,transparent,var(--gold),transparent)}
  .logo{width:158px;height:auto;display:block;margin:0 auto;opacity:.98}
  .wordmark{font-family:var(--sans);font-weight:900;font-size:26px;letter-spacing:.14em;
    color:var(--gold-bright);text-transform:uppercase}

  /* ---- identity ---- */
  /* position+z-index so the avatar sits ON the band, not under it */
  .id{padding:0 20px;text-align:center;margin-top:-38px;position:relative;z-index:1}
  .avatar{
    width:84px;height:84px;border-radius:50%;object-fit:cover;display:grid;place-items:center;
    margin:0 auto 15px;font-family:var(--sans);font-size:30px;font-weight:900;letter-spacing:.02em;
    background:var(--ink);color:var(--gold-bright);
    border:2px solid var(--gold);box-shadow:0 6px 18px -6px rgba(26,26,26,.5);
  }
  h1{font-family:var(--sans);font-weight:900;text-transform:uppercase;
    font-size:clamp(25px,7.4vw,31px);line-height:1.02;letter-spacing:-.028em;margin:0 0 10px}
  .title{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--gold-ink);
    font-weight:500;margin:0}
  .tag{font-size:12.5px;line-height:1.65;color:var(--mut);margin:13px 2px 0}
  .rule{height:1px;background:var(--line);margin:20px 0 0}

  /* ---- actions ---- */
  .body{padding:20px}
  .save{
    display:flex;align-items:center;justify-content:center;gap:9px;
    padding:15px;border-radius:999px;text-decoration:none;
    background:var(--gold);color:{{INK_ON_ACCENT}};
    font-size:11.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
    box-shadow:0 8px 20px -10px color-mix(in srgb,var(--gold) 95%,transparent);
    transition:transform .12s ease, background .12s ease;
  }
  .save:active{transform:scale(.975);background:var(--gold-bright)}
  .save svg{width:17px;height:17px;fill:currentColor}
  .acts{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:9px;margin-top:11px}
  .act{
    display:flex;flex-direction:column;align-items:center;gap:7px;padding:13px 4px;
    border-radius:8px;border:1px solid var(--line);background:var(--card);
    text-decoration:none;color:var(--ink);
    font-size:9.5px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;
    transition:transform .12s ease,border-color .12s ease,background .12s ease;
  }
  .act:active{transform:scale(.96);border-color:var(--gold);background:color-mix(in srgb,var(--gold) 8%,transparent)}
  .ico{display:grid;place-items:center}
  .ico svg{width:19px;height:19px;fill:var(--gold-deep)}

  /* ---- detail rows ---- */
  .links{margin-top:11px;border:1px solid var(--line);border-radius:8px;overflow:hidden}
  .row{display:flex;align-items:center;gap:12px;padding:13px 14px;text-decoration:none;color:var(--ink)}
  .row+.row{border-top:1px solid var(--line)}
  a.row:active{background:color-mix(in srgb,var(--gold) 9%,transparent)}
  .rowtxt{flex:1;text-align:left;display:flex;flex-direction:column;min-width:0;gap:2px}
  .rowtxt b{font-size:9.5px;font-weight:500;letter-spacing:.13em;text-transform:uppercase;color:var(--mut)}
  .rowtxt em{font-style:normal;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .chev{color:var(--gold-deep);font-size:21px;line-height:1}

  /* ---- footer ---- */
  .foot{display:flex;gap:9px;margin-top:11px}
  .ghost{
    flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:13px;
    border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);
    font-family:var(--mono);font-size:9.5px;font-weight:500;letter-spacing:.12em;
    text-transform:uppercase;cursor:pointer;transition:transform .12s ease,border-color .12s ease;
  }
  .ghost:active{transform:scale(.97);border-color:var(--gold)}
  .ghost svg{width:15px;height:15px;fill:var(--gold-deep)}
  .note{text-align:center;color:var(--mut);font-size:9.5px;letter-spacing:.1em;
    text-transform:uppercase;margin:18px 2px 2px;line-height:1.8}

  /* ---- QR ---- */
  dialog{border:none;background:transparent;padding:0;max-width:92vw}
  dialog:focus,dialog:focus-visible{outline:none}
  dialog::backdrop{background:rgba(14,14,14,.82);backdrop-filter:blur(5px)}
  .qrbox{background:#fff;padding:20px;border-radius:10px;text-align:center;
    border-top:3px solid var(--gold)}
  .qrsvg{width:min(72vw,290px);height:auto;display:block}
  .qrbox p{margin:14px 0 0;font-family:var(--mono);font-size:9.5px;letter-spacing:.13em;
    text-transform:uppercase;color:#4B5563}
  .toast{
    position:fixed;left:50%;bottom:32px;transform:translate(-50%,18px);opacity:0;
    background:{{INK}};color:{{PAPER}};padding:11px 18px;border-radius:999px;
    font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
    pointer-events:none;transition:.25s;box-shadow:0 10px 28px -8px rgba(0,0,0,.5);z-index:9
  }
  .toast.on{opacity:1;transform:translate(-50%,0)}
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<main class="wrap">
  <section class="card">
    <div class="band">{{BRANDMARK}}</div>

    <div class="id">
      {{AVATAR}}
      <h1>{{NAME}}</h1>
      <p class="title">{{TITLE}}</p>
      {{TAGLINE}}
      <div class="rule"></div>
    </div>

    <div class="body">
      <a class="save" href="contact.vcf" id="save">
        <svg viewBox="0 0 24 24"><path d="M12 3a1 1 0 0 1 1 1v8.6l2.3-2.3a1 1 0 1 1 1.4 1.4l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4l2.3 2.3V4a1 1 0 0 1 1-1ZM4 16a1 1 0 0 1 1 1v2h14v-2a1 1 0 1 1 2 0v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1Z"/></svg>
        Save to Contacts
      </a>

      <div class="acts">
{{ACTIONS}}
      </div>

      <div class="links">
{{LINKS}}
      </div>

      <div class="foot">
        <button class="ghost" id="share">
          <svg viewBox="0 0 24 24"><path d="M18 16.1a3 3 0 0 0-2 .8l-7.1-4.1a3 3 0 0 0 0-1.6L15.9 7A3 3 0 1 0 15 5c0 .3 0 .6.1.8L8 9.9a3 3 0 1 0 0 4.2l7.2 4.2c0 .2-.1.4-.1.7a3 3 0 1 0 3-3Z"/></svg>
          Share
        </button>
        <button class="ghost" id="qrbtn">
          <svg viewBox="0 0 24 24"><path d="M3 3h8v8H3V3Zm2 2v4h4V5H5Zm8-2h8v8h-8V3Zm2 2v4h4V5h-4ZM3 13h8v8H3v-8Zm2 2v4h4v-4H5Zm8-2h3v3h-3v-3Zm5 0h3v3h-3v-3Zm-5 5h3v3h-3v-3Zm5 0h3v3h-3v-3Z"/></svg>
          QR Code
        </button>
      </div>

      <p class="note">Add to home screen — opens like an app</p>
    </div>
  </section>
</main>

<dialog id="qrdlg"><div class="qrbox">{{QR}}<p>Scan to open this card</p></div></dialog>
<div class="toast" id="toast"></div>

<script>
  var toast = document.getElementById('toast');
  function say(m){ toast.textContent = m; toast.classList.add('on');
    clearTimeout(say.t); say.t = setTimeout(function(){ toast.classList.remove('on'); }, 2200); }

  document.getElementById('share').addEventListener('click', async function(){
    var data = { title: {{JS_NAME}}, text: {{JS_SHARE}}, url: location.href };
    try {
      if (navigator.share) { await navigator.share(data); }
      else { await navigator.clipboard.writeText(location.href); say('Link copied'); }
    } catch(e) { if (e && e.name !== 'AbortError') say('Could not share'); }
  });

  // The click that opens the dialog can land again on the fresh backdrop, so
  // ignore close-clicks for a beat after opening.
  var dlg = document.getElementById('qrdlg'), openedAt = 0;
  document.getElementById('qrbtn').addEventListener('click', function(){
    openedAt = Date.now(); dlg.showModal();
  });
  dlg.addEventListener('click', function(){
    if (Date.now() - openedAt > 300) dlg.close();
  });

  document.getElementById('save').addEventListener('click', function(){
    setTimeout(function(){ say('Opening contact card'); }, 350);
  });
</script>
</body>
</html>
"""

page = TEMPLATE
for token, value in {
    "{{NAME}}": E(full_name),
    "{{FIRST}}": E(C["first_name"]),
    "{{TITLE}}": E(C["title"]),
    "{{COMPANY}}": E(C["company"]),
    "{{BRANDMARK}}": brandmark,
    "{{AVATAR}}": avatar,
    "{{TAGLINE}}": f'<p class="tag">{E(C["tagline"])}</p>' if C["tagline"] else "",
    "{{ACTIONS}}": "\n".join(acts),
    "{{LINKS}}": link_html,
    "{{QR}}": qr_svg(),
    "{{JS_NAME}}": json.dumps(f"{full_name} — {C['company']}"),
    "{{JS_SHARE}}": json.dumps(f"{full_name}'s contact card"),
    "{{ACCENT}}": T["accent"],
    "{{ACCENT_DEEP}}": T["accent_deep"],
    "{{ACCENT_BRIGHT}}": T["accent_bright"],
    "{{ACCENT_TEXT}}": T["accent_text"],
    "{{INK}}": T["ink"],
    "{{PAPER}}": T["paper"],
    "{{SURFACE}}": T["surface"],
    "{{MUTED}}": T["muted"],
    "{{LINE}}": T["line"],
    "{{DK_INK}}": T["dark_ink"],
    "{{DK_PAPER}}": T["dark_paper"],
    "{{DK_SURFACE}}": T["dark_surface"],
    "{{DK_MUTED}}": T["dark_muted"],
    "{{DK_LINE}}": T["dark_line"],
    "{{SANS}}": T["font_sans"],
    "{{MONO}}": T["font_mono"],
    "{{GOOGLE_FONTS}}": T["google_fonts"],
    "{{INK_ON_ACCENT}}": T["ink_on_accent"],
}.items():
    page = page.replace(token, value)

DIST.mkdir(exist_ok=True)
(DIST / "index.html").write_text(page)
(DIST / "contact.vcf").write_text(vcard())
(DIST / "manifest.webmanifest").write_text(json.dumps({
    "name": f"{full_name} — {C['company']}",
    "short_name": C["first_name"],
    "start_url": ".",
    "display": "standalone",
    "background_color": T["paper"],
    "theme_color": T["ink"],
    "icons": [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
              {"src": "icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
}, indent=2))
(DIST / "icon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
    f'<rect width="512" height="512" rx="104" fill="{T["ink"]}"/>'
    f'<rect x="34" y="34" width="444" height="444" rx="76" fill="none" stroke="{T["accent"]}" stroke-width="10"/>'
    f'<text x="50%" y="53%" dy=".35em" text-anchor="middle" fill="{T["accent_bright"]}" '
    f'font-family="Inter,-apple-system,Helvetica,Arial" font-size="228" font-weight="900">{E(monogram)}</text></svg>'
)
# Netlify: serve .vcf with the right type so phones open Contacts instead of downloading.
(DIST / "_headers").write_text(
    "/contact.vcf\n"
    "  Content-Type: text/vcard; charset=utf-8\n"
    "  Content-Disposition: inline; filename=\"%s.vcf\"\n" % full_name.replace(" ", "-").lower()
)
print(f"built dist/ for {full_name} -> {C['card_url']}")
