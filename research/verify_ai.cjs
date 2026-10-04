const fs=require('fs'),path=require('path'),assert=require('assert');
const {JSDOM,VirtualConsole}=require('jsdom');
const {createCanvas}=require('@napi-rs/canvas');
const root=path.resolve(__dirname,'..'),dist=path.join(root,'dist');
(async()=>{
 const model=JSON.parse(fs.readFileSync(path.join(dist,'ai_models.json'),'utf8')),boundary=JSON.parse(fs.readFileSync(path.join(dist,'paraiba_boundary.json'),'utf8')),references=JSON.parse(fs.readFileSync(path.join(__dirname,'reference_predictions.json'),'utf8'));
 const errors=[],tools=[],downloads=[],canvases=new Map();let nasaReply=null,nasaFailure=false;
 const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(fs.readFileSync(path.join(dist,'index.html'),'utf8'),{url:'https://qa.invalid/',runScripts:'dangerously',virtualConsole:vc,beforeParse(w){
  Object.defineProperty(w.HTMLCanvasElement.prototype,'clientWidth',{get(){return 700;}});
  w.HTMLCanvasElement.prototype.getContext=function(){let c=canvases.get(this.id);if(!c||c.width!==this.width||c.height!==this.height){c=createCanvas(this.width,this.height);canvases.set(this.id,c);}return c.getContext('2d');};
  w.URL.createObjectURL=()=> 'blob:qa-local';w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=function(){downloads.push(this.download);};
  w.document.modelContext={registerTool:t=>tools.push(t)};
  w.fetch=async url=>{if(String(url)==='ai_models.json')return {ok:true,json:async()=>model};if(String(url)==='paraiba_boundary.json')return {ok:true,json:async()=>boundary};if(String(url).startsWith('https://power.larc.nasa.gov/api/')){if(nasaFailure)throw Error('Injected network failure');return {ok:true,json:async()=>nasaReply};}throw Error('Unexpected fetch '+url);};
 }});
 const w=dom.window,d=w.document,a=w.AguaTwin;
 assert(a,'Water model initialized');assert.equal(a.daily.length,731);
 w.eval(fs.readFileSync(path.join(dist,'ai.js'),'utf8'));await w.AguaTwinAI.ready;const ai=w.AguaTwinAI;
 assert.equal(ai.state.bundle.tasks.potential.n,3022);assert.equal(ai.state.bundle.tasks.salinity.n,8234);assert.equal(d.querySelectorAll('.panel.active').length,1);assert(d.getElementById('ai').classList.contains('active'));
 assert.equal(d.getElementById('aiComparison').querySelectorAll('tbody tr').length,5);assert.equal(ai.state.lastPrediction.mode,'out-of-fold');
 let checked=0,maxScoreError=0;
 for(const [task,methods] of Object.entries(references))for(const [name,refs] of Object.entries(methods))for(const ref of refs){const got=ai.infer(model.tasks[task],name,ref.input);assert.equal(got.label,ref.label,`${task} ${name} at ${ref.input}`);if(ref.score!==null){const err=Math.abs(got.score-ref.score);maxScoreError=Math.max(maxScoreError,err);assert(err<1e-8,`${task} ${name} score diff ${err}`);}checked++;}
 // Every observation stays in one geographical fold; no fabricated negative labels.
 for(const t of Object.values(model.tasks)){const groupFold=new Map();assert.equal(new Set(t.records.map(r=>r.id)).size,t.n);for(const r of t.records){if(groupFold.has(r.group))assert.equal(groupFold.get(r.group),r.fold);else groupFold.set(r.group,r.fold);}assert.equal(groupFold.size,t.groups);}
 for(const r of model.tasks.potential.records){assert.equal(r.measurement_date,null);if(r.label===0){assert.equal(r.status,'Seco');assert(!(r.specific_yield>0));}else {assert(r.specific_yield>0);assert.notEqual(r.status,'Seco');}}
 assert(ai.insideBoundary([-7.49,-36.29]));assert(!ai.insideBoundary([-23.55,-46.63]));assert.throws(()=>ai.validatePoint(model.tasks.potential,[-23.55,-46.63,60]),/fora/);
 const originalInput=ai.inputs();d.getElementById('aiLat').value='-23.55';d.getElementById('aiPredict').click();assert(d.getElementById('aiMessage').textContent.includes('fora'));assert(d.getElementById('aiPrediction').textContent.includes('indisponível'));
 ['aiLat','aiLon','aiDepth'].forEach((id,i)=>d.getElementById(id).value=originalInput[i]);d.getElementById('aiPredict').click();
 d.getElementById('aiCandidates').click();assert(ai.state.candidates.length>0);for(const c of ai.state.candidates){assert(c.nearest_km>=.15&&c.nearest_km<=5);assert(ai.insideBoundary([c.latitude,c.longitude]));}assert.equal(d.getElementById('exportCandidates').disabled,false);d.getElementById('exportCandidates').click();assert(downloads.includes('AguaTwin_hipoteses_nao_confirmadas.csv'));
 d.querySelector('.candidate-use').click();assert.equal(ai.state.lastPrediction.mode,'full-training-fit');
 const p={q:1,hours:1,fraction:100,recovery:60,tds:3000,rejection:98,people:50,lpd:4,area:0,etc:5,eff:85,rainEff:50,capacity:0,initial:0,pv:1000,pr:75,sec:2.5,solarOnly:false,year:'2025',month:9};
 const first=a.model(p).rows[0];assert.equal(first.raw,1000);assert.equal(first.perm,600);assert.equal(first.conc,400);assert.equal(first.human,200);assert(Math.abs(first.cp-60)<1e-9);assert(Math.abs(first.cr-7410)<1e-8);assert(a.model(p).total.maxMassResidual<1e-8);
 const embedded=JSON.parse(d.getElementById('nasa-data').textContent),parameters={};for(const key of ['PRECTOTCORR','T2M','ALLSKY_SFC_SW_DWN'])parameters[key]=Object.assign({},embedded.years['2024'].properties.parameter[key],embedded.years['2025'].properties.parameter[key]);
 nasaReply={properties:{parameter:parameters},parameters:{PRECTOTCORR:{units:'mm/day'},T2M:{units:'C'},ALLSKY_SFC_SW_DWN:{units:'MJ/m^2/day'}},header:{time_standard:'UTC'}};
 const parsed=ai.parseNASA(nasaReply);assert.equal(parsed.length,731);assert.equal(parsed[0].date,'2024-01-01');assert.equal(parsed[730].date,'2025-12-31');assert(Math.abs(parsed.filter(r=>r.date.startsWith('2025')).reduce((s,r)=>s+r.rain,0)-588.65)<1e-8);
 await ai.fetchNASA();assert.equal(a.getClimate().source.provider,'NASA POWER');assert.equal(a.getClimate().rows.length,731);assert(d.getElementById('nasaLiveMessage').textContent.includes('731'));
 const validClimate=a.getClimate();nasaFailure=true;await assert.rejects(ai.fetchNASA(),/Injected/);assert.strictEqual(a.getClimate().rows,validClimate.rows);assert(d.getElementById('nasaLiveMessage').textContent.includes('última série válida'));nasaFailure=false;
 nasaReply.parameters.T2M.units='K';await assert.rejects(ai.fetchNASA(),/Unidade/);assert.strictEqual(a.getClimate().rows,validClimate.rows);nasaReply.parameters.T2M.units='C';
 delete nasaReply.properties.parameter.PRECTOTCORR['20251231'];assert.throws(()=>ai.parseNASA(nasaReply),/incompleta/);nasaReply.properties.parameter.PRECTOTCORR['20251231']=embedded.years['2025'].properties.parameter.PRECTOTCORR['20251231'];
 d.getElementById('nasaRestore').click();assert.strictEqual(a.getClimate().rows,a.daily);
 // WebMCP uses the same validation and visible UI. Invalid actions leave input unchanged.
 assert.equal(tools.length,1);const valid=ai.inputs(),before=[...valid];await assert.rejects(tools[0].execute({latitude:-23,longitude:-46,depth_m:60}),/fora/);assert.deepEqual(Array.from(ai.inputs()),Array.from(before));
 const toolResult=await tools[0].execute({latitude:valid[0],longitude:valid[1],depth_m:valid[2],task:'potential'});assert.equal(JSON.parse(toolResult.content[0].text).input[0],valid[0]);assert.equal(Number(d.getElementById('aiLat').value),valid[0]);
 d.getElementById('aiTask').value='salinity';d.getElementById('aiTask').dispatchEvent(new w.Event('change'));assert.equal(ai.state.task,'salinity');assert(d.getElementById('aiStats').textContent.includes('8.234'));assert.equal(d.getElementById('aiPrediction').querySelectorAll('tbody tr').length,5);
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(__dirname,'qa_benchmark.png'),canvases.get('aiBenchmark').toBuffer('image/png'));
 const report={passed:true,independent_python_predictions_checked:checked,max_score_error:maxScoreError,checks:['shared spatial groups','authentic outcome labels','Python-to-browser model inference','out-of-fold selected-record display','candidate domain and ranking','water and salt balance','NASA valid response and retained state on failure','NASA units and daily completeness','WebMCP valid/invalid action contracts','task switching and downloads'],environment:'jsdom DOM execution and native canvas; full browser layout not tested; WebMCP context stubbed'};
 fs.writeFileSync(path.join(__dirname,'qa_result.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));dom.window.close();
})().catch(e=>{console.error(e);process.exit(1);});
