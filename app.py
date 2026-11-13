import csv, math, heapq, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NODES={}
with (ROOT/"data/nodes.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        NODES[r["id"]]={"name":r["name"],"x":float(r["x"]),"y":float(r["y"]),"elevation":float(r["elevation_m"]),"type":r["type"],"need":float(r["daily_need_m3"]),"priority":(1.5 if r["id"] in ("F02","F04","F05") else 1.0)}
EDGES=[]
with (ROOT/"data/pipelines.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        EDGES.append({"u":r["start"],"v":r["end"],"length":float(r["length_m"]),"loss":float(r["loss_pct"]),"energy":float(r["energy_kwh_day"]),"capacity":float(r["capacity_m3_day"])})
G={n:[] for n in NODES}
for e in EDGES:
    G[e["u"]].append((e["v"],e));G[e["v"]].append((e["u"],e))
def edge_cost(e,objective):
    if objective=="length":return e["length"]
    if objective=="loss":return e["length"]*e["loss"]/100
    if objective=="energy":return e["energy"]
    return e["length"]+35*e["loss"]+18*e["energy"]
def kruskal(objective="length"):
    st=time.perf_counter();parent={n:n for n in NODES};rank={n:0 for n in NODES}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    chosen=[];total=0
    for e in sorted(EDGES,key=lambda z:edge_cost(z,objective)):
        a,b=find(e["u"]),find(e["v"])
        if a!=b:
            if rank[a]<rank[b]:a,b=b,a
            parent[b]=a
            if rank[a]==rank[b]:rank[a]+=1
            chosen.append(e);total+=edge_cost(e,objective)
            if len(chosen)==len(NODES)-1:break
    return chosen,total,(time.perf_counter()-st)*1000
def prim(objective="length"):
    st=time.perf_counter();seen={"RES"};q=[]
    for v,e in G["RES"]:heapq.heappush(q,(edge_cost(e,objective),e["u"],v,e))
    chosen=[];total=0
    while q and len(seen)<len(NODES):
        cost,u,v,e=heapq.heappop(q)
        if v in seen:continue
        seen.add(v);chosen.append(e);total+=cost
        for nxt,ne in G[v]:
            if nxt not in seen:heapq.heappush(q,(edge_cost(ne,objective),v,nxt,ne))
    return chosen,total,(time.perf_counter()-st)*1000
def shortest_path(source,target,objective="length"):
    st=time.perf_counter();dist={n:float("inf") for n in NODES};dist[source]=0;prev={};q=[(0,source)];expanded=0
    while q:
        d,u=heapq.heappop(q)
        if d!=dist[u]:continue
        expanded+=1
        if u==target:break
        for v,e in G[u]:
            nd=d+edge_cost(e,objective)
            if nd<dist[v]:dist[v]=nd;prev[v]=u;heapq.heappush(q,(nd,v))
    if dist[target]==float("inf"):return [],dist[target],(time.perf_counter()-st)*1000,expanded
    path=[target]
    while path[-1]!=source:path.append(prev[path[-1]])
    path.reverse()
    return path,dist[target],(time.perf_counter()-st)*1000,expanded
def route_metrics(chosen):
    length=sum(e["length"] for e in chosen);loss=sum(e["length"]*e["loss"]/100 for e in chosen)
    energy=sum(e["energy"] for e in chosen);capacity=min((e["capacity"] for e in chosen),default=0)
    return {"length":round(length,2),"loss_index":round(loss,2),"energy":round(energy,2),"minimum_capacity":round(capacity,2)}
def mst_result(algorithm="Kruskal",objective="length"):
    chosen,total,ms=(kruskal(objective) if algorithm=="Kruskal" else prim(objective))
    return {"algorithm":algorithm,"objective":objective,"edges":[{"u":e["u"],"v":e["v"],"length":e["length"],"loss":e["loss"],"energy":e["energy"],"capacity":e["capacity"]} for e in chosen],"metrics":route_metrics(chosen),"weighted_cost":round(total,2),"time_ms":round(ms,4),"connected":len(chosen)==len(NODES)-1}
def irrigation_schedule(water_available):
    crops=[(n,d) for n,d in NODES.items() if d["type"]=="field"]
    cap=max(0,int(water_available));dp=[0]*(cap+1);take=[[False]*(cap+1) for _ in crops]
    for i,(code,d) in enumerate(crops):
        need=int(d["need"]);value=int(d["need"]*d["priority"])
        for w in range(cap,need-1,-1):
            if dp[w-need]+value>dp[w]:
                dp[w]=dp[w-need]+value;take[i][w]=True
    w=cap;selected=[]
    for i in range(len(crops)-1,-1,-1):
        if take[i][w]:
            code,d=crops[i];selected.append({"id":code,"name":d["name"],"water_m3":int(d["need"])});w-=int(d["need"])
    selected.reverse()
    return {"available_m3":cap,"allocated_m3":sum(x["water_m3"] for x in selected),"selected":selected,"total_crop_priority_score":dp[cap]}
def benchmark():
    rows=[]
    for objective in ("length","loss","energy","balanced"):
        for name,fn in (("Kruskal",kruskal),("Prim",prim)):
            es,c,ms=fn(objective);rows.append({"objective":objective,"algorithm":name,"runtime_ms":round(ms,4),"edges":len(es),"weighted_cost":round(c,2)})
    return rows
