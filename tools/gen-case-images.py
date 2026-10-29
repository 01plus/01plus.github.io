import json, os, sys, base64, urllib.request, concurrent.futures as cf, time
KEY=[l.split("=",1)[1].strip() for l in open("/Users/yusun/workspace/01plus/.env") if l.startswith("OPENAI_API_KEY=")][0]
OUT="/Users/yusun/workspace/01plus/assets/cases/"
cases=json.load(open("/Users/yusun/workspace/01plus/cases/cases.json"))
STYLE="Photoreal editorial photograph, soft natural daylight, airy and clean, muted palette with purple and warm yellow accents, shallow depth of field, no text, no logos, no watermarks, no readable words anywhere. The student is a 17-year-old East Asian {g} wearing a plain purple hoodie. Horizontal 3:2 composition."
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
    g="boy" if c["gender"]=="m" else "girl"
    st=STYLE.format(g=g)
    for k,q in (("hero","high"),("s1","medium"),("s2","medium"),("s3","medium")):
        jobs.append((c["slug"],k,st+" "+c["img"][k],q))
with cf.ThreadPoolExecutor(4) as ex:
    for res in ex.map(lambda j: gen(*j), jobs): print(*res, flush=True)
print("done")
