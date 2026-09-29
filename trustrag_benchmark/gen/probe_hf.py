import requests, json
B="https://datasets-server.huggingface.co"
C=[("rajpurkar/squad","plain_text","validation"),("mandarjoshi/trivia_qa","rc.wikipedia","validation"),("mandarjoshi/trivia_qa","rc.web","validation"),
   ("mrqa-workshop/mrqa","default","validation"),("xanhho/2WikiMultihopQA",None,None),("voidful/2WikiMultihopQA",None,None),("framolfese/2WikiMultihopQA",None,None),
   ("scholarly-shadows-syndicate/2WikiMultihopQA",None,None),("akariasai/PopQA",None,None),("hotpotqa/hotpot_qa","distractor","validation")]
out={}
for ds,cfg,sp in C:
    try:
        s=requests.get(f"{B}/splits",params={"dataset":ds},timeout=60).json()
        out[ds]={"splits":s}
        if cfg is None and "splits" in s and s["splits"]:
            cfg,sp=s["splits"][0]["config"],[x for x in s["splits"] if x["split"] in("validation","dev","test")][0]["split"] if any(x["split"] in("validation","dev","test") for x in s["splits"]) else s["splits"][0]["split"]
        r=requests.get(f"{B}/rows",params={"dataset":ds,"config":cfg,"split":sp,"offset":0,"length":1},timeout=60).json()
        out[ds]["row"]=json.dumps(r)[:3000]
    except Exception as e:
        out[ds]={"err":repr(e)}
json.dump(out,open("gen/probe_out.json","w"),indent=1)
print("done")
