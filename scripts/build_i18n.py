#!/usr/bin/env python3
"""One Zensical build per language, merged into site-i18n/de and site-i18n/en.

The base zensical.base.toml stays the single source of truth. It is deliberately not
named zensical.toml, so a plain `zensical serve`/`zensical build` finds no config and
cannot produce a combined site without the language selector. For each language the script
stages docs/<lang>/ (plus the shared images/, javascripts/, stylesheets/ and api/ trees) as its own docs_dir,
generates a config (own nav, language, site_url, language selector) and builds it.

Usage: uv run python scripts/build_i18n.py [--strict] [--local[=PORT]] [--serve[=PORT]]
  --serve[=PORT]   build for http://127.0.0.1:PORT (default 8000), serve site-i18n/ there,
                   rebuild when docs/ or zensical.base.toml change and reload open pages
                   after each successful rebuild
Base URL (used for site_url and the language selector), first match wins:
  --serve[=PORT]   see above
  --local[=PORT]   local test site, http://127.0.0.1:PORT (default port 8001)
  DOCS_SITE_URL    production URL (set by deploy.sh / CI)
  (neither)        placeholder site_url of zensical.base.toml
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parent.parent
docs = root / "docs"
stage_root = root / ".stage"
out_root = root / ".out"
site = root / "site-i18n"

def load_base():
    """(Re)reads zensical.base.toml. main() calls it on every build, so a running --serve
    picks up nav and config changes instead of rebuilding with the state it started with."""
    global base_text, base_cfg
    base_text = (root / "zensical.base.toml").read_text(encoding="utf-8")
    base_cfg = tomllib.loads(base_text)


load_base()


def resolve_base_url():
    for arg in sys.argv[1:]:
        if arg == "--serve" or arg.startswith("--serve="):
            return f"http://127.0.0.1:{arg.partition('=')[2] or '8000'}", "serve"
        if arg == "--local" or arg.startswith("--local="):
            port = arg.partition("=")[2] or "8001"
            return f"http://127.0.0.1:{port}", "local"
    if os.environ.get("DOCS_SITE_URL"):
        return os.environ["DOCS_SITE_URL"], "DOCS_SITE_URL"
    return base_cfg["project"]["site_url"], "zensical.base.toml (placeholder)"


base_url, base_source = resolve_base_url()
if not base_url.endswith("/"):
    base_url += "/"

LANGS = {
    "de": {"nav_key": "Deutsch", "unit_key": "Messbox", "backend_key": "Backend", "dev_key": "Development", "selector": "Deutsch", "lang": "de"},
    "en": {"nav_key": "English", "unit_key": "Measurement unit", "backend_key": "Backend", "dev_key": "Development", "selector": "English", "lang": "en"},
}
PALETTE_EN = {
    "Zu hellem Design wechseln": "Switch to light mode",
    "Zu dunklem Design wechseln": "Switch to dark mode",
    "Systemeinstellung verwenden": "Switch to system preference",
}


def strip_prefix(item, prefix):
    """Turns docs/<lang>/x.md references of a nav entry into stage-relative paths."""
    if isinstance(item, str):
        return item[len(prefix):] if item.startswith(prefix) else item
    (title, value), = item.items()
    if isinstance(value, list):
        return {title: [strip_prefix(i, prefix) for i in value]}
    return {title: strip_prefix(value, prefix)}


def ser(items, indent=2):
    pad = " " * indent
    out = []
    for item in items:
        if isinstance(item, str):
            out.append(f'{pad}"{item}",')
            continue
        (title, value), = item.items()
        if isinstance(value, list):
            out.append(f'{pad}{{ "{title}" = [')
            out.extend(ser(value, indent + 2))
            out.append(f"{pad}] }},")
        else:
            out.append(f'{pad}{{ "{title}" = "{value}" }},')
    return out


def nav_for(lang, shared=True):
    """Navigation of one language build. The dev docs go into the Development section
    (dev_key) of the language's measurement-unit section (unit_key), the API reference into
    the Development section of the backend section; shared=False leaves both out,
    for the page pairing of the language selector. api-autonav fills an existing, empty
    section named after its nav_section_title instead of adding its own top-level tab."""
    spec = LANGS[lang]
    nav = base_cfg["project"]["nav"]
    own = next(i for i in nav if isinstance(i, dict) and spec["nav_key"] in i)[spec["nav_key"]]
    out = [strip_prefix(i, f"{lang}/") for i in own]
    unit = next((i for i in out if isinstance(i, dict) and spec["unit_key"] in i), None)
    assert unit is not None, f"nav of {lang} has no section {spec['unit_key']!r}"
    if shared:
        dev_docs = base_cfg["project"]["plugins"]["api-autonav"]["nav_section_title"]
        unit_dev = next((i for i in unit[spec["unit_key"]] if isinstance(i, dict) and spec["dev_key"] in i), None)
        assert unit_dev is not None, f"nav of {lang} has no section {spec['unit_key']!r} -> {spec['dev_key']!r}"
        unit_dev[spec["dev_key"]] = unit_dev[spec["dev_key"]] + [{dev_docs: []}]
        backend = next((i for i in out if isinstance(i, dict) and spec["backend_key"] in i), None)
        assert backend is not None, f"nav of {lang} has no section {spec['backend_key']!r}"
        dev = next((i for i in backend[spec["backend_key"]] if isinstance(i, dict) and spec["dev_key"] in i), None)
        assert dev is not None, f"nav of {lang} has no section {spec['backend_key']!r} -> {spec['dev_key']!r}"
        dev[spec["dev_key"]] = dev[spec["dev_key"]] + [{API_NAV_TITLE: f"{API_SERVED}/index.md"}]
    return out


def config_for(lang):
    spec = LANGS[lang]
    extra_js = ["assets/lang-map.js", "assets/repo-switch.js", "javascripts/flugplanung.js"] + (["assets/live-reload.js"] if serve_port() is not None else [])
    text = base_text
    nav_lines = ["nav = ["] + ser(nav_for(lang)) + ["]"]
    text, n = re.subn(r"^nav = \[\n.*?^\]\n", "\n".join(nav_lines) + "\n", text, count=1, flags=re.S | re.M)
    assert n == 1, "nav block not found"
    site_url = f"{base_url}{lang}/"
    text, n = re.subn(
        r'^site_url = .*$',
        f'site_url = "{site_url}"\ndocs_dir = ".stage/{lang}"\nsite_dir = ".out/{lang}"\nextra_javascript = {json.dumps(extra_js)}',
        text, count=1, flags=re.M)
    assert n == 1
    text = text.replace('language = "de"', f'language = "{spec["lang"]}"')
    if lang == "en":
        for de, en in PALETTE_EN.items():
            text = text.replace(de, en)
    alternates = "".join(
        f'\n[[project.extra.alternate]]\nname = "{LANGS[k]["selector"]}"\n'
        f'link = "{base_url}{k}/"\nlang = "{LANGS[k]["lang"]}"\n' for k in LANGS)
    return text.rstrip("\n") + "\n" + alternates


LINK = re.compile(r'(\]\(|src="|href=")((?:\.\./)+)')


def rewrite_links(path, depth):
    """Pages moved up one level: links that left docs/<lang>/ lose one '../'."""
    text = path.read_text(encoding="utf-8")

    def fix(m):
        ups = m.group(2).count("../")
        return m.group(1) + ("../" * (ups - 1) if ups >= depth + 1 else m.group(2))
    path.write_text(LINK.sub(fix, text), encoding="utf-8")


def stage(lang):
    target = stage_root / lang
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(docs / lang, target)
    for md in target.rglob("*.md"):
        rewrite_links(md, depth=len(md.relative_to(target).parts) - 1)
    # source directory below docs/ -> where it is served within each language build
    for shared, served in (("images", "images"), ("javascripts", "javascripts"), ("stylesheets", "stylesheets"), ("api", API_SERVED)):
        if (docs / shared).exists():
            shutil.copytree(docs / shared, target / served)


def flat(items):
    """Ordered list of the page paths of a nav tree."""
    out = []
    for item in items:
        if isinstance(item, str):
            out.append(item)
        else:
            (_, value), = item.items()
            out.extend(flat(value) if isinstance(value, list) else [value])
    return out


def page_dir(md):
    """messbox/nutzung/kurzanleitung.md -> messbox/nutzung/kurzanleitung, messbox/nutzung/index.md -> messbox/nutzung, index.md -> ''."""
    stem = md[:-3]
    return "" if stem == "index" else stem[:-6].rstrip("/") if stem.endswith("/index") else stem


def page_map():
    """Directory of a page in one language -> directory of its counterpart in the other."""
    pages = {k: flat(nav_for(k, shared=False)) for k in LANGS}
    assert len({len(v) for v in pages.values()}) == 1, "navs of the languages differ in structure"
    mapping = {k: {} for k in LANGS}
    for k in LANGS:
        for other in LANGS:
            if other != k:
                for a, b in zip(pages[k], pages[other]):
                    mapping[k][page_dir(a)] = page_dir(b)
    return mapping


LANG_MAP_JS = """/* generated by build_i18n.py: keeps the language selector on the counterpart page
   (instant navigation does not re-render the header) */
