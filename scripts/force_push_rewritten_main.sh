#!/usr/bin/env bash
# Force-push rewritten main (AI Co-authored-by trailers stripped).
# Requires GitHub auth (gh auth login, SSH key, or HTTPS credentials).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
echo "Local main:  $(git rev-parse main)"
echo "Origin main: $(git rev-parse origin/main 2>/dev/null || echo 'unknown')"
echo "Trailers on main (should be empty):"
git log main --grep='cursoragent@cursor.com\|noreply@anthropic.com' --oneline || true
if ! git push --force-with-lease origin main; then
  echo ""
  echo "Push failed from this shell (auth or network)."
  echo "In GitHub Desktop:"
  echo "  1. Do NOT Pull / merge (that reintroduces AI co-author commits)."
  echo "  2. Menu → Repository → Push (enable force push if prompted:"
  echo "     Settings → Advanced → 'Allow force push' for this repo)."
  echo "  3. Or run this same script in Terminal.app after 'gh auth login'."
  exit 1
fi
echo "Pushed. In Desktop: Fetch only (do not Pull). Check https://github.com/Huang-lab/LinkD/graphs/contributors"
