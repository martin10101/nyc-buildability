"""Reproduce the geometric findings from the official MapPLUTO response.

Coordinates are EPSG:2263, US survey feet. This is GIS analysis, not a survey.
Run from the evidence-pack root (data/mappluto.json) or this research directory.
"""
import json, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'mappluto.txt'
if not INPUT.exists(): INPUT = HERE / 'data/mappluto.json'
OUT = HERE / 'derived'
OUT.mkdir(exist_ok=True)
raw = json.loads(INPUT.read_text())
features = {int(f['attributes']['Lot']): f for f in raw['features']}
rings = {k: v['geometry']['rings'][0] for k,v in features.items()}
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def norm(a): return math.hypot(*a)
def dist_line(p,a,b): return abs(cross(sub(b,a),sub(p,a)))/norm(sub(b,a))
def area(r):
    q=[sub(v,r[0]) for v in r]
    return abs(sum(cross(a,b) for a,b in zip(q,q[1:])))/2
def overlap(a,b,c,d,tol=.001):
    if max(dist_line(c,a,b),dist_line(d,a,b))>tol: return 0.
    length=norm(sub(b,a)); u=tuple(z/length for z in sub(b,a))
    v=sorted([dot(sub(c,a),u),dot(sub(d,a),u)])
    return max(0.,min(length,v[1])-max(0.,v[0]))
def shared(r,s): return sum(overlap(a,b,c,d) for a,b in zip(r,r[1:]) for c,d in zip(s,s[1:]))
origin = rings[1][2]
north_east = rings[70][2]
u = tuple(z/norm(sub(north_east,origin)) for z in sub(north_east,origin))
v=(-u[1],u[0])
def xy(p): return dot(sub(p,origin),u), dot(sub(p,origin),v)
adj={str(l):{str(k):shared(rings[l],r) for k,r in rings.items() if k!=l and shared(rings[l],r)>.001} for l in [1,70]}
calc={
 'measurement_basis':'MapPLUTO 26v2 GIS; EPSG:2263; US survey feet; retrieved 2026-10-10',
 'not_a_survey':True,
 'areas_sqft':{str(l):area(rings[l]) for l in [1,70,11,61]},
 'edge_lengths_ft':{str(l):[norm(sub(b,a)) for a,b in zip(rings[l],rings[l][1:])] for l in [1,70,11,61]},
 'adjacent_shared_lengths_ft':adj,
 'northern_combined_frontage_ft':norm(sub(north_east,origin)),
 'maximum_distance_from_northern_line_ft':{str(l):max(dist_line(p,origin,north_east) for p in rings[l]) for l in [1,70]},
 'lot70_distance_corner_to_southwest_ft':norm(sub(rings[70][0],north_east)),
 'coordinates':{str(l):rings[l] for l in [1,70,11,61]},
}
(OUT/'geometry-calculations.json').write_text(json.dumps(calc,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,ax=plt.subplots(figsize=(11,8),dpi=180)
fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
colors={1:'#e6eef2',70:'#cce4ee',11:'#f2ede3',61:'#f2ede3'}
for lot in [1,70,11,61]:
    coords=[xy(p) for p in rings[lot]]
    ax.add_patch(Polygon(coords,closed=True,facecolor=colors[lot],edgecolor='#294a58',linewidth=1.5))
ax.text(49,-40,'LOT 1',ha='center',fontsize=19,weight='bold',color='#1d4354')
ax.text(49,-52,'215-10 Northern Boulevard',ha='center',fontsize=9)
ax.text(49,-64,'9,925 sq ft · PLUTO record',ha='center',fontsize=10)
ax.text(151,-40,'LOT 70',ha='center',fontsize=19,weight='bold',color='#1d4354')
ax.text(151,-52,'215-16 Northern Boulevard',ha='center',fontsize=9)
ax.text(151,-64,'10,075 sq ft · PLUTO record',ha='center',fontsize=10)
ax.text(50,-113,'LOT 61  ·  45-11 215 Street',ha='center',fontsize=10,weight='bold')
ax.text(152,-113,'LOT 11  ·  45-12 215 Place',ha='center',fontsize=10,weight='bold')
ax.text(101,24,'NORTHERN BOULEVARD',ha='center',fontsize=12,weight='bold',color='#536b75')
ax.text(-13,-52,'215 STREET',ha='center',va='center',rotation=90,weight='bold',color='#536b75')
ax.text(218,-52,'215 PLACE',ha='center',va='center',rotation=90,weight='bold',color='#536b75')
ax.text(49,8,'99.25 ft printed on tax map',ha='center',fontsize=9)
ax.text(151,8,'100.76 ft printed on tax map',ha='center',fontsize=9)
ax.text(101,43,'Short block frontage: 200.01 ft on tax map / 203.13 ft in GIS',ha='center',fontsize=11,color='#1d4354')
ax.annotate('',xy=(203.13,35),xytext=(0,35),arrowprops={'arrowstyle':'|-|','lw':.8,'color':'#5c7782'})
# Highlight both southern interfaces of lot 70, including the small contact with lot 61.
p0,p1,p2,p3,p4=rings[70][:-1]
for a,b in [(p3,p4),(p4,p0)]:
    a,b=xy(a),xy(b);ax.plot([a[0],b[0]],[a[1],b[1]],color='#b45f20',lw=3)
ax.text(153,-94,'101.71 ft adjoining lot 11 (GIS)',ha='center',fontsize=9,color='#8c4717')
mid=tuple((a+b)/2 for a,b in zip(xy(p0),xy(p4)))
ax.annotate('2.22 ft adjoining lot 61 (GIS)',xy=mid,xytext=(93,-146),ha='center',fontsize=10,color='#8c4717',arrowprops={'arrowstyle':'->','connectionstyle':'angle,angleA=90,angleB=0,rad=3','color':'#8c4717','lw':1})
ax.text(151,-77,'GIS depth from Northern: 99.97 ft',ha='center',fontsize=9,color='#3e6b7d')
ax.text(103,-170,'Map geometry only. Tax boundaries do not establish the legal zoning lot.',ha='center',fontsize=10,weight='bold',color='#334b56')
ax.text(103,-181,'Rotated to the Northern Boulevard frontage. No building footprint or easement is represented.',ha='center',fontsize=9,color='#536b75')
ax.text(103,-192,'Source: NYC DCP MapPLUTO 26v2 and DOF tax map effective July 29, 2021; retrieved October 10, 2026.',ha='center',fontsize=8,color='#536b75')
ax.set_xlim(-27,231);ax.set_ylim(-200,58);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('215-16 Northern Boulevard · boundary relationships',x=.12,ha='left',y=.96,fontsize=17,weight='bold',color='#193b4b')
fig.subplots_adjust(left=.06,right=.98,bottom=.03,top=.90)
fig.savefig(OUT/'site-boundary-diagram.png',bbox_inches='tight',facecolor='white')
print(json.dumps(calc,indent=2))
