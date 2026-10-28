#!/bin/sh
# Builds the standalone index.html (served by GitHub Pages) from src/index.html (the artifact source, which has no document skeleton).
cd "$(dirname "$0")"
{
  printf '%s\n' '<!doctype html>' '<html lang="zh-CN">' '<head>' '<meta charset="utf-8">' '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' '<meta name="description" content="01+ 名校背景提升：一个项目 × 多元成果。把一个真实项目做实、做深，产出论文、专利、竞赛、产品、品牌与推荐信，叩开世界名校之门。">' '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">' '<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">' '<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">' '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>' '</head>' '<body>'
  cat src/index.html
  printf '%s\n' '</body>' '</html>'
} > index.html
echo "built index.html ($(wc -c < index.html) bytes)"
