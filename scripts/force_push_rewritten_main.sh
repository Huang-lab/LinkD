#!/usr/bin/env bash
# Force-push rewritten main (AI Co-authored-by trailers stripped).
# Requires GitHub auth (gh auth login, SSH key, or HTTPS credentials).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
echo "Local main:  $(git rev-parse main)"
echo "Origin main: $(git rev-parse origin/main 2>/dev/null || echo 'unknown')"
echo "Trailers on main (should be empty):"
git log main --grep='cursoragent@cursor.com\|noreply@anthropic.com' --oneline || true
git push --force-with-lease origin main
echo "Pushed. Check https://github.com/Huang-lab/LinkD/graphs/contributors (may take minutes to refresh)."
