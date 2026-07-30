#!/usr/bin/env bash
# Deploy the card to Netlify.
#
#   netlify login          # once — opens a browser
#   ./deploy.sh            # every time after
#
# Site name defaults to the "netlify_site" key in card.json, or override:
#   SITE_NAME=my-card ./deploy.sh
set -euo pipefail

cd "$(dirname "$0")"

DEFAULT_NAME=$(./.venv/bin/python -c \
  "import json;print(json.load(open('card.json')).get('netlify_site','my-card'))" 2>/dev/null || echo my-card)
SITE_NAME="${SITE_NAME:-$DEFAULT_NAME}"

if ! command -v netlify >/dev/null 2>&1; then
  echo "Netlify CLI not found.  npm install -g netlify-cli"
  exit 1
fi

if ! netlify status >/dev/null 2>&1; then
  echo "Not logged in. Run:  netlify login"
  exit 1
fi

# Rebuild from card.json so a deploy can never be staler than your data.
[ -f logo.png ] || ./.venv/bin/python prep_logo.py >/dev/null 2>&1 || true
./.venv/bin/python build.py

# Create the site on first run; reuse it every time after.
if [ ! -f .netlify/state.json ]; then
  echo "Creating Netlify site '$SITE_NAME'..."
  netlify sites:create --name "$SITE_NAME" --disable-linking 2>/dev/null || true
  netlify link --name "$SITE_NAME"
fi

netlify deploy --dir=dist --prod --message "card update"

cat <<'EOF'

Custom domain (one time):
  netlify domains:create card.yourdomain.com
…or add it in the Netlify UI. If your domain already uses Netlify DNS,
no external DNS changes are needed.
EOF
