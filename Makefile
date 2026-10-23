# divergences: commands
#
#   make new TITLE="My new post"     create a post (add LANG=fr for a post in French)
#   make preview                     live preview in the browser while you write
#   make serve                       the complete site, exactly as it will be published
#
# Less often:  make build (the static site into _site/)
#              make check (build + test all links/images) · make setup · make clean

QUARTO_VERSION := 1.10.19
LOCAL_QUARTO   := .tools/quarto-$(QUARTO_VERSION)/bin/quarto
# The pinned Quarto in .tools/ (downloaded on first use), so builds never depend on
# whatever version happens to be installed system-wide. Override: make build QUARTO=quarto
QUARTO         ?= $(LOCAL_QUARTO)
QUARTO_DEP     := $(if $(filter $(LOCAL_QUARTO),$(QUARTO)),$(LOCAL_QUARTO),)
PORT           ?= 9310

.PHONY: help new preview build serve check setup clean

help:
	@sed -n '2,9p' Makefile | sed 's/^# \{0,1\}//'

# LANG=fr|en on the command line (not the LANG locale variable from the environment)
POST_LANG := $(if $(filter command line,$(origin LANG)),$(LANG),)

new:
	@python3 tools/new_post.py "$(TITLE)" "$(CATEGORIES)" "$(TAGS)" "$(POST_LANG)"

preview: $(QUARTO_DEP)
	python3 tools/taxonomy.py
	$(QUARTO) preview --port $(PORT)

build: $(QUARTO_DEP)
	python3 tools/taxonomy.py   # (also runs inside quarto; first run here creates _latest.md)
	$(QUARTO) render
	python3 tools/redirect_pages.py _site   # old Publii addresses, for hosts without _redirects

serve: build
	@echo "Serving the built site at http://localhost:$(PORT)/  (Ctrl+C to stop)"
	python3 -m http.server $(PORT) --bind 127.0.0.1 --directory _site

check: build
	python3 tools/check_site.py _site

setup: $(QUARTO_DEP)
	@$(QUARTO) --version

# Downloads Quarto into .tools/ (git-ignored) the first time it is needed.
$(LOCAL_QUARTO):
	sh tools/setup.sh $(QUARTO_VERSION)

clean:
	rm -rf _site .quarto category tag
