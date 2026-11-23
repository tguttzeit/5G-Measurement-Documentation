# 5G Measurement Documentation

Sources of the public documentation site for the 5G measurement unit (5GMU),
served under `/docs` of the production domain. Built with
[Zensical](https://zensical.org) (the successor to Material for MkDocs), API
documentation via [mkdocstrings](https://mkdocstrings.github.io).

## What lives here and what is generated

| Path | Contents | Maintained |
|---|---|---|
| `docs/de/`, `docs/en/` | How-tos for usage, maintenance and troubleshooting, repository documentation of the measurement unit and the backend, bilingual; folders follow the nav (`de/messbox/`, `en/measurement-unit/`, `<lang>/backend/`) | here, by hand |
| `docs/index.md` | bilingual landing page | here, by hand |
| `docs/reference/` | dev docs from the docstrings | generated during the build, not checked in |
| `docs/api/` | API reference page; `openapi.json` is generated from the backend sources, Redoc (MIT) renders it | here; `openapi.json` not checked in |

The only source is the public repository
[`tguttzeit/5G-Measurement-Software`](https://github.com/tguttzeit/5G-Measurement-Software)
(branch `main`); only the dev docs are generated from it. The repository
documentation lives here. The backend repository is fetched the same way for
its API reference; until it is published, `scripts/sync-sources.sh` skips it
and the API reference stays empty.

The how-tos and the repository documentation are written in German and
English; the dev docs stay English.

## Building locally

Requires [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync                          # install Zensical and mkdocstrings-python
./scripts/sync-sources.sh        # fetch the public repositories
uv run python scripts/build_i18n.py --serve      # preview on http://127.0.0.1:8000, reloads on changes
uv run python scripts/build_i18n.py --strict     # build into site-i18n/
```

`scripts/sync-sources.sh` has to run before the first build: without
`.sources/` the dev docs and the API reference are missing. To build against a
local checkout instead of the public repository, point `SOFTWARE_SOURCE_DIR` or
`BACKEND_SOURCE_DIR` at it; its working tree is then copied into `.sources/`:

```bash
BACKEND_SOURCE_DIR=../backend ./scripts/sync-sources.sh
```

With backend sources in `.sources/`, the build generates the API reference
(`docs/api/openapi.json`) from the backend's OpenAPI schema in a separate `uv`
environment; no database is needed. If the output looks
unexpected, delete `site-i18n/`, `.stage/` and `.out/` and build again.

There is no plain `zensical serve`: the configuration is named
`zensical.base.toml` on purpose, so Zensical alone finds none. The site only
exists as one build per language with a language selector in the header.

## Deployment

The backend server builds the public repository itself on a `systemd` timer and
publishes the result through the Caddy instance that already serves the frontend
and the API. See [`deploy/README.md`](deploy/README.md) for the setup, including
the two changes needed in the backend repository. The GitHub workflow only
checks that the site builds; it does not publish anything.

## Configuration

Everything lives in `zensical.base.toml`:

- `nav` — navigation; the trees `Deutsch` and `English` map to `docs/de/` and
  `docs/en/` and must stay parallel. Each has three tabs: the start page, the
  measurement unit (`Messbox`/`Measurement unit`, whose `Development` section the build
  extends by the dev docs) and `Backend`. Zensical has no i18n plugin, so
  `scripts/build_i18n.py` generates one config per language from them
  (`zensical.de.toml`, `zensical.en.toml`, not checked in), builds each and adds
  the language selector.
- `[project.plugins.api-autonav]` — generates the dev-docs pages and their
  navigation section from `.sources/5G-Measurement-Software/src`. Zensical does
  not support `mkdocs-gen-files`.
- `[project.plugins.mkdocstrings.handlers.python]` — options for the API
  documentation. Zensical's `mkdocstrings` support is still preliminary (as of
  2026-11 there are no backlinks), which is why `backlinks` is not set.
- Emoji shortcodes cannot be combined with `attr_list` (`:flag_de:{ .lg }` is
  left as text), while Material icons (`:material-earth:{ .lg }`) work.
