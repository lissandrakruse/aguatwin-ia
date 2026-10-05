(function(root){
'use strict';
const R=6371,rad=Math.PI/180;
function xy(lon,lat){return [(lon+36.5)*111195*Math.cos(-7.15*rad),(lat+7.15)*111195];}
function ringLocation(ring,p){
 let inside=false;
 for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const a=ring[j],b=ring[i],dx=b[0]-a[0],dy=b[1]-a[1],cross=(p[0]-a[0])*dy-(p[1]-a[1])*dx;
  if(Math.abs(cross)<=1e-12&&p[0]>=Math.min(a[0],b[0])-1e-12&&p[0]<=Math.max(a[0],b[0])+1e-12&&p[1]>=Math.min(a[1],b[1])-1e-12&&p[1]<=Math.max(a[1],b[1])+1e-12)return 0;
  if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
 }
 return inside?1:-1;
}
function polygonCovers(rings,p){const outer=ringLocation(rings[0],p);if(outer<0)return false;if(outer===0)return true;for(let i=1;i<rings.length;i++){const hole=ringLocation(rings[i],p);if(hole===0)return true;if(hole===1)return false;}return true;}
function covers(geometry,p){if(geometry.type==='Polygon')return polygonCovers(geometry.coordinates,p);if(geometry.type==='MultiPolygon')return geometry.coordinates.some(r=>polygonCovers(r,p));return false;}
function prepare(data){
 const segments=[];
 for(const f of data.structures.features){const lines=f.geometry.type==='LineString'?[f.geometry.coordinates]:f.geometry.coordinates;for(const line of lines)for(let i=1;i<line.length;i++)segments.push([xy(...line[i-1]),xy(...line[i]),f.id]);}
 const domains=data.domains.features.map(f=>{const polys=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates,bounds=[Infinity,Infinity,-Infinity,-Infinity];for(const poly of polys)for(const ring of poly)for(const p of ring){bounds[0]=Math.min(bounds[0],p[0]);bounds[1]=Math.min(bounds[1],p[1]);bounds[2]=Math.max(bounds[2],p[0]);bounds[3]=Math.max(bounds[3],p[1]);}return {feature:f,bounds};});
 return {segments,domains,provenance:data.provenance};
}
function segmentDistance(p,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],length=dx*dx+dy*dy,t=length?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length)):0;return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy);}
function features(context,latitude,longitude){
 if(!Number.isFinite(latitude)||!Number.isFinite(longitude))throw Error('Coordenadas inválidas.');
 const hits=context.domains.filter(d=>longitude>=d.bounds[0]&&latitude>=d.bounds[1]&&longitude<=d.bounds[2]&&latitude<=d.bounds[3]&&covers(d.feature.geometry,[longitude,latitude]));
 const p=xy(longitude,latitude);let nearest=Infinity,id=null;
 for(const [a,b,sid] of context.segments){const d=segmentDistance(p,a,b);if(d<nearest){nearest=d;id=sid;}}
 const km=nearest/1000;
 return {latitude,longitude,hydrolithological_domain:hits.length?hits[0].feature.properties.u_hl_afl:'__unmapped__',domain_polygon_matches:hits.length,mapped_structure_distance_km:km,nearest_structure_id:id,log_structure_distance:Math.log1p(km)};
}
function infer(task,f){
 const input=[f.latitude,f.longitude,f.log_structure_distance,...task.category_levels.map(c=>Number(c===f.hydrolithological_domain))].map(Math.fround);
 const values=task.parameters.trees.map(t=>{let i=0;while(t.left[i]!==-1)i=input[t.feature[i]]<=t.threshold[i]?t.left[i]:t.right[i];return t.p1[i];});
 const score=values.reduce((s,v)=>s+v,0)/values.length,tree_std=Math.sqrt(values.reduce((s,v)=>s+(v-score)**2,0)/values.length);
 return {score,tree_std,label:Number(score>.5)};
}
function distance(a,b){const dlat=(b[0]-a[0])*rad,dlon=(b[1]-a[1])*rad,h=Math.sin(dlat/2)**2+Math.cos(a[0]*rad)*Math.cos(b[0]*rad)*Math.sin(dlon/2)**2;return 2*R*Math.asin(Math.sqrt(Math.min(1,h)));}
function support(task,point){let best=Infinity,id=null;for(const r of task.support_records){const d=distance(point,[r.latitude,r.longitude]);if(d<best){best=d;id=r.id;}}return {distance_km:best,id};}
function selectVisits(candidates,limit=6,separationKm=1){
 const selected=[];
 const scoreOrder=[...candidates].sort((a,b)=>b.production.score-a.production.score||a.id.localeCompare(b.id));
 const uncertaintyOrder=[...candidates].sort((a,b)=>(b.production.tree_std+b.salinity.tree_std)-(a.production.tree_std+a.salinity.tree_std)||a.id.localeCompare(b.id));
 function take(c,reason){if(selected.length<limit&&!selected.some(s=>distance([s.latitude,s.longitude],[c.latitude,c.longitude])<separationKm))selected.push({...c,visit_reason:reason});}
 if(scoreOrder.length)take(scoreOrder[0],'Maior escore de produção entre os candidatos');
 for(const c of uncertaintyOrder)take(c,'Dispersão entre árvores e separação espacial');
 return selected;
}
const api={xy,covers,prepare,features,infer,distance,support,selectVisits};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AguaTwinHydro=api;
})(typeof window!=='undefined'?window:globalThis);
