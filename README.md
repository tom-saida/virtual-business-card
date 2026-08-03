# Virtual business card

A digital business card that works on iPhone and Android with **no app, no App Store, no monthly fee**.

You get one link. Someone opens it, taps **Save to Contacts**, and you're in their phone — name,
number, email, company, the lot. It's a plain static page, so it costs nothing to host and there's
no account, no login, and no service that can shut it down or start charging you.

It also generates a **print-ready PDF** of a physical card with the QR code on the back, which is
what you actually hand people at a conference.

The paid versions of this (Popl, Blinq, HiHello, V1CE) run $30+ per card and often a subscription
on top. This is the same thing, built from a JSON file.

---

## What you get

| | |
|---|---|
| **Web card** | One responsive page. Light and dark mode. Add-to-home-screen so it opens like an app. |
| **Save to Contacts** | A real vCard (`.vcf`) — the phone's own contact importer, not a form to retype. |
| **Tap actions** | Call, text, email, plus rows for website / LinkedIn / location. |
| **QR code** | Built into the page (show it off your screen) *and* rendered onto the printable card. |
| **Share button** | Uses the native share sheet, falls back to copy-link. |
| **Lead capture** | Optional "Send me your info" form. Free via Netlify Forms, emails you each submission. |
| **Analytics** | Optional. Drop in a Cloudflare Web Analytics token (free) or any other provider's script. |
| **Print PDF** | Front + back, 3.5×2in trim with proper bleed, fonts embedded. Send it straight to a printer. |
| **NFC-ready** | Write the card URL to a cheap NFC tag and tap phones together. |

Everything is generated from one file: `card.json`.

---

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git card
cd card

python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

cp card.example.json card.json   # then edit card.json with your details
./.venv/bin/python build.py
```

That writes `dist/`. Preview it locally:

```bash
python3 -m http.server 8077 --directory dist
```

Open <http://localhost:8077>. To test on your actual phone, use your computer's LAN address
(`http://192.168.x.x:8077`) with both devices on the same Wi-Fi — `localhost` won't work from a
phone, because it means "this phone".

---

## Configuration

Every field lives in `card.json`. Leave any of them empty and that row simply disappears.

```jsonc
{
  "first_name": "Jordan",
  "last_name": "Reyes",
  "title": "Founder | CEO",
  "company": "Northwind",
  "tagline": "Logistics software for mid-market shippers",

  "phone": "+15551234567",            // E.164 — this is what tel:/sms: dial
  "phone_display": "(555) 123-4567",  // what humans read
  "email": "jordan@example.com",
  "website": "https://example.com",
  "website_display": "example.com",
  "linkedin": "https://www.linkedin.com/in/example",
  "linkedin_display": "jordan-reyes",
  "location": "Philadelphia, PA",

  "photo": "",             // path to a headshot, or leave empty for an initials monogram
  "logo_src": "logo.png",  // optional company logo, shown in the header band
  "card_url": "https://card.example.com/"   // IMPORTANT: what the QR code encodes
}
```

**`card_url` matters more than it looks.** It's the URL baked into the QR code and into the vCard
note. Set it to the real address *before* you print anything.

### Theming

Add a `theme` block to `card.json`. Any key you omit falls back to the default slate palette.

```jsonc
"theme": {
  "accent": "#4F7CFF",        // buttons, icons, accents
  "accent_deep": "#3D63D8",   // icon fill on light backgrounds
  "accent_bright": "#7CA0FF", // accent on dark backgrounds
  "accent_text": "#2F4FA8",   // accent dark enough to read as text on paper
  "ink": "#1A1A1A",           // header band + primary text
  "ink_on_accent": "#FFFFFF", // text on the filled button — check contrast!
  "paper": "#FAFAFA"
}
```

Fonts are configurable too — `font_sans`, `font_mono`, and `google_fonts` (the Google Fonts query
string). Defaults are Inter + JetBrains Mono.

### Logo with a white background

If your logo is a JPEG or PNG on white, it'll show as a white box on the dark header band.
`prep_logo.py` fixes that — it trims the padding and knocks the white out to transparency,
preserving the anti-aliased edges instead of leaving a halo:

```bash
./.venv/bin/python prep_logo.py path/to/your-logo.jpg   # writes logo.png
```

---

## Lead capture and analytics

Both are optional, both are free, and both are off until you turn them on. Together they close
most of the gap with the paid card services.

### Lead capture

Set `"exchange_form": true` in `card.json`. That adds a **Send me your info** button that opens a
form (name, email, phone, company, note). On Netlify it works with no backend at all — Netlify
scans the deployed HTML, finds the form, and captures submissions. The free tier covers 100
submissions a month.

To get an email for every submission, add a notification hook once:

```bash
SITE_ID=$(python3 -c "import json;print(json.load(open('.netlify/state.json'))['siteId'])")
netlify api createHookBySiteId --data "{\"site_id\":\"$SITE_ID\",\"body\":{\"type\":\"email\",\"event\":\"submission_created\",\"data\":{\"email\":\"you@example.com\"}}}"
```

