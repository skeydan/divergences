#!/usr/bin/env python3
"""Check the built site: every internal link and image must point at an existing file
(and, for links with #fragments, at an existing id on that page).

    python3 tools/check_site.py _site            # internal links + images
    python3 tools/check_site.py _site --external # also try every external link (slow)
"""
import os
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        for key in ("href", "src"):
            if key in a and a[key] and not (tag == "link" and a.get("rel") in ("preconnect", "dns-prefetch")):
                self.refs.append((tag, key, a[key]))
        if "srcset" in a:
            for part in a["srcset"].split(","):
                if part.strip():
                    self.refs.append((tag, "srcset", part.strip().split()[0]))


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "_site")
    external = "--external" in sys.argv
    pages = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".html"):
                p = os.path.join(dirpath, f)
                c = Collector()
                c.feed(open(p, encoding="utf-8", errors="replace").read())
                pages[p] = c

    problems, ext_links, checked = [], set(), 0
    for page, c in pages.items():
        rel_page = os.path.relpath(page, root)
        for tag, key, ref in c.refs:
            if ref.startswith(("mailto:", "javascript:", "data:", "tel:")):
                continue
            u = urllib.parse.urlparse(ref)
            if u.scheme in ("http", "https") or ref.startswith("//"):
                if tag == "a":
                    ext_links.add(ref)
                continue
            checked += 1
            path = urllib.parse.unquote(u.path)
            if path == "":
                target = page
            elif path.startswith("/"):
                target = os.path.join(root, path.lstrip("/"))
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(page), path))
            if os.path.isdir(target):
                target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                problems.append(f"{rel_page}: missing {key}={ref}")
                continue
            frag = urllib.parse.unquote(u.fragment)
            if frag and target.endswith(".html") and target in pages and tag == "a":
                if frag not in pages[target].ids and not frag.startswith(("category=", "fn", "ref-")):
                    problems.append(f"{rel_page}: missing anchor #{frag} in {os.path.relpath(target, root)}")

    if external:
        for link in sorted(ext_links):
            try:
                req = urllib.request.Request(link, method="HEAD", headers={"User-Agent": "Mozilla/5.0 link-check"})
                urllib.request.urlopen(req, timeout=15)
            except urllib.error.HTTPError as e:
                if e.code not in (401, 403, 405, 429):  # bot walls, not dead links
                    problems.append(f"external {e.code}: {link}")
            except Exception as e:  # noqa: BLE001
                problems.append(f"external error ({type(e).__name__}): {link}")

    print(f"{len(pages)} pages, {checked} internal links/images checked, {len(ext_links)} external links"
          + (" checked" if external else " (not checked; use --external)"))
    for p in problems:
        print("  PROBLEM", p)
    if problems:
        sys.exit(1)
    print("all good")


if __name__ == "__main__":
    main()
