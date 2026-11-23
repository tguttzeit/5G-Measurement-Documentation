#!/usr/bin/env bash
# Builds the documentation site on the backend server and publishes it
# atomically.
#
# Runs as a oneshot service behind a timer (see deploy/). The source is the
# public repository: only what has been pushed there as a snapshot goes live.
# A build only happens when the documentation repository or one of the mirrored
# source repositories has changed; otherwise the run exits without work.
#
# Environment:
#   DOCS_BASE    base directory, default $HOME/5gm-docs
#   DOCS_REPO    git URL of the public documentation repository
#   DOCS_BRANCH  branch, default main
#   DOCS_KEEP    number of releases to keep, default 5
#   DOCS_SITE_URL  public URL of the site (https://<domain>/docs/); replaces the placeholder
#                  site_url of the tracked zensical.base.toml. The build appends the language
#                  (<url>/de/, <url>/en/). Set it in the untracked $DOCS_BASE/site.env.
#
# Usage: scripts/deploy.sh [--force]
set -euo pipefail

base="${DOCS_BASE:-$HOME/5gm-docs}"
repo_url="${DOCS_REPO:-https://github.com/tguttzeit/5G-Measurement-Documentation.git}"
branch="${DOCS_BRANCH:-main}"
keep="${DOCS_KEEP:-5}"

force=0
if [ "${1:-}" = "--force" ]; then
  force=1
elif [ -n "${1:-}" ]; then
  echo "unknown option: $1" >&2
  exit 2
fi

checkout="$base/repo"
releases="$base/releases"
stamp="$base/last-build"

log() { printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"; }

mkdir -p "$base" "$releases"

# One run at a time; a second one exits without an error.
exec 9>"$base/.deploy.lock"
if ! flock -n 9; then
  log "a build is already running, exiting"
  exit 0
fi

# 1. Bring the public documentation repository to the tip of the branch
if [ -d "$checkout/.git" ]; then
  git -C "$checkout" remote set-url origin "$repo_url"
  git -C "$checkout" fetch --quiet --prune origin "$branch"
else
  log "cloning the documentation repository"
  git clone --quiet --branch "$branch" "$repo_url" "$checkout"
fi
# Refuse to touch the working tree unless the target commit actually carries the
# site sources. Resetting onto an empty commit would wipe the checkout --
# including this script, which systemd starts from there.
for required in zensical.base.toml scripts/sync-sources.sh; do
  if ! git -C "$checkout" cat-file -e "origin/$branch:$required" 2>/dev/null; then
    log "origin/$branch carries no $required yet, nothing to build"
    exit 0
  fi
done

git -C "$checkout" checkout --quiet --force -B "$branch" "origin/$branch"
# Drop stale untracked files. .sources/, .venv/ and site-i18n/ are ignored and are
# kept as a cache.
git -C "$checkout" clean --quiet -fd

# 2. Update the mirrored sources
"$checkout/scripts/sync-sources.sh"

# 3. Check whether anything changed at all
fingerprint() {
  git -C "$checkout" rev-parse HEAD
  for dir in "$checkout"/.sources/*/; do
    [ -d "$dir/.git" ] || continue
    printf '%s %s\n' "$(basename "$dir")" "$(git -C "$dir" rev-parse HEAD)"
  done
}
current_fp="$(fingerprint | sha256sum | cut -d' ' -f1)"

if [ "$force" -eq 0 ] && [ -f "$stamp" ] && [ "$(cat "$stamp")" = "$current_fp" ] \
   && [ -L "$base/current" ]; then
  log "no changes since the last build"
  exit 0
fi

# The tracked zensical.base.toml carries a placeholder site_url. The real one comes from the
# environment and is read by scripts/build_i18n.py, which generates the per-language
# configs; the tracked file is never edited.
if [ -n "${DOCS_SITE_URL:-}" ]; then
  case "$DOCS_SITE_URL" in
    https://*|http://*) ;;
    *) echo "DOCS_SITE_URL must start with http:// or https://" >&2; exit 2 ;;
  esac
  export DOCS_SITE_URL
else
  log "DOCS_SITE_URL is not set, building with the placeholder site_url"
fi

# 4. Build. If this fails, the currently published release stays untouched.
log "installing dependencies"
(cd "$checkout" && uv sync --frozen --quiet)
log "building the site (one build per language)"
(cd "$checkout" && uv run python scripts/build_i18n.py --strict)

# 5. Store the release and switch over atomically. The symlink target stays
# relative to $base so that it also resolves inside the Caddy container, where
# the base directory is mounted under a different path.
stamp_name="$(date -u '+%Y%m%d-%H%M%S')"
release="$releases/$stamp_name"
rm -rf "$release"
cp -a "$checkout/site-i18n" "$release"
ln -sfn "releases/$stamp_name" "$base/.current.new"
mv -Tf "$base/.current.new" "$base/current"
printf '%s\n' "$current_fp" > "$stamp"
log "published: $release"

# 6. Prune old releases
find "$releases" -mindepth 1 -maxdepth 1 -type d | sort -r | tail -n "+$((keep + 1))" \
  | while IFS= read -r old; do
      log "removing old release: $old"
      rm -rf "$old"
    done
