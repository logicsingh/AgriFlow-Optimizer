from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.parse import urlparse,parse_qs
from pathlib import Path
import json
from app import NODES,EDGES,mst_result,shortest_path,irrigation_schedule,benchmark
HTML=(Path(__file__).parent/"index.html").read_text(encoding="utf-8")
class Handler(BaseHTTPRequestHandler):
 def send(self,data,typ="application/json; charset=utf-8",status=200):
  b=data.encode() if isinstance(data,str) else json.dumps(data).encode()
  self.send_response(status);self.send_header("Content-Type",typ);self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);q=parse_qs(u.query)
  if u.path=="/":self.send(HTML,"text/html; charset=utf-8")
  elif u.path=="/api/nodes":self.send([{"id":k,**v} for k,v in NODES.items()])
  elif u.path=="/api/mst":
   a=q.get("algorithm",["Kruskal"])[0];o=q.get("objective",["length"])[0]
   if a not in ("Kruskal","Prim"):a="Kruskal"
   if o not in ("length","loss","energy","balanced"):o="length"
   self.send(mst_result(a,o))
  elif u.path=="/api/path":
   s=q.get("from",["RES"])[0];t=q.get("to",["F01"])[0];o=q.get("objective",["length"])[0]
   if s not in NODES or t not in NODES:self.send({"error":"Invalid node selection."},status=400)
   else:
    p,c,ms,n=shortest_path(s,t,o if o in ("length","loss","energy","balanced") else "length")
    self.send({"path":p,"cost":c,"time_ms":round(ms,4),"expanded":n})
  elif u.path=="/api/schedule":
   try:w=max(0,min(200,int(q.get("water",["90"])[0])))
   except ValueError:w=90
   self.send(irrigation_schedule(w))
  elif u.path=="/api/benchmark":self.send(benchmark())
  else:self.send({"error":"Not found"},status=404)
 def log_message(self,fmt,*args):print("[server]",fmt%args)
if __name__=="__main__":
 print("\\n AGRIFLOW OPTIMIZER — http://127.0.0.1:8000\\n Press Ctrl+C to stop.\\n")
 HTTPServer(("127.0.0.1",8000),Handler).serve_forever()
