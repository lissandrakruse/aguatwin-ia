(function(){'use strict';
const $=id=>document.getElementById(id),H=window.AguaTwinHydro;let loaded=null,last=null,revision=0;
const fmt=(n,d=2)=>n.toLocaleString('pt-BR',{maximumFractionDigits:d,minimumFractionDigits:d}),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){if(!loaded){loaded=Promise.all(['hydro_context.json','hydro_models.json','hydro_validation.json'].map(async url=>{const r=await fetch(url);if(!r.ok)throw Error('Não foi possível carregar '+url);return r.json();})).then(([context,models,report])=>({context:H.prepare(context),models,report})).catch(e=>{loaded=null;throw e;});}return loaded;}
function invalidate(){revision++;last=null;$('hExport').disabled=true;$('hStatus').textContent='Local ou seleção alterado. Prepare novamente o plano para essas coordenadas.';$('hCandidates').innerHTML='<tbody><tr><td>Plano anterior desatualizado.</td></tr></tbody>';}
async function plan(){
 const rev=revision;$('hPlan').disabled=true;last=null;$('hExport').disabled=true;$('hStatus').textContent='Carregando geologia e preparando hipóteses…';
 try{
  await window.AguaTwinAI.ready;const lat=$('aiLat').valueAsNumber,lon=$('aiLon').valueAsNumber,radius=$('aiRadius').valueAsNumber;
  if(![lat,lon,radius].every(Number.isFinite)||radius<.5||radius>10)throw Error('Informe coordenadas e raio de 0,5 a 10 km.');
  if(!window.AguaTwinAI.insideBoundary([lat,lon]))throw Error('O centro precisa estar dentro da Paraíba.');
  const {context,models,report}=await load();if(rev!==revision)throw Error('As entradas mudaram durante o carregamento. Prepare o plano novamente.');
  const rows=[];let tested=0;
  for(let y=-3;y<=3;y++)for(let x=-3;x<=3;x++){
   if((x===0&&y===0)||Math.hypot(x,y)>3)continue;tested++;
   const latitude=lat+y*radius/3/111.195,longitude=lon+x*radius/3/(111.195*Math.cos(lat*Math.PI/180)),point=[latitude,longitude];
   if(!window.AguaTwinAI.insideBoundary(point))continue;
   const prod=H.support(models.tasks.potential,point),sal=H.support(models.tasks.salinity,point);
   if(prod.distance_km<.15||prod.distance_km>5||sal.distance_km>5)continue;
   if(Object.values(models.tasks).some(t=>point.some((v,i)=>v<t.bounds.min[i]||v>t.bounds.max[i])))continue;
   const f=H.features(context,latitude,longitude);if(f.domain_polygon_matches!==1)continue;
   rows.push({...f,id:`p${tested}`,nearest_production_km:prod.distance_km,nearest_salinity_km:sal.distance_km,production:H.infer(models.tasks.potential,f),salinity:H.infer(models.tasks.salinity,f)});
  }
  const visits=H.selectVisits(rows);last={version:'2.1',created_at:new Date().toISOString(),center:{latitude:lat,longitude:lon},radius_km:radius,candidates:rows,proposed_visits:visits,source:context.provenance,limitations:['Exploratory uncalibrated scores, not drilling recommendations','Tree dispersion is not a confidence interval','Distance and support thresholds are unvalidated heuristics','No community needs data or technical/community reports were used to train these models','Historical CADASTRE status is not a dated drilling outcome']};
  const ordered=[...rows].sort((a,b)=>b.production.score-a.production.score),selected=new Map(visits.map(v=>[v.id,v.visit_reason]));
  $('hCandidates').innerHTML='<caption>Escores históricos; CE alta significa acima de 3.000 µS/cm. Linhas selecionadas são propostas de visitas.</caption><thead><tr><th>Latitude</th><th>Longitude</th><th>Domínio</th><th>Estrutura (km)</th><th>Escore produção</th><th>Escore CE alta</th><th>Proposta de visita</th></tr></thead><tbody>'+ordered.map(c=>`<tr><td>${fmt(c.latitude,5)}</td><td>${fmt(c.longitude,5)}</td><td>${esc(c.hydrolithological_domain)}</td><td>${fmt(c.mapped_structure_distance_km)}</td><td>${fmt(c.production.score,3)}</td><td>${fmt(c.salinity.score,3)}</td><td>${esc(selected.get(c.id)||'')}</td></tr>`).join('')+(rows.length?'':'<tr><td colspan="7">Nenhum ponto atende aos critérios de suporte desta grade.</td></tr>')+'</tbody>';
  const names={cadastre:'Cadastro com profundidade',geology:'Cadastro + geologia',pre_drill:'Geologia sem profundidade'};
  $('hValidation').innerHTML='<thead><tr><th>Tarefa</th><th>Entradas</th><th>Faixa (km)</th><th>Acurácia balanceada</th><th>Registros avaliados</th></tr></thead><tbody>'+Object.entries(report.tasks).flatMap(([task,t])=>t.evaluations.map(e=>`<tr><td>${task==='potential'?'Produção × seco':'CE alta'}</td><td>${names[e.feature_set]}</td><td>${e.buffer_km}</td><td>${e.metrics?fmt(100*e.metrics.balanced_accuracy,1)+'%':'Insuficiente'}</td><td>${e.tested_n}</td></tr>`)).join('')+'</tbody>';
  $('hStatus').textContent=`${rows.length} candidatos com suporte em ${tested} pontos examinados; ${visits.length} visitas propostas com separação mínima de 1 km. A primeira prioriza escore de produção; as demais, dispersão entre árvores. Verifique acesso, geologia e necessidades da comunidade. Não há benefício de campo comprovado.`;$('hExport').disabled=false;
 }catch(e){$('hStatus').textContent=e.message;$('hCandidates').innerHTML='<tbody><tr><td>Plano indisponível para as entradas atuais.</td></tr></tbody>';}finally{$('hPlan').disabled=false;}
}
$('hPlan').addEventListener('click',plan);$('hExport').addEventListener('click',()=>{if(!last)return;const u=URL.createObjectURL(new Blob([JSON.stringify(last,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=u;a.download='AguaTwin_plano_investigacao.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);});
['aiLat','aiLon','aiRadius'].forEach(id=>$(id).addEventListener('input',invalidate));['aiMunicipality','aiWell','aiTask'].forEach(id=>$(id).addEventListener('change',invalidate));
window.AguaTwinHydroUI={plan,getLast:()=>last};
})();
