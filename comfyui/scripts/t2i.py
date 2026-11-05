import json,sys,time,uuid,urllib.request,os
sys.argv_saved=sys.argv; sys.argv=['x']; sys.path.insert(0,'.')
import gen as g
prompt,out,seed,n,W,H=open(sys.argv_saved[1]).read(),sys.argv_saved[2],int(sys.argv_saved[3]),int(sys.argv_saved[4]),int(sys.argv_saved[5]),int(sys.argv_saved[6])
w={"1":{"class_type":"QwenImageTextToImageApi","inputs":{"model":"qwen-image-3.0","model.prompt":prompt,"model.negative_prompt":__import__("os").environ.get("NEG","child, teenager, school uniform, nudity, cleavage, text, watermark, multiple people"),"model.width":W,"model.height":H,"n":n,"seed":seed,"prompt_extend":False,"watermark":False}},
   "2":{"class_type":"SaveImage","inputs":{"images":["1",0],"filename_prefix":"char"}}}
jid=g.req("POST","/api/v2/jobs",{"workflow":w,"extra_data":{"api_key_comfy_org":g.KEY}},{"Idempotency-Key":str(uuid.uuid4())})["id"]; print("已提交",jid,flush=True)
while True:
    j=g.req("GET","/api/v2/jobs/"+jid)
    if j["status"] in("succeeded","failed","canceled"): break
    time.sleep(5)
if j["status"]!="succeeded": sys.exit(json.dumps(j.get("error"),ensure_ascii=False)[:1500])
for i,o in enumerate(j["outputs"]): urllib.request.urlretrieve(o["url"],f"{out}_{i}.png"); print("已下载",f"{out}_{i}.png")
