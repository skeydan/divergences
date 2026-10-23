#!/usr/bin/env python3
"""Create a new post:  make new TITLE="My title" [LANG=fr|en] [CATEGORIES="Books, Deep Learning"] [TAGS="R, torch"]

Makes posts/<slug>/index.qmd with today's date and the front matter filled in.
"""
import datetime
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from frontmatter import read_front_matter, slugify  # noqa: E402


def split_list(s):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


def yaml_list(items):
    def q(x):
        return '"' + x.replace('"', '\\"') + '"' if any(ch in x for ch in ',:&()#[]{}"\'') else x
    return "[" + ", ".join(q(i) for i in items) + "]"


def short_slug(title, limit=60):
    slug = slugify(title)
    if len(slug) <= limit:
        return slug
    cut = slug[:limit]
    return cut.rsplit("-", 1)[0] if "-" in cut else cut


def main():
    title = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not title:
        print('Please give the post a title, like this:\n\n    make new TITLE="What I learned from wavelets"\n')
        sys.exit(1)
    cats = split_list(sys.argv[2] if len(sys.argv) > 2 else "")
    tags = split_list(sys.argv[3] if len(sys.argv) > 3 else "")
    lang = (sys.argv[4] if len(sys.argv) > 4 else "").strip().lower()[:2]
    if lang not in ("en", "fr"):
        if lang:
            print(f"LANG must be en or fr (got {sys.argv[4]!r}).")
            sys.exit(1)
        lang = "en"
        if sys.stdin.isatty():
            answer = input("Language of the post, en or fr? [en] ").strip().lower()[:2]
            lang = answer if answer in ("en", "fr") else "en"

    known_cats, known_tags = set(), set()
    for qmd in glob.glob(os.path.join(ROOT, "posts", "*", "index.qmd")):
        fm = read_front_matter(qmd)
        known_cats.update(fm.get("categories", []) or [])
        known_tags.update(fm.get("tags", []) or [])

    slug = short_slug(title)
    folder = os.path.join(ROOT, "posts", slug)
    if os.path.exists(folder):
        print(f"There is already a post folder posts/{slug}/ - pick another title, or edit that one.")
        sys.exit(1)
    os.makedirs(folder)

    today = datetime.date.today().isoformat()
    safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
    new_cats = [c for c in cats if c not in known_cats]
    content = f"""---
title: "{safe_title}"
description: ""   # optional: one or two sentences for the list of posts, RSS and link previews
date: {today}
lang: {lang}               # en or fr: the language this post is written in
categories: {yaml_list(cats)}
# categories you have used so far: {", ".join(sorted(known_cats))}
tags: {yaml_list(tags)}
# tags are free-form keywords; you have used: {", ".join(sorted(known_tags, key=str.lower))}
# image: picture.jpg        # optional: a picture in this folder, shown on top and in the list
# draft: true               # optional: keeps the post off the published site while you work
---

{"Commencez à écrire ici." if lang == "fr" else "Start writing here."}

<!--
Cheat sheet (this block is invisible on the site; delete it whenever you like).

*italic*  **bold**  [a link](https://example.org)  `code`

## A section heading

A footnote.[^1]

[^1]: The footnote text (shown in the margin on wide screens).

Math inline $e^{{i\\pi}} + 1 = 0$, or on its own line:
$$
\\nabla \\cdot \\mathbf{{F}} = \\partial_x F_x + \\partial_y F_y
$$

A picture in this folder, with a caption:
![The caption](picture.jpg){{fig-alt="What the picture shows, for screen readers"}}

> A quotation.

Code (shown, not run): three backticks and the language, e.g. ```r ... ```
Charts, R and Python figures: see examples/charts.qmd
(or /examples/charts.html while `make preview` is running).
-->
"""
    with open(os.path.join(folder, "index.qmd"), "w", encoding="utf-8") as f:
        f.write(content)

    rel = os.path.relpath(os.path.join(folder, "index.qmd"), ROOT)
    print(f"\nNew post: {rel}\n")
    if new_cats:
        print(f"Note: new categor{'y' if len(new_cats) == 1 else 'ies'} {', '.join(new_cats)} "
              "(that's fine; it gets its own page automatically).\n")
    print(f"Language: {'French' if lang == 'fr' else 'English'} (change `lang:` in the file if needed)\n")
    print("Next:\n  1. open that file and write (put pictures in the same folder)")
    print("  2. make preview     # look at it in the browser while you write")
    print("  3. make serve       # the whole site as it will be published\n")


if __name__ == "__main__":
    main()
