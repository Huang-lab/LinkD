# Keep GitHub Contributors human-only

GitHub lists anyone named in commit **`Co-authored-by:`** trailers as a repository contributor. Cursor and Claude previously appeared because agent commits added:

- `Co-authored-by: Cursor <cursoragent@cursor.com>`
- `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`

History on `main` was rewritten to remove those trailers. After `bash scripts/force_push_rewritten_main.sh`, only the human author should remain.

## Prevention

1. **Cursor:** Settings → search “co-author” / “Attribution” → disable adding Cursor as commit co-author.
2. **This repo:** enable the shared hook (once per clone):

```bash
git config core.hooksPath .githooks
```

The hook [`.githooks/prepare-commit-msg`](../.githooks/prepare-commit-msg) strips Claude/Cursor co-author lines before the commit is created.
