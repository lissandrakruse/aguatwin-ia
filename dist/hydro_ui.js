(() => {
'use strict';
const $=id=>document.getElementById(id),H=window.AguaTwinHydro;
const fmt=(n,d=2)=>Number(n).toLocaleString('pt-BR',{maximumFractionDigits:d,minimumFractionDigits:d});
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let loaded=null,last=null,revision=0,pending=null,report=null;
function validation(){if(!report){const el=$('hydro-validation-data');if(!el)throw Error('Os resultados não estão disponíveis nesta versão. Atualize a página.');report=JSON.parse(el.textContent);}return report;}
async function load(){
 if(!loaded)loaded=(async()=>{
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),45000);
  try{
   const [context,models]=await Promise.all(['hydro_context.json','hydro_models.json'].map(async path=>{const r=await fetch(new URL(path,document.baseURI).href,{signal:controller.signal});if(!r.ok)throw Error('Não foi possível carregar os dados de geologia. Tente preparar o plano novamente.');return r.json();}));
   await new Promise(resolve=>setTimeout(resolve,0));
   return {context:H.prepare(context),models};
  }catch(e){loaded=null;if(e.name==='AbortError')throw Error('O carregamento excedeu 45 segundos. Verifique a conexão e tente novamente.');throw e;}finally{clearTimeout(timeout);}
 })();
 return loaded;
}
function invalidate(){revision++;last=null;for(const id of ['hExport','hExportCSV','hExportJSON','hShowMap'])$(id).disabled=true;$('hPlanView').hidden=true;$('hStatus').textContent='O local mudou. Prepare novamente as visitas para usar as coordenadas atuais.';$('hCandidates').innerHTML='<tbody><tr><td>Prepare um novo plano para este local.</td></tr></tbody>';window.AguaTwinMap?.clearVisits();}
function renderTests(){
 try{
  const r=validation(),names={cadastre:'Cadastro com profundidade',geology:'Cadastro + geologia',pre_drill:'Geologia sem profundidade'};
  $('hValidation').innerHTML='<thead><tr><th>Pergunta</th><th>Dados usados</th><th>Isolamento (km)</th><th>Acurácia</th><th>Acurácia balanceada</th><th>F1 macro</th><th>Registros</th></tr></thead><tbody>'+Object.entries(r.tasks).flatMap(([task,t])=>t.evaluations.map(e=>`<tr><td>${task==='potential'?'Produção ou seco':'Mais ou menos sais'}</td><td>${names[e.feature_set]}</td><td>${e.buffer_km}</td><td>${e.metrics?fmt(100*e.metrics.accuracy,1)+'%':'Insuficiente'}</td><td>${e.metrics?fmt(100*e.metrics.balanced_accuracy,1)+'%':'Insuficiente'}</td><td>${e.metrics?fmt(e.metrics.macro_f1,3):'Insuficiente'}</td><td>${fmt(e.tested_n,0)}</td></tr>`)).join('')+'</tbody>';
  $('hResults').hidden=false;$('hTestStatus').textContent='18 testes mostrados abaixo. Resultados históricos; não comprovam sucesso de perfuração.';
  return r;
 }catch(e){$('hTestStatus').textContent=e.message;return null;}
}
function visitsTable(visits){return '<thead><tr><th>Visita</th><th>Latitude</th><th>Longitude</th><th>Cidade de referência</th><th>Objetivo</th></tr></thead><tbody>'+visits.map((v,i)=>`<tr><td>V${i+1}</td><td>${v.latitude.toFixed(5)}</td><td>${v.longitude.toFixed(5)}</td><td>${esc(v.municipality_reference)}</td><td>${i===0?'Investigar o maior escore de produção da grade':'Coletar dados onde há maior dispersão entre as árvores'}</td></tr>`).join('')+'</tbody>';}
async function prepare(){
 const rev=revision;$('hPlan').disabled=true;last=null;for(const id of ['hExport','hExportCSV','hExportJSON','hShowMap'])$(id).disabled=true;$('hPlanView').hidden=true;window.AguaTwinMap?.clearVisits();$('hStatus').textContent='Carregando o mapa de rochas e os modelos. Aguarde…';
 try{
  await window.AguaTwinAI.ready;
  const lat=$('aiLat').valueAsNumber,lon=$('aiLon').valueAsNumber,radius=$('aiRadius').valueAsNumber;
  if(![lat,lon,radius].every(Number.isFinite)||radius<.5||radius>10)throw Error('Informe coordenadas e um raio entre 0,5 e 10 km.');
  if(!window.AguaTwinAI.insideBoundary([lat,lon]))throw Error('Escolha um centro dentro da Paraíba.');
  const {context,models}=await load();if(rev!==revision)throw Error('O local mudou durante o carregamento. Prepare o plano novamente.');
  const records=window.AguaTwinAI.state.bundle.tasks.potential.records,rows=[];let tested=0;
  for(let y=-3;y<=3;y++)for(let x=-3;x<=3;x++){
   if((x===0&&y===0)||Math.hypot(x,y)>3)continue;tested++;
   if(tested%4===0){$('hStatus').textContent=`Analisando o ponto ${tested} de 28…`;await new Promise(resolve=>setTimeout(resolve,0));if(rev!==revision)throw Error('O local mudou. Prepare as visitas novamente.');}
   const latitude=lat+y*radius/3/111.195,longitude=lon+x*radius/3/(111.195*Math.cos(lat*Math.PI/180)),point=[latitude,longitude];
   if(!window.AguaTwinAI.insideBoundary(point))continue;
   const prod=H.support(models.tasks.potential,point),sal=H.support(models.tasks.salinity,point);
   if(prod.distance_km<.15||prod.distance_km>5||sal.distance_km>5)continue;
   if(Object.values(models.tasks).some(t=>point.some((v,i)=>v<t.bounds.min[i]||v>t.bounds.max[i])))continue;
   const f=H.features(context,latitude,longitude);if(f.domain_polygon_matches!==1)continue;
   const reference=records.find(r=>r.id===prod.id);
   rows.push({...f,id:`p${tested}`,municipality_reference:reference?.municipality||'Não informada',nearest_production_id:prod.id,nearest_salinity_id:sal.id,nearest_production_km:prod.distance_km,nearest_salinity_km:sal.distance_km,production:H.infer(models.tasks.potential,f),salinity:H.infer(models.tasks.salinity,f)});
  }
  if(rev!==revision)throw Error('O local mudou. Prepare as visitas novamente.');
  const visits=H.selectVisits(rows);renderTests();
  if(!visits.length){$('hStatus').textContent='A grade não tem pontos com dados suficientes para preparar visitas. Troque o centro ou o raio. Isso não indica ausência de água.';$('hCandidates').innerHTML='<tbody><tr><td>Nenhuma hipótese atende aos critérios de dados desta grade.</td></tr></tbody>';return null;}
  const centerReference=records.find(r=>r.id===H.support(models.tasks.potential,[lat,lon]).id);
  last={version:'2.1',created_at:new Date().toISOString(),center:{latitude:lat,longitude:lon,municipality_reference:centerReference?.municipality||$('aiMunicipality').value},radius_km:radius,candidates:rows,proposed_visits:visits,source:context.provenance,limitations:['Exploratory uncalibrated scores, not drilling recommendations','Tree dispersion is not a confidence interval','Distance and support thresholds are unvalidated heuristics','No community needs data or technical/community reports were used to train these models','Historical CADASTRE status is not a dated drilling outcome']};
  const ordered=[...rows].sort((a,b)=>b.production.score-a.production.score);
  $('hVisits').innerHTML=visitsTable(visits);
  $('hCandidates').innerHTML='<thead><tr><th>Ponto</th><th>Latitude</th><th>Longitude</th><th>Cidade de referência</th><th>Escore produção</th><th>Escore sais</th></tr></thead><tbody>'+ordered.map(c=>`<tr><td>${esc(c.id)}</td><td>${c.latitude.toFixed(5)}</td><td>${c.longitude.toFixed(5)}</td><td>${esc(c.municipality_reference)}</td><td>${fmt(c.production.score,3)}</td><td>${fmt(c.salinity.score,3)}</td></tr>`).join('')+'</tbody>';
  $('hPlanSummary').textContent=`${visits.length} visitas propostas entre ${rows.length} hipóteses, com pelo menos 1 km entre as visitas. Centro: ${lat.toFixed(5)}, ${lon.toFixed(5)}; raio: ${radius} km.`;
  $('hPlanView').hidden=false;for(const id of ['hExport','hExportCSV','hExportJSON','hShowMap'])$(id).disabled=false;
  window.AguaTwinMap?.showVisits(visits,last.center,radius);
  $('hStatus').textContent=`Plano pronto: ${visits.length} visitas. Os marcadores roxos V1, V2… estão no mapa. Você pode ler o plano abaixo ou baixá-lo.`;
  return last;
 }catch(e){last=null;$('hStatus').textContent=e.message;$('hCandidates').innerHTML='<tbody><tr><td>Plano indisponível para este local. Os resultados dos testes podem ser abertos separadamente.</td></tr></tbody>';return null;}finally{$('hPlan').disabled=false;}
}
function plan(){if(pending)return pending;pending=prepare().finally(()=>{pending=null;});return pending;}
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);}
function exportPlan(kind='html'){
 if(!last){$('hStatus').textContent='Primeiro prepare um plano com visitas válidas.';return;}
 if(kind==='json'){download('AguaTwin_plano_investigacao.json',JSON.stringify(last,null,2),'application/json');return;}
 if(kind==='csv'){const cols=['visit','latitude','longitude','municipality_reference','production_score','salinity_score','visit_reason'],cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';download('AguaTwin_visitas_coordenadas.csv',cols.join(',')+'\n'+last.proposed_visits.map((v,i)=>[i+1,v.latitude,v.longitude,v.municipality_reference,v.production.score,v.salinity.score,v.visit_reason].map(cell).join(',')).join('\n'),'text/csv;charset=utf-8');return;}
 const body=`<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ÁguaTwin • Plano de visitas</title><style>body{font:16px/1.5 system-ui;max-width:1100px;margin:25px auto;padding:20px;color:#123d3a}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #dce6e0;padding:8px;text-align:left}th{background:#e7f2ec}.table{overflow:auto}</style><h1>Plano de visitas de campo</h1><p>Cidade de referência: ${esc(last.center.municipality_reference)}. Centro: ${last.center.latitude.toFixed(5)}, ${last.center.longitude.toFixed(5)}. Raio: ${last.radius_km} km.</p><p>Gerado em ${esc(last.created_at)}. ${last.candidates.length} hipóteses examinadas com dados suficientes; ${last.proposed_visits.length} visitas propostas.</p><div class="table"><table>${visitsTable(last.proposed_visits)}</table></div><h2>Antes de ir a campo</h2><p>Confirme acesso à área e registre as observações geológicas e geofísicas. Estas coordenadas são hipóteses para investigação. Não confirmam água, vazão ou qualidade.</p><p>Dados: SGB/SIAGAS e mapa hidrogeológico regional do SGB. As cidades indicam a referência do cadastro mais próximo; não definem o limite municipal de cada ponto.</p><h2>Todas as hipóteses do plano</h2><div class="table"><table><tr><th>Ponto</th><th>Latitude</th><th>Longitude</th><th>Cidade de referência</th></tr>${last.candidates.map(c=>`<tr><td>${esc(c.id)}</td><td>${c.latitude.toFixed(5)}</td><td>${c.longitude.toFixed(5)}</td><td>${esc(c.municipality_reference)}</td></tr>`).join('')}</table></div></html>`;
 download('AguaTwin_plano_visitas.html',body,'text/html;charset=utf-8');
}
$('hPlan').addEventListener('click',plan);$('hTests').addEventListener('click',renderTests);
$('hExport').addEventListener('click',()=>exportPlan());$('hExportCSV').addEventListener('click',()=>exportPlan('csv'));$('hExportJSON').addEventListener('click',()=>exportPlan('json'));
$('hReportJSON').addEventListener('click',()=>download('AguaTwin_resultados_18_testes.json',JSON.stringify(validation(),null,2),'application/json'));
$('hShowMap').addEventListener('click',()=>{if(!last)return;window.AguaTwinMap?.showVisits(last.proposed_visits,last.center,last.radius_km);$('wellMapCard').scrollIntoView?.({behavior:'smooth',block:'start'});});
['aiLat','aiLon','aiRadius'].forEach(id=>$(id).addEventListener('input',invalidate));['aiMunicipality','aiWell','aiTask'].forEach(id=>$(id).addEventListener('change',invalidate));window.addEventListener('aguatwin-location-changed',invalidate);
window.AguaTwinHydroUI={plan,getLast:()=>last,whenIdle:()=>pending||Promise.resolve(last),renderTests,exportPlan};
})();


(()=>{const host=document.getElementById('wellMapCard');if(host&&!document.getElementById('chemistryLink')){const p=document.createElement('p');const a=document.createElement('a');a.id='chemistryLink';a.href='quimica.html';a.textContent='Consultar dados químicos públicos auditados';p.appendChild(a);host.appendChild(p);}})();
