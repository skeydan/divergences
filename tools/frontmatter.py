"""Tiny helpers shared by the build scripts (no third-party packages needed)."""
import re
import unicodedata


def slugify(text):
    """'Philosophy (sort of)' -> 'philosophy-sort-of', 'Climate & Weather' -> 'climate-and-weather'.

    Keep in sync with slugify() in tools/divergences.lua.
    """
    text = str(text)
    for k, v in {"ł": "l", "Ł": "l", "ß": "ss", "æ": "ae", "ø": "o", "Ø": "o"}.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "post"


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def _inline_list(v):
    inner = v.strip()[1:-1]
    items, cur, quote = [], "", None
    for ch in inner:
        if quote:
            if ch == quote:
                quote = None
            else:
                cur += ch
        elif ch in "\"'":
            quote = ch
        elif ch == ",":
            items.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        items.append(cur.strip())
    return [i for i in items if i]


def read_front_matter(path):
    """Read the simple top-level keys of a post's YAML header.

    Handles `key: value`, `key: [a, "b c"]` (also spread over several lines) and
    block lists (`key:` followed by `- item` lines). Good enough for
    title/date/categories/tags/draft; it is not a general YAML parser.
    """
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    if not m:
        return {}
    lines = m.group(1).split("\n")
    out, i = {}, 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2)
        val = re.sub(r"\s+#.*$", "", val) if not val.startswith(("'", '"')) else val
        if val.startswith("["):
            while "]" not in val and i + 1 < len(lines):
                i += 1
                val += " " + lines[i].strip()
            out[key] = _inline_list(val[: val.rindex("]") + 1])
        elif val == "":
            items = []
            while i + 1 < len(lines) and re.match(r"^\s+-\s+", lines[i + 1]):
                i += 1
                items.append(_scalar(re.sub(r"^\s+-\s+", "", lines[i])))
            out[key] = items if items else ""
        else:
            v = _scalar(val)
            out[key] = {"true": True, "false": False}.get(v, v)
        i += 1
    return out
