import json,sys,time,uuid,urllib.request
a=sys.argv; sys.argv=['x']; sys.path.insert(0,'.')
import gen as g
img,pf,out,seed,n=a[1],a[2],a[3],int(a[4]),int(a[5])
w={"1":{"class_type":"LoadImage","inputs":{"image":g.upload(img)}},
 "2":{"class_type":"QwenImageEditApi","inputs":{"model":"qwen-image-3.0","model.images.image_1":["1",0],"model.prompt":open(pf).read(),"model.negative_prompt":__import__("os").environ.get("NEG","school uniform, blazer, tie, pleated skirt, revealing clothes, cleavage, short skirt, text, watermark"),"size":"match input","n":n,"seed":seed,"prompt_extend":False,"watermark":False}},
 "3":{"class_type":"SaveImage","inputs":{"images":["2",0],"filename_prefix":"o"}}}
jid=g.req("POST","/api/v2/jobs",{"workflow":w,"extra_data":{"api_key_comfy_org":g.KEY}},{"Idempotency-Key":str(uuid.uuid4())})["id"]; print("已提交",jid,flush=True)
while True:
    j=g.req("GET","/api/v2/jobs/"+jid)
    if j["status"] in("succeeded","failed","canceled"): break
    time.sleep(5)
if j["status"]!="succeeded": sys.exit(json.dumps(j.get("error"),ensure_ascii=False)[:1500])
for i,o in enumerate(j["outputs"]): urllib.request.urlretrieve(o["url"],f"{out}_{i}.png"); print("已下载",f"{out}_{i}.png")
