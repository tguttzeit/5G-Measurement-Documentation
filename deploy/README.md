# Deployment

The documentation site is built on the backend server itself and served as a
static directory by the Caddy instance that already serves the frontend and the
API there. There is no SSH access from GitHub and no deploy secret in GitHub:
the server pulls the current state by itself.

The source is the public repository
[`tguttzeit/5G-Measurement-Documentation`](https://github.com/tguttzeit/5G-Measurement-Documentation)
(branch `main`). Only what has been pushed there as a snapshot goes live.

## What a run does

`scripts/deploy.sh`, started by `5gm-docs.timer` every 10 minutes:

1. `flock` makes sure only one run works at a time.
2. Fetch, then check that the target commit actually carries `zensical.base.toml`
   and `scripts/sync-sources.sh`. If it does not — an empty public repository,
   for instance — the run ends here without touching the working tree.
   Resetting onto an empty commit would wipe the checkout, this script
   included, and systemd starts it from there.
3. Reset the checkout under `$DOCS_BASE/repo` to `origin/main`.
4. `scripts/sync-sources.sh` updates the source repositories in `.sources/`.
5. Build a fingerprint over the documentation commit and the commits of all
   source repositories. If it matches the last successful build, the run ends
   here. This way a rebuild also happens when only the software code (and with
   it the dev docs) changed, and does not happen when nothing changed.
6. `uv sync --frozen` and `uv run python scripts/build_i18n.py --strict`. If the build fails,
   the currently published release stays untouched.
7. Copy the result to `$DOCS_BASE/releases/<timestamp>` and switch the
   symlink `$DOCS_BASE/current` over with `mv -T`, which is atomic. Its
   target is relative (`releases/<timestamp>`) so that it also resolves inside
   the Caddy container, where the base directory is mounted elsewhere. The five
   most recent releases are kept, older ones are removed.

A build can be forced with `scripts/deploy.sh --force`, regardless of the
fingerprint.

## Server setup

The site runs as an unprivileged user out of a base directory, `$HOME/5gm-docs` by default
(`DOCS_BASE`), on the backend server. Requirements: `git`, `bash`, `flock` (util-linux) and
[`uv`](https://docs.astral.sh/uv/); only the unit installation needs root.

Nothing specific to the installation is tracked in this repository. The unit files are templates
with `@DOCS_USER@`, `@DOCS_HOME@` and `@DOCS_BASE@` placeholders that are filled in at install
time, and the public URL of the site comes from an untracked environment file,
`$DOCS_BASE/site.env`, which the unit loads and `scripts/deploy.sh` applies as `site_url`:

```bash
# uv, if it is not installed yet
curl -LsSf https://astral.sh/uv/install.sh | sh

# First checkout
DOCS_BASE="$HOME/5gm-docs"
git clone https://github.com/tguttzeit/5G-Measurement-Documentation.git "$DOCS_BASE/repo"

# Site-specific values, kept out of the repository
cat > "$DOCS_BASE/site.env" <<ENV
DOCS_SITE_URL=https://<your-domain>/docs/
ENV

# First run by hand
set -a; . "$DOCS_BASE/site.env"; set +a
"$DOCS_BASE/repo/scripts/deploy.sh"

# Install the units and enable the timer
sed -e "s|@DOCS_USER@|$USER|g" -e "s|@DOCS_HOME@|$HOME|g" -e "s|@DOCS_BASE@|$DOCS_BASE|g" \
  "$DOCS_BASE/repo/deploy/5gm-docs.service" | sudo tee /etc/systemd/system/5gm-docs.service > /dev/null
sudo cp "$DOCS_BASE/repo/deploy/5gm-docs.timer" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now 5gm-docs.timer
```

Without `DOCS_SITE_URL` the build still works but uses the placeholder `site_url`, so the
`canonical` links and `sitemap.xml` point to the wrong host.

Checking it:

```bash
systemctl list-timers 5gm-docs.timer
sudo systemctl start 5gm-docs.service   # trigger a run by hand
journalctl -u 5gm-docs.service -n 50
```

Note that `scripts/deploy.sh` runs out of the checkout it updates. When the
script itself changes, the current run still uses the previous version and the
next run picks up the new one.

## Serving the site from the backend

Caddy runs as a container in the backend repository (`docker-compose.yml`, profile `prod`).
That repository mounts the base directory, not the `current` symlink: Docker resolves a mounted
symlink once at start, so the mount would keep pointing at the old release after the next switch.
The mount source is `DOCS_DIR` in the backend's untracked `.env`; set it to this base directory.
The Caddyfile there serves the symlink with

```caddyfile
    redir /docs /docs/
    handle_path /docs/* {
        root * /srv/docs/current
        file_server
    }
```

The `redir` is needed because `/docs` without a trailing slash does not match
`/docs/*`. The generated pages link to each other relatively; only the
`canonical` links and `sitemap.xml` use `site_url`, which matches when the site
is served under `/docs/`.

After changing the backend configuration, check and reload it:

```bash
docker compose --profile prod up -d caddy
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile
curl -sI https://<your-domain>/docs/ | head -1
```

Optional, later: Caddy serves an empty 404 for unknown paths below `/docs/`. The
`404.html` that Zensical generates can be wired up through `handle_errors`; that
is not set up yet.
