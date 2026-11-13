import re,html,sys
src,dst=sys.argv[1],sys.argv[2]
t=open(src,errors="replace").read()
t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S)
t=re.sub(r"<(br|/p|/div|/li|/tr|/h\d)[^>]*>","\n",t)
t=html.unescape(re.sub(r"<[^>]+>"," ",t))
t=re.sub(r"[ \t]+"," ",t); t=re.sub(r"\n\s*\n+","\n",t)
open(dst,"w").write(t); print(dst,len(t))