The form submits over `fetch`, so the visitor stays on your card and sees a confirmation instead
of being bounced to a success page. If you host somewhere other than Netlify, the button still
appears but submissions won't be captured — either point the form at your own endpoint or set
`exchange_form` to `false`.

### Analytics

Cloudflare Web Analytics is free, needs no cookie banner, and doesn't track people across sites.

1. Sign in at <https://dash.cloudflare.com> → **Web Analytics** → **Add a site**.
2. Enter your card's hostname. Cloudflare hands you a beacon token.
3. Put it in `card.json` and rebuild:

```jsonc
"analytics": { "cloudflare_token": "your-token-here" }
```

Prefer something else? `"custom_script"` takes a raw `<script>` tag, so Plausible, Umami,
GoatCounter, or Fathom all drop straight in.

---

## Hosting

It's static files. Anything that serves a folder works, and the free tiers are more than enough.

**Netlify** — drag `dist/` onto <https://app.netlify.com/drop>, or use the CLI:

```bash
netlify login
netlify deploy --dir=dist --prod
```

**GitHub Pages** — push `dist/` to a `gh-pages` branch, or point Pages at `/docs`.

**Cloudflare Pages / Vercel / S3** — same story, upload the folder.

### One hosting gotcha: the vCard MIME type

If `contact.vcf` is served as `text/plain` or `application/octet-stream`, phones download it as a
file instead of opening the contact card. The build writes a Netlify `_headers` file that sets
`text/vcard` for you. On other hosts, set that MIME type yourself:

```
/contact.vcf   Content-Type: text/vcard; charset=utf-8
```

### Custom domain

**You do not need to buy a domain.** Every host above gives you a free one —
`yourname.netlify.app`, `yourname.github.io`, `yourname.pages.dev`. That URL works forever, costs
nothing, and does everything a paid domain does. Put it on an NFC tag and nobody ever sees it.

A custom subdomain like `card.yourdomain.com` is purely cosmetic — it matters when the URL is
*printed* on a card and someone reads it. If you already own a domain it's usually free to add:
create a CNAME pointing at your host. If your domain's DNS is managed by that same host, there's
often nothing to configure at all.

**Heads up on new DNS records.** If anything looked up your subdomain *before* it existed, public
resolvers cache the "doesn't exist" answer for as long as your zone's negative-cache TTL (often an
hour). The site is live; the world just hasn't been told yet. Test with `dig @8.8.8.8 yourhost` and
wait it out rather than assuming you misconfigured something.

---

## Printing physical cards

```bash
./.venv/bin/python fetch_fonts.py   # once — grabs TTFs for PDF embedding
./.venv/bin/python print_card.py
weasyprint print/card.html print/business-card-PRINT.pdf
```

Requires [WeasyPrint](https://weasyprint.org/). On macOS you may need
`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` in front of the command.

Output is 2 pages — front and back — at 3.75×2.25in, which is a 3.5×2in card plus 0.125in bleed on
every edge. Important text sits inside a further 0.125in safety margin. Hand that PDF to any print
shop.

You also get `print/qr-standalone.png` — a high-resolution QR for slides, a conference badge, an
email signature, or a phone lock screen.

> **Scan the QR with your own phone before ordering 500 cards.** If `card_url` is wrong or the site
> isn't live yet, you've just printed 500 dead links.

---

## NFC tags

Tap a phone against a tag and the card opens. No app on their end.

1. Buy **NTAG213 or NTAG215** stickers or blank PVC cards (roughly $10–15 for 10–25).
2. Install **NFC Tools** (free, iOS and Android).
3. Write → Add a record → **URL** → your `card_url` → Write.
4. Optionally lock the tag read-only so nobody can overwrite it. This is permanent — test first.

iPhone XS and newer read tags in the background: a banner appears, they tap it, the card opens.
Older iPhones need the NFC reader in Control Center. Most Androids with NFC just work.

A tag stuck to the back of your phone case means you always have your card on you.

---

## Your data stays yours

`card.json`, `logo.png`, `assets/`, `dist/`, and `print/` are all in `.gitignore`. Your phone
number and email live in a file git never sees, so forking or contributing to this repo can't
leak them.

There's also a guard you can run before pushing:

```bash
./.venv/bin/python scrub_check.py
```

It reads your local `card.json`, then greps every git-tracked file for your phone (in any format),
email, and LinkedIn, and exits non-zero if it finds one.

---

## How it works

No framework, no build pipeline, no JavaScript dependencies.

```
card.json        your details + theme — the only file you edit
build.py         renders dist/: index.html, contact.vcf, manifest, icon, _headers
prep_logo.py     white-background logo -> trimmed transparent PNG
print_card.py    renders print/card.html + QR PNGs for the PDF
fetch_fonts.py   downloads TTFs (print only)
scrub_check.py   pre-push privacy guard
```

The page is a single self-contained HTML file with inline CSS and about 20 lines of JavaScript
(share button, QR dialog). The vCard is **version 3.0** rather than 4.0 — 3.0 is what iOS Contacts
and Android import most reliably.

---

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, sell cards with it.
