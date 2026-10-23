# divergences

Personal blog of Sigrid Keydana: deep learning (mostly R torch), weather and climate,
geometry, AI and society, books, and philosophy (sort of).

Built with [Quarto](https://quarto.org) into a plain static site (the folder `_site/`), which
any static web host can serve. Published on GitHub Pages on every `git push` (see "Publishing").

## How to add a post

Open a terminal in this folder. Then:

**1. Create the post**

```sh
make new TITLE="What wavelets told me about the Arctic"
```

This makes a folder `posts/what-wavelets-told-me-about-the-arctic/` with a file `index.qmd`
in it: today's date and the title are already filled in.
It asks whether the post is in English or French (or say it right away with `LANG=fr` / `LANG=en`).
You can give categories and tags right away, too (or fill them in later in the file):

```sh
make new TITLE="Ce que les ondelettes disent de l'Arctique" LANG=fr CATEGORIES="Climate & Weather" TAGS="wavelets, R"
```

**2. Write**

Open `index.qmd` in any editor (RStudio, VS Code, gedit, ...). The top part, between the two
`---` lines, is the post's "front matter":

```yaml
title: "What wavelets told me about the Arctic"
description: ""          # one or two sentences: shown in the post list, RSS and link previews
date: 2026-10-15
lang: en                 # en or fr: the language the post is written in
categories: [Climate & Weather, Deep Learning]   # the file lists the ones you already use
tags: [wavelets, R]      # free-form keywords
# image: picture.jpg     # optional: remove the "#" and name a picture in the post's folder
# draft: true            # optional: remove the "#" to keep the post unpublished for now
```

Below the second `---` you write the post in Markdown. Pictures go in the same folder as
`index.qmd`. A short cheat sheet is at the bottom of the new file (invisible on the site):
headings, links, footnotes, math, pictures with captions, quotes, code.

**3. Look at it**

```sh
make preview
```

Your browser opens the blog at <http://localhost:9310/>; every time you save, the page updates.
Stop it with `Ctrl+C`. (The very first time, this downloads Quarto into `.tools/`, about a minute.)

**4. Look at the whole site, then publish**

```sh
make serve
```

This builds the complete site into `_site/` and shows it at <http://localhost:9310/>, exactly as
it will be published (see "Checking before publishing" below for what to look at). Then
`git add -A`, `git commit -m "..."`, `git push`.

The post is featured on the home page, listed on the Posts page and on its category and tag
pages, in the archive, in search, and in the RSS feed. Nothing else needs updating: new
categories and tags get their own pages (and a colour) automatically.

## Two languages

* The interface (menus, dates, labels, search) is in English or French. Readers switch with
  the **EN / FR** button in the menu bar; by default it follows their browser's language.
  The words live in `assets/i18n.html` (one list per language).
* Each post is written in one language (`lang: en` or `lang: fr`); posts are never translated
  automatically. As soon as posts exist in both languages, the Posts page shows a language
  filter (All / English / Français), and lists mark posts that are not in the reader's
  interface language with a small `EN`/`FR` badge.

## Colours

Six hues, all nuances around cyan: cyan, teal-green, blue, violet, brown, amber (yellow).
Every category has one (`HUES` at the top of `tools/taxonomy.py`; a new category gets the next
free one). Light and dark values are in `assets/theme-light.scss` / `theme-dark.scss`; all text
colours pass WCAG AA (4.5:1) on the page, on cards and on their tinted backgrounds.

## Charts and figures

* **Interactive charts** (hover, zoom, filters) are Observable JS cells written straight into
  the post; they run in the reader's browser and follow light/dark mode. A complete working
  example to copy from is `examples/charts.qmd` (open <http://localhost:9310/examples/charts.html>
  while previewing). Colours and fonts come from `assets/viz.js`.
* **Figures from R or Python**: use `{r}` or `{python}` code cells. They run once on your computer
  when you render (you need R/Python installed for that post), and the result is stored in
  `_freeze/` (commit it), so later builds never need R or Python.
  `assets/theme_divergences.R` (ggplot2) and `assets/divergences-light|dark.mplstyle`
  (matplotlib) give figures the blog's look.
* **A picture you already have** (PNG, SVG, JPG): put it in the post folder and write
  `![Caption](figure.png){fig-alt="What it shows"}`.
* Code that should only be *shown*, not run, uses plain fences: ```` ```r ```` … ```` ``` ````.
  All the old posts do this.

## All commands

| command | what it does |
|---|---|
| `make new TITLE="..."` | create a new post |
| `make preview` | live preview while writing (<http://localhost:9310/>) |
| `make build` | build the site into `_site/` (also what GitHub runs to publish) |
| `make serve` | build, then show `_site/` exactly as it will be published (<http://localhost:9310/>) |
| `make check` | build, then check every internal link and image (`python3 tools/check_site.py _site --external` also tries external links) |
| `make setup` | download Quarto into `.tools/` (happens automatically when needed) |
| `make clean` | delete build output |

Needs only `make`, `python3` and `curl` (all there on Fedora). R and Python packages are
needed only for posts that run code.

## Checking before publishing

1. **While writing:** `make preview`. The browser opens <http://localhost:9310/> and reloads
   every time you save. This is the quick view; it renders only what you change.
2. **Before publishing:** stop the preview (`Ctrl+C`) and run

   ```sh
   make serve
   ```

   This builds the *whole* site exactly as it will be published and shows it at
   <http://localhost:9310/> (stop with `Ctrl+C`). Look at:
   - the **home page**: your new post is the large one at the top, with its picture and opening;
   - **the post itself**: headings, pictures, captions, footnotes (in the margin on a wide
     window), math, code;
   - its **category page** (click the coloured category name) and the **Posts** page;
   - **dark and light** (the switch in the menu bar) and **EN/FR** (also in the menu bar);
   - **a phone-sized window**: make the browser window narrow, everything should still read well.
3. Optional: `make check` builds and tests every internal link and picture; it ends with
   `all good`, or lists what is broken.

## Publishing

The site is published on GitHub Pages at <https://divergences.xyz>. On every push to `main`,
`.github/workflows/publish.yml` runs the same `make build` and puts the result online about two
minutes later; `gh run watch` (or the **Actions** tab) shows when it is live. If the build fails,
the live site stays as it was.

* A post with `{r}` or `{python}` cells: run `make build` locally first and commit `_freeze/`;
  the GitHub build has no R or Python and uses the stored results.
* `draft: true` posts are not published.
* Old Publii addresses: GitHub Pages does not read `_redirects`, so `make build`
  (`tools/redirect_pages.py`) turns each line into a small page that forwards to the new address;
  deeper old addresses are forwarded by the 404 page, and `/feed.xml` is a copy of the feed
  `index.xml`. `/feed.json` is not served. `_redirects` stays the one list to edit.

## Why Quarto

* A post is one Markdown file; listings, categories, RSS, search, footnotes, citations
  (`bibliography:`), math and code highlighting are built in.
* R and Python code can run in a post, with `freeze` so the published site never re-runs it;
  Observable JS gives interactive charts without any build step.
* The output is plain static HTML that any static host can serve.

## Where things are

```
posts/<slug>/index.qmd   one folder per post, with its pictures, data and .bib file
posts/_metadata.yml      defaults for all posts (table of contents, layout)
index.qmd, posts.qmd,
topics.qmd, archive.qmd,
about.qmd                home (latest post, recent posts, categories), all posts, topics, archive, about
categories.yml           optional one-line descriptions for category pages
_quarto.yml              site settings (title, menu, theme, site-url)
assets/                  theme (*.scss), fonts, listing templates, chart helpers, i18n.html
tools/                   make new / taxonomy pages and home feature / link check
examples/charts.qmd      chart reference page (not linked on the site)
_redirects               old Publii addresses -> new ones (Netlify format; make build also writes
                         forwarding pages from it for GitHub Pages: tools/redirect_pages.py)
.github/workflows/       publish.yml: builds and publishes on every push
```
