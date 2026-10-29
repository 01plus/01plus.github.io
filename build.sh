#!/bin/sh
# Builds the standalone pages served by GitHub Pages from the sources in src/ (which have no document skeleton).
#   src/index.html           -> index.html
#   src/case-carvetrack.html -> case/carvetrack.html   (asset links in that source are already ../assets/)
cd "$(dirname "$0")"
page(){ # src out root description
  mkdir -p "$(dirname "$2")"
  {
    printf '%s\n' '<!doctype html>' '<html lang="zh-CN">' '<head>' '<meta charset="utf-8">' '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' "<meta name=\"description\" content=\"$4\">" "<link rel=\"icon\" href=\"${3}assets/favicon.svg\" type=\"image/svg+xml\">" "<link rel=\"icon\" href=\"${3}assets/favicon-32.png\" type=\"image/png\" sizes=\"32x32\">" "<link rel=\"apple-touch-icon\" href=\"${3}assets/apple-touch-icon.png\">" '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>' '</head>' '<body>'
    cat "$1"
    printf '%s\n' '</body>' '</html>'
  } > "$2"
  echo "built $2 ($(wc -c < "$2") bytes)"
}
page src/index.html index.html "" "01+ 名校背景提升：把一个真实项目做实、做深，产出论文、专利、竞赛、产品、品牌与推荐信，叩开世界名校之门。"
page src/case-carvetrack.html case/carvetrack.html "../" "01+ 案例：CarveTrack 多模态滑雪传感器。一个滑雪少年的 30 个月，从一个真实的问题到九种成果和斯坦福的录取信。"
