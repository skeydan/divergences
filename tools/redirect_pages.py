#!/usr/bin/env python3
"""Make the old Publii addresses in `_redirects` work on hosts that ignore that file
(GitHub Pages), by writing small files into the built site:

  * an exact old address (`/the-hard-problem-of-privacy.html`, `/tags`) gets a tiny HTML page
    there that forwards the reader at once (meta refresh + JavaScript + a plain link, and a
    canonical link so search engines move to the new address);
  * a wildcard (`/tags/books/*`) gets that page for its folder (`/tags/books/`), and the
    404 page learns the pattern, so deeper old addresses (`/tags/books/page/2/`) still forward;
  * an old feed address (`/feed.xml`) gets a copy of the new feed, because feed readers
    do not follow HTML forwarding.

`_redirects` stays the one list to edit. Real pages are never overwritten. Hosts that do read
`_redirects` (Netlify, Cloudflare) still find it in the site as before.

    python3 tools/redirect_pages.py _site      (run by `make build`)
"""
import html
import json
import os
import re
import shutil
import sys

MARKER = "<!-- old-address-forwarding (tools/redirect_pages.py) -->"

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved: divergences</title>
<link rel="canonical" href="{abs}">
<meta http-equiv="refresh" content="0; url={href}">
<script>location.replace({js} + location.hash);</script>
</head>
<body>
<p>This page has moved to <a href="{href}">{href}</a>.</p>
</body>
</html>
"""


def site_url(project):
    try:
        text = open(os.path.join(project, "_quarto.yml"), encoding="utf-8").read()
        m = re.search(r"^\s*site-url:\s*['\"]?([^'\"\s#]+)", text, re.M)
        if m:
            return m.group(1).rstrip("/")
    except OSError:
        pass
    return ""


def read_rules(path):
    rules = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            rules.append((parts[0], parts[1]))
    return rules


def main():
    site = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "_site")
    project = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    src = os.path.join(project, "_redirects")
    if not os.path.exists(src):
        print("redirect_pages: no _redirects, nothing to do")
        return
    base = site_url(project)
    written, skipped, patterns = 0, [], []

    def target_exists(to):
        p = to.split("#", 1)[0]
        f = os.path.join(site, p.lstrip("/"))
        return os.path.isfile(f) or os.path.isfile(os.path.join(f, "index.html"))

    for frm, to in read_rules(src):
        if not frm.startswith("/") or "://" in to:
            skipped.append(frm)
            continue
        if not target_exists(to):
            print(f"redirect_pages: WARNING {frm} -> {to}: the new address does not exist")
        if frm.endswith("/*"):
            patterns.append([frm[:-1], to])        # "/tags/books/" -> to
            frm = frm[:-1]                          # also a page at the folder itself
        elif "*" in frm or ":" in frm:
            skipped.append(frm)                     # other patterns: only the 404 page could
            continue
        rel = frm.lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel += "index.html"
        elif not os.path.splitext(rel)[1]:
            rel += "/index.html"                    # "/tags" -> tags/index.html
        out = os.path.join(site, rel)
        if os.path.exists(out):
            continue                                # a real page (or an earlier rule) wins
        ext = os.path.splitext(rel)[1]
        if ext == ".html":
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                f.write(STUB.format(href=html.escape(to), abs=html.escape(base + to),
                                    js=json.dumps(to)))
            written += 1
        elif ext == os.path.splitext(to)[1] and target_exists(to):
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copyfile(os.path.join(site, to.lstrip("/")), out)   # e.g. feed.xml
            written += 1
        else:
            skipped.append(frm)                     # e.g. /feed.json: no way without the host

    page404 = os.path.join(site, "404.html")
    if patterns and os.path.exists(page404):
        text = open(page404, encoding="utf-8").read()
        if MARKER not in text:
            script = (MARKER + "<script>(function(){var r=" + json.dumps(patterns) +
                      ",p=location.pathname;for(var i=0;i<r.length;i++)"
                      "if(p.indexOf(r[i][0])===0){location.replace(r[i][1]);return;}})();"
                      "</script>")
            text = text.replace("<head>", "<head>\n" + script, 1)
            with open(page404, "w", encoding="utf-8") as f:
                f.write(text)

    msg = f"redirect_pages: {written} old addresses forward to the new ones"
    if patterns:
        msg += f", {len(patterns)} patterns in 404.html"
    if skipped:
        msg += "; not possible without host redirects: " + ", ".join(skipped)
    print(msg)


if __name__ == "__main__":
    main()
