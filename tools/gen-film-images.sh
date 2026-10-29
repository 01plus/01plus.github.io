#!/bin/sh
# Generates the three milestone images with the OpenAI Images API, three requests in parallel.
# Key: $OPENAI_API_KEY, else /Users/yusun/workspace/01plus/.env (OPENAI_API_KEY=...). Model: $MODEL (default gpt-image-2).
OUT=/private/tmp/claude-501/-Users-yusun-workspace-01plus/1b2b27b7-9e00-484b-8726-8780f435dc17/scratchpad/gen
[ -z "$OPENAI_API_KEY" ] && [ -f /Users/yusun/workspace/01plus/.env ] && export $(grep '^OPENAI_API_KEY=' /Users/yusun/workspace/01plus/.env | xargs)
[ -z "$OPENAI_API_KEY" ] && { echo "no key"; exit 2; }
MODEL=${MODEL:-gpt-image-2}
STYLE="Photoreal editorial photograph, soft natural daylight, airy and clean, muted palette with purple and warm yellow accents, shallow depth of field, no text, no logos, no watermarks. The student is a 17-year-old East Asian boy with short dark hair wearing a plain purple hoodie."
gen(){ # name prompt
  printf '%s' "$2" | python3 -c 'import json,sys;print(json.dumps({"model":sys.argv[1],"prompt":sys.stdin.read(),"size":"1024x1536","quality":"high","n":1}))' "$MODEL" > "$OUT/$1.req.json"
  curl -sS https://api.openai.com/v1/images/generations -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d @"$OUT/$1.req.json" > "$OUT/$1.resp.json"
  python3 - "$OUT/$1" <<'PY'
import json,base64,sys
p=sys.argv[1]; r=json.load(open(p+".resp.json"))
if "data" not in r: print("ERROR",p,json.dumps(r)[:400]); sys.exit(1)
open(p+".png","wb").write(base64.b64decode(r["data"][0]["b64_json"])); print("ok",p+".png")
PY
}
gen contest "$STYLE He stands beside his trifold research poster at a large international high-school science and engineering fair hall, explaining a wearable ski-boot sensor prototype on the table to two adult judges wearing lanyards. Rows of poster booths and tall banners blur behind him. Bright even exhibition lighting, confident posture, one hand gesturing toward a chart on the poster. Vertical composition, subject centered." &
gen apply "$STYLE He sits at a desk by a tall window at sunrise, laptop open, one finger on the trackpad as he submits his university application, a quiet hopeful smile. Warm golden morning light floods the room, a few printed pages and a yellow folder on the desk, trees and clear sky outside. High-key, optimistic, full of hope. Vertical composition, subject centered." &
gen letter "$STYLE In a sunlit university office, a professor in his forties with glasses and a cardigan hands him a signed recommendation letter across the desk; both are smiling warmly. Bookshelves, a framed research poster and a laptop showing sensor data plots in the background. Sincere, proud, mentor-and-student moment. Vertical composition, both figures centered." &
wait
echo done
