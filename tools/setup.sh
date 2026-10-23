#!/bin/sh
# Download Quarto into .tools/ (no sudo, nothing installed system-wide).
set -e
cd "$(dirname "$0")/.."
VERSION="${1:-1.10.19}"
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)  ASSET="quarto-$VERSION-linux-amd64.tar.gz" ;;
  Linux-aarch64) ASSET="quarto-$VERSION-linux-arm64.tar.gz" ;;
  Darwin-*)      ASSET="quarto-$VERSION-macos.tar.gz" ;;
  *) echo "Please install Quarto from https://quarto.org/docs/get-started/" >&2; exit 1 ;;
esac
mkdir -p .tools
echo "Downloading Quarto $VERSION (one time, ~130 MB) ..."
curl -fsSL -o .tools/quarto.tar.gz "https://github.com/quarto-dev/quarto-cli/releases/download/v$VERSION/$ASSET"
mkdir -p ".tools/quarto-$VERSION"
case "$ASSET" in
  *macos*) tar xzf .tools/quarto.tar.gz -C ".tools/quarto-$VERSION" ;;
  *)       tar xzf .tools/quarto.tar.gz -C .tools ;;
esac
rm .tools/quarto.tar.gz
echo "ok: Quarto $VERSION is in .tools/"