(function () {
  var MAP = %s;
  function update() {
    var path = location.pathname.replace(/index\\.html$/, "");
    if (!/\\/$/.test(path)) path += "/";
    var targets = MAP[path];
    if (!targets) return;
    document.querySelectorAll(".md-select__link[hreflang]").forEach(function (a) {
      var t = targets[a.getAttribute("hreflang")];
      if (t) a.setAttribute("href", t);
    });
  }
  update();
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(update);
})();
"""


LIVE_RELOAD_JS = """/* generated by build_i18n.py, --serve only: reloads the page after each successful rebuild */
(function () {
  var seen = null;
  setInterval(function () {
    fetch("/__build", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.text() : null; })
      .then(function (id) {
        if (id === null) return;
        if (seen !== null && id !== seen) location.reload();
        seen = id;
      })
      .catch(function () {});
  }, 1000);
})();
"""


def write_live_reload(lang):
    target = out_root / lang / "assets" / "live-reload.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(LIVE_RELOAD_JS, encoding="utf-8")


REPO_SWITCH_JS = """/* generated by build_i18n.py: shows the backend repository in the header on backend pages
   (Zensical knows only one repo_url; instant navigation does not re-render the header) */
(function () {
  var BACKEND = %s;
  var style = document.createElement("style");
  style.textContent = "html.repo-backend .md-source__facts { display: none; }";
  document.head.appendChild(style);
  function update() {
    var onBackend = location.pathname.indexOf(BACKEND.prefix) !== -1;
    document.documentElement.classList.toggle("repo-backend", onBackend);
    document.querySelectorAll("a.md-source").forEach(function (a) {
      var repo = a.querySelector(".md-source__repository");
      if (!repo) return;
      if (!a.dataset.defaultHref) {
        a.dataset.defaultHref = a.getAttribute("href");
        a.dataset.defaultName = repo.firstChild.textContent.trim();
      }
      a.setAttribute("href", onBackend ? BACKEND.url : a.dataset.defaultHref);
      repo.firstChild.textContent = onBackend ? BACKEND.name : a.dataset.defaultName;
    });
  }
  update();
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(update);
})();
"""


def write_repo_switch(lang):
    backend_repo = base_cfg["project"]["extra"]["backend_repo"]
    data = {"url": backend_repo["url"], "name": backend_repo["name"], "prefix": "/backend/"}
    target = out_root / lang / "assets" / "repo-switch.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(REPO_SWITCH_JS % json.dumps(data), encoding="utf-8")


def write_lang_map(lang, js_map):
    target = out_root / lang / "assets" / "lang-map.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(LANG_MAP_JS % json.dumps(js_map, indent=1), encoding="utf-8")


def localize_selector():
    """Points the language selector of every page at the counterpart page, if there is one."""
    mapping = page_map()
    exists = {k: {str(f.parent.relative_to(out_root / k)).replace(".", "") for f in (out_root / k).rglob("index.html")}
              for k in LANGS}
    for k in LANGS:
        js_map = {}
        for f in (out_root / k).rglob("index.html"):
            here = str(f.parent.relative_to(out_root / k)).replace(".", "")
            html = f.read_text(encoding="utf-8")
            targets = {}
            for other in LANGS:
                if other == k:
                    target = here
                else:
                    target = mapping[k].get(here, here)
                    if target not in exists[other]:
                        target = ""
                url = f"{base_url}{other}/" + (target + "/" if target else "")
                targets[other] = urlparse(url).path
                html = html.replace(f'href="{base_url}{other}/" hreflang="{other}"', f'href="{url}" hreflang="{other}"')
            f.write_text(html, encoding="utf-8")
            js_map[urlparse(f"{base_url}{k}/" + (here + "/" if here else "")).path] = targets
        write_lang_map(k, js_map)


API_NAV_TITLE = "API"
API_SERVED = "backend/dev/api"
BACKEND_SOURCE = root / ".sources" / "5G-Measurement-Backend"
OPENAPI_JSON = docs / "api" / "openapi.json"
OPENAPI_DUMP = "import json, sys; from app.main import app; json.dump(app.openapi(), sys.stdout, indent=1)"


def generate_openapi():
    """Writes docs/api/openapi.json from the backend sources mirrored into .sources/ (cloned
    from the public repository, or copied from a local checkout, see sync-sources.sh). The
    backend runs in its own uv environment; only its schema is needed, not a database.
    Without backend sources the file is removed, and the API page says so."""
    if not (BACKEND_SOURCE / "app" / "main.py").is_file():
        OPENAPI_JSON.unlink(missing_ok=True)
        print("==> no backend sources, API reference skipped")
        return
    newest = max(f.stat().st_mtime for f in (BACKEND_SOURCE / "app").rglob("*.py"))
    if OPENAPI_JSON.is_file() and OPENAPI_JSON.stat().st_mtime >= newest:
        return
    print("==> generating the API reference from the backend sources")
    env = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")}
    result = subprocess.run(
        ["uv", "run", "--quiet", "--frozen", "--no-dev", "--project", str(BACKEND_SOURCE), "python", "-c", OPENAPI_DUMP],
        cwd=BACKEND_SOURCE, env=env, check=True, capture_output=True, text=True)
    OPENAPI_JSON.write_text(result.stdout, encoding="utf-8")


def main():
    load_base()
    generate_openapi()
    strict = ["--strict"] if "--strict" in sys.argv else []
    print(f"==> base url: {base_url} ({base_source})")
    shutil.rmtree(out_root, ignore_errors=True)
    shutil.rmtree(site, ignore_errors=True)
    for lang in LANGS:
        stage(lang)
        cfg = root / f"zensical.{lang}.toml"
        cfg.write_text(config_for(lang), encoding="utf-8")
        print(f"==> building {lang}")
        subprocess.run(["zensical", "build", "-f", str(cfg), *strict], cwd=root, check=True)
    localize_selector()
    for lang in LANGS:
        write_repo_switch(lang)
    if serve_port() is not None:
        for lang in LANGS:
            write_live_reload(lang)
    site.mkdir()
    for lang in LANGS:
        shutil.copytree(out_root / lang, site / lang)
    (site / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>5GMU</title>'
        '<script>location.replace(navigator.language.startsWith("de") ? "de/" : "en/")</script>'
        '<p><a href="de/">Deutsch</a> · <a href="en/">English</a></p>\n', encoding="utf-8")
    print(f"==> merged into {site.name}/")


def serve_port():
    for arg in sys.argv[1:]:
        if arg == "--serve" or arg.startswith("--serve="):
            return int(arg.partition("=")[2] or "8000")
    return None


def watch_and_serve(port):
    import functools
    import http.server
    import threading
    import time

    build_id = {"value": str(time.time_ns())}

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path != "/__build":
                return super().do_GET()
            body = build_id["value"].encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", port), functools.partial(Quiet, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"==> serving {site.name}/ at http://127.0.0.1:{port}/ (Ctrl+C stops)")

    def snapshot():
        files = [root / "zensical.base.toml", *docs.rglob("*")]
        return {f: f.stat().st_mtime_ns for f in files if f.is_file()}

    last = snapshot()
    try:
        while True:
            time.sleep(1)
            now = snapshot()
            if now == last:
                continue
            print("==> change detected, rebuilding")
            try:
                main()
                build_id["value"] = str(time.time_ns())
            except (subprocess.CalledProcessError, OSError) as err:
                print(f"==> build failed: {err}")
            last = snapshot()
    except KeyboardInterrupt:
        server.shutdown()


main()
if serve_port() is not None:
    watch_and_serve(serve_port())
