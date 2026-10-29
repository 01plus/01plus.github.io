import sys, re, base64, io, os
sys.path.insert(0,"/Users/yusun/Library/Python/3.9/lib/python/site-packages")
from fontTools import subset
from fontTools.ttLib import TTFont
PAGES=["/Users/yusun/workspace/01plus/src/index.html","/Users/yusun/workspace/01plus/src/case-carvetrack.html"]
EXTRA=["/Users/yusun/workspace/01plus/src/case-template.html","/Users/yusun/workspace/01plus/cases/cases.json","/Users/yusun/workspace/01plus/build.py"]
body="".join(re.sub(r"/\*FONTS-START\*/.*?/\*FONTS-END\*/","",open(p,encoding="utf-8").read(),flags=re.S) for p in PAGES+EXTRA)
chars=set(body)|set(chr(c) for c in range(0x20,0x7f))|set("“”‘’—–·×→…（）：；，。！？、《》")
text="".join(sorted(c for c in chars if ord(c)>=0x20 and c not in "\r\n\t"))
F=os.path.expanduser("~/Library/Fonts/")
faces=[("DOUYU",400,"douyuFont.otf"),("PuHui",300,"AlibabaPuHuiTi-2-45-Light.otf"),("PuHui",700,"AlibabaPuHuiTi-2-85-Bold.otf")]
css=["/*FONTS-START*/"]; total=0
for fam,wt,fn in faces:
    f=TTFont(F+fn)
    opts=subset.Options(); opts.flavor="woff2"; opts.hinting=False; opts.desubroutinize=True; opts.layout_features=["*"]; opts.name_IDs=["*"]; opts.notdef_outline=True
    sub=subset.Subsetter(opts); sub.populate(text=text); sub.subset(f)
    buf=io.BytesIO(); f.flavor="woff2"; f.save(buf); data=buf.getvalue(); total+=len(data)
    open(f"/Users/yusun/workspace/01plus/assets/fonts/{fam.lower()}-{wt}.woff2","wb").write(data)
    css.append(f'@font-face{{font-family:"{fam}";font-weight:{wt};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format("woff2")}}')
    print(fam,wt,len(data)//1024,"KB")
css.append("/*FONTS-END*/")
for P in PAGES:
    s=open(P,encoding="utf-8").read(); s=re.sub(r"/\*FONTS-START\*/.*?/\*FONTS-END\*/","\n".join(css),s,flags=re.S); open(P,"w",encoding="utf-8").write(s)
    print("chars:",len(text),"| fonts total:",total//1024,"KB |",P.split("/")[-1],os.path.getsize(P)//1024,"KB")
