import json, os, sys, base64, urllib.request, concurrent.futures as cf, time
KEY=[l.split("=",1)[1].strip() for l in open("/Users/yusun/workspace/01plus/.env") if l.startswith("OPENAI_API_KEY=")][0]
OUT="/Users/yusun/workspace/01plus/assets/cases/"
cases=json.load(open("/Users/yusun/workspace/01plus/cases/cases.json"))
STYLE="Photoreal product and documentary photograph, soft natural daylight, airy and clean, muted palette with subtle purple and warm yellow accents, shallow depth of field. Screens show plausible modern app interfaces built from shapes, icons and charts only. No posed hero subject; any people are incidental, partially out of frame or seen from behind. No text, no logos, no watermarks, no readable words anywhere. Horizontal 3:2 composition."
HERO_STYLE="Candid documentary photograph shot on 35mm film, available light only, visible fine grain, slightly imperfect framing, real-world clutter and wear, unstaged, mixed colour temperatures. Any people are incidental, cropped by the frame or seen from behind. Screens show plausible modern app interfaces made only of shapes, icons and charts. No text, no logos, no watermarks, no readable words anywhere. Horizontal 3:2 composition."
# Covers (hero) use the candid 35mm documentary style; scene images keep the clean product style.
def gen(slug,key,prompt,quality):
    fn=f"{OUT}{slug}-{key}.png"
    if os.path.exists(fn): return (slug,key,"skip")
    body=json.dumps({"model":"gpt-image-2","prompt":prompt,"size":"1536x1024","quality":quality,"n":1}).encode()
    for attempt in range(3):
        try:
            req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=body,headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
            r=json.load(urllib.request.urlopen(req,timeout=600))
            open(fn,"wb").write(base64.b64decode(r["data"][0]["b64_json"])); return (slug,key,"ok")
        except Exception as e:
            err=str(e); time.sleep(5)
    return (slug,key,"ERR "+err[:120])
jobs=[]
for c in cases:
    st=STYLE
    for k,q in (("hero","high"),("s1","medium"),("s2","medium"),("s3","medium")):
        jobs.append((c["slug"],k,(HERO_STYLE if k=="hero" else st)+" "+c["img"][k],q))
with cf.ThreadPoolExecutor(4) as ex:
    for res in ex.map(lambda j: gen(*j), jobs): print(*res, flush=True)
print("done")
