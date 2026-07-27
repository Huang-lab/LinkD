#!/bin/bash
# Deprecated wrapper — use scripts/prepare_zenodo.sh
echo "NOTE: prepare_figshare.sh is deprecated; calling prepare_zenodo.sh" >&2
exec "$(dirname "$0")/prepare_zenodo.sh" "$@"
