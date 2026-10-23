-- divergences.lua: small additions to every page.
--  * links for categories and tags (to the generated category/ and tag/ pages)
--  * reading time for posts
-- Used by assets/title-block.html.

local ACCENTS = {
  ["à"]="a",["á"]="a",["â"]="a",["ã"]="a",["ä"]="a",["å"]="a",["æ"]="ae",["ç"]="c",
  ["è"]="e",["é"]="e",["ê"]="e",["ë"]="e",["ì"]="i",["í"]="i",["î"]="i",["ï"]="i",
  ["ñ"]="n",["ò"]="o",["ó"]="o",["ô"]="o",["õ"]="o",["ö"]="o",["ø"]="o",["ù"]="u",
  ["ú"]="u",["û"]="u",["ü"]="u",["ý"]="y",["ÿ"]="y",["ß"]="ss",["ł"]="l",
  ["À"]="a",["Á"]="a",["Â"]="a",["Ã"]="a",["Ä"]="a",["Å"]="a",["Ç"]="c",["È"]="e",
  ["É"]="e",["Ê"]="e",["Ë"]="e",["Ì"]="i",["Í"]="i",["Î"]="i",["Ï"]="i",["Ñ"]="n",
  ["Ò"]="o",["Ó"]="o",["Ô"]="o",["Õ"]="o",["Ö"]="o",["Ø"]="o",["Ù"]="u",["Ú"]="u",
  ["Û"]="u",["Ü"]="u",["Ý"]="y",["Ł"]="l",
}

-- Keep in sync with slugify() in tools/frontmatter.py
local function slugify(s)
  for k, v in pairs(ACCENTS) do s = s:gsub(k, v) end
  s = s:lower():gsub("&", " and ")
  s = s:gsub("[^a-z0-9]+", "-"):gsub("^%-+", ""):gsub("%-+$", "")
  if s == "" then s = "post" end
  return s
end

local function root_prefix()
  local input = quarto and quarto.doc and quarto.doc.input_file or nil
  local proj = quarto and quarto.project and quarto.project.directory or nil
  if not input or not proj then return "" end
  local rel = input:sub(#proj + 2)
  local _, depth = rel:gsub("/", "")
  return string.rep("../", depth)
end

local function as_list(v)
  if v == nil then return {} end
  if type(v) == "table" and v.t == nil and #v > 0 then return v end
  if pandoc.utils.type(v) == "List" then return v end
  return { v }
end

local function links(meta_value, kind, prefix)
  local out = pandoc.List()
  for _, item in ipairs(as_list(meta_value)) do
    local name = pandoc.utils.stringify(item)
    if name ~= "" then
      out:insert(pandoc.MetaMap({
        name = pandoc.MetaString(name),
        slug = pandoc.MetaString(slugify(name)),
        href = pandoc.MetaString(prefix .. kind .. "/" .. slugify(name) .. ".html"),
      }))
    end
  end
  return out
end

local function count_words(blocks)
  local n = 0
  local doc = pandoc.Pandoc(blocks)
  doc:walk({
    Str = function(_) n = n + 1 end,
    Code = function(_) n = n + 1 end,
  })
  return n
end

local function has_margin_content(block)
  if not block then return false end
  local found = false
  pandoc.Pandoc({ block }):walk({
    Note = function(_) found = true end,
    Cite = function(_) found = true end,
  })
  return found
end

-- On wide screens, figures may use the space right of the text column, unless the
-- paragraph just before them has a margin note (footnote/citation) that would collide.
local function widen_figures(blocks)
  local out = pandoc.List()
  for i, b in ipairs(blocks) do
    if b.t == "Figure" and not has_margin_content(blocks[i - 1]) then
      out:insert(pandoc.Div({ b }, pandoc.Attr("", { "column-body-outset-right", "dv-wide-figure" })))
    else
      out:insert(b)
    end
  end
  return out
end

function Pandoc(doc)
  local meta = doc.meta
  if meta["post-layout"] then
    doc.blocks = widen_figures(doc.blocks)
  end
  local prefix = root_prefix()
  meta["site-root"] = pandoc.MetaString(prefix)
  if meta.categories then
    meta["category-links"] = pandoc.MetaList(links(meta.categories, "category", prefix))
  end
  if meta.tags then
    meta["tag-links"] = pandoc.MetaList(links(meta.tags, "tag", prefix))
  end
  if meta["post-layout"] then
    local words = count_words(doc.blocks)
    local minutes = math.max(1, math.floor(words / 230 + 0.5))
    meta["reading-time-text"] = pandoc.MetaString(minutes .. " min read")
    meta["reading-minutes"] = pandoc.MetaString(tostring(minutes))
    local lang = meta.lang and pandoc.utils.stringify(meta.lang) or "en"
    meta["post-lang"] = pandoc.MetaString(lang:sub(1, 2):lower())
  end
  doc.meta = meta
  return doc
end
