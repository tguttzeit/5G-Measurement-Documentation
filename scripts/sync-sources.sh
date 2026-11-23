#!/usr/bin/env bash
# Fetches the public source repositories into .sources/ and mirrors their docs/
# into docs/<target>/ where a target is set (currently none: the repository
# documentation of both repositories lives in docs/<lang>/). The public
# repositories are the only source; the dev docs
# are generated from .sources/*/src by mkdocstrings during the build, the API
# reference from the backend's OpenAPI schema (see scripts/build_i18n.py).
#
# A repository that cannot be cloned (not published yet) is skipped with a
# warning. For local testing, an environment variable can point at a local
# checkout instead; its working tree is then copied into .sources/ as is:
#   BACKEND_SOURCE_DIR=../backend scripts/sync-sources.sh
#
# Usage: scripts/sync-sources.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sources="$root/.sources"
mkdir -p "$sources"

# directory|git url|branch|target below docs/ ("-": no docs mirroring)|local override variable
repos=(
  "5G-Measurement-Software|https://github.com/tguttzeit/5G-Measurement-Software.git|main|-|SOFTWARE_SOURCE_DIR"
  "5G-Measurement-Backend|https://github.com/tguttzeit/5G-Measurement-Backend.git|main|-|BACKEND_SOURCE_DIR"
)

for entry in "${repos[@]}"; do
  IFS='|' read -r name url branch target local_var <<< "$entry"
  dir="$sources/$name"
  local_dir="${!local_var:-}"

  if [ -n "$local_dir" ]; then
    echo "==> copying $name from $local_dir (local override, $local_var)"
    rm -rf "$dir"
    mkdir -p "$dir"
    rsync -a --delete \
      --exclude .git --exclude .venv --exclude node_modules --exclude __pycache__ \
      --exclude dist --exclude .pytest_cache --exclude .ruff_cache \
      "$local_dir/" "$dir/"
  elif [ -d "$dir/.git" ]; then
    echo "==> updating $name ($branch)"
    if ! { git -C "$dir" fetch --quiet --depth 1 origin "$branch" 2>/dev/null \
           && git -C "$dir" checkout --quiet --force "origin/$branch"; }; then
      echo "    update failed (no remote origin or not reachable), keeping the existing checkout"
    fi
  elif [ -d "$dir" ]; then
    echo "==> using the existing copy of $name in .sources/ (no git checkout, not updated)"
  else
    echo "==> cloning $name ($branch)"
    if ! git clone --quiet --depth 1 --branch "$branch" "$url" "$dir" 2>/dev/null; then
      echo "    $name is not reachable (not published yet?), skipped"
      rm -rf "$dir"
      continue
    fi
  fi

  if [ "$target" = "-" ]; then
    continue
  fi

  if [ ! -d "$dir/docs" ]; then
    echo "    no docs/ in $name, skipped"
    continue
  fi

  echo "    docs/ -> docs/$target/"
  mkdir -p "$root/docs/$target"
  # index.md is hand-written and stays; only the top-level pages are mirrored.
  find "$dir/docs" -maxdepth 1 -name '*.md' -print0 \
    | while IFS= read -r -d '' file; do
        base="$(basename "$file")"
        [ "$base" = "index.md" ] && continue
        cp "$file" "$root/docs/$target/$base"
      done
done

echo "==> done"
