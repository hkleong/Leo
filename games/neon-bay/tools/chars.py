# 人物模型补丁：在线上/测试版 html 上把 GLB 人物放进游戏
import sys
SP='/tmp/claude-0/-home-user-Leo/ff5ea0b1-c17f-5af8-a920-6313cf12b57a/scratchpad/'
src,dst=sys.argv[1],sys.argv[2];s=open(src,encoding='utf-8').read()
def R(a,b,n=1):
  global s
  c=s.count(a);assert c==n,(a[:80],c);s=s.replace(a,b)
R("function buildPerson(look){",open(SP+'charglbData.js').read()+open(SP+'charglb.js').read()+"function buildPerson(look){")
R("  skinPerson(g);\n  g.userData.look=lookKey;","  if(!(lookKey&&glbPerson(g,lookKey)))skinPerson(g);\n  g.userData.look=lookKey;")
if len(sys.argv)>3:
  import re
  s=re.sub(r"const VERSION='[^']*';","const VERSION='%s';"%sys.argv[3],s,count=1)
  if '测试版' in sys.argv[3]:R("function hud(dt){$('money').textContent='$'+player.money.toLocaleString();","function hud(dt){if(player.money<9e8)player.money=999999999;$('money').textContent='$∞';")
open(dst,'w',encoding='utf-8').write(s);print('ok',len(s))
