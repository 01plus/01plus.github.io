# Landing-page cover illustrations (flat concept art, brand palette). Detail pages keep the documentary hero photos from gen-case-images.py.
import json, os, base64, urllib.request, concurrent.futures as cf, time
KEY=[l.split("=",1)[1].strip() for l in open("/Users/yusun/workspace/01plus/.env") if l.startswith("OPENAI_API_KEY=")][0]
OUT="/Users/yusun/workspace/01plus/assets/cases/"
STYLE=("Minimal flat vector concept illustration, clean geometric shapes with crisp edges, generous negative space, no gradients, no shadows, no outlines, no texture. "
"Strict palette: pale lavender background #ece9fb, deep indigo #1b1833, brand purple #5040bf, bright yellow #ffdf00 as a small accent, white. "
"A single clear central motif, composed like a modern tech-brand editorial spot illustration. Absolutely no text, letters, numbers, logos or watermarks. Horizontal 3:2.")
P={
"campus-platform":"Motif: a stylised school building silhouette made of simple blocks, with three floating rounded app-card rectangles connected by thin lines to a phone outline; one small yellow bell dot.",
"gunshot-alert":"Motif: a small ceiling sensor disc emitting concentric sound-wave arcs over a row of simplified lockers; one yellow alert dot at the centre of the waves.",
"clinical-trials":"Motif: a phone outline with two overlapping circles like a Venn diagram, one a patient silhouette dot, one a clipboard shape, their overlap highlighted in yellow; a small cross symbol.",
"assistive-navigation":"Motif: a white cane and a forward arrow path made of dashed segments weaving around three abstract obstacle blocks, a small camera lens circle at the top, yellow arrow tip.",
"street-medicine":"Motif: a simple pop-up tent canopy shape over a pill capsule and a hexagonal molecule diagram of connected dots, one node yellow.",
"task-platform":"Motif: a weekly grid of seven columns with a few filled blocks, a progress ring three-quarters complete in purple with a yellow remaining segment, a checkmark dot.",
"peer-support":"Motif: two speech bubbles overlapping, one with a soft heart shape inside, surrounded by a gentle circular halo; a small yellow sun-like dot.",
"gait-rehab":"Motif: a running figure made of joints and bones as dots and lines, with angle arcs at the knee and hip, a wavy stride chart line beneath; yellow highlight on one joint.",
"home-robot-arm":"Motif: a simplified articulated robotic arm of rounded segments holding a mug above a kitchen counter line, a small gear and a laptop outline; yellow accent on the gripper.",
}
def gen(slug):
    fn=f"{OUT}{slug}-cover.png"
    if os.path.exists(fn): return (slug,"skip")
    body=json.dumps({"model":"gpt-image-2","prompt":STYLE+" "+P[slug],"size":"1536x1024","quality":"high","n":1}).encode()
    err=""
    for attempt in range(3):
        try:
            req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=body,headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
            r=json.load(urllib.request.urlopen(req,timeout=600))
            open(fn,"wb").write(base64.b64decode(r["data"][0]["b64_json"])); return (slug,"ok")
        except Exception as e:
            err=str(e); time.sleep(5)
    return (slug,"ERR "+err[:120])
with cf.ThreadPoolExecutor(4) as ex:
    for res in ex.map(gen, P): print(*res, flush=True)
print("done")
