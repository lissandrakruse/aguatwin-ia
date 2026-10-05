from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parent; DIST=ROOT.parent/'dist'
base=(ROOT/'base_simulator.html').read_text()
base=base.replace('<title>ÁguaTwin | Simulador de pesquisa</title>','<title>ÁguaTwin IA | Hipóteses de poços na Paraíba</title>')
base=base.replace('</style>', '''
body{font-size:16px}label,.metric .label{font-size:14px}.small{font-size:13px}header{padding-top:20px;padding-bottom:20px}h1{font-size:30px}header p{font-size:15px;margin:4px 0}.status{margin-top:6px}.ai-grid{grid-template-columns:320px 1fr}.section-top{display:flex;justify-content:space-between;align-items:center;gap:12px}.badge{font-size:12px;background:#e7f2ec;border:1px solid #ccd9d3;border-radius:20px;padding:4px 10px}.blue{background:#3368b2}.geo-map{width:100%;overflow:hidden;border-radius:8px}.geo-map svg{width:100%;display:block}#aiBenchmark{height:230px}.btn{text-decoration:none;display:inline-block}button:disabled{opacity:.55;cursor:default}details p{font-size:14px}.notice{font-size:14px}.r-strategies{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.r-choice{font-size:23px;font-weight:700}#rInputs input{min-width:105px}caption{caption-side:bottom;text-align:left;font-size:13px;color:var(--muted);padding:10px 0}#hCandidates td:last-child{white-space:normal;min-width:200px}@media(max-width:900px){.ai-grid{grid-template-columns:1fr}.r-strategies{grid-template-columns:1fr}}
</style>''')
favicon='<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="vendor/leaflet.css"><link rel="stylesheet" href="interface.css">'
base=base.replace('</head>',favicon+'</head>')
# Inline the map styles so each geographic marker is positioned even if a linked stylesheet fails.
for sheet in ['vendor/leaflet.css','interface.css']:
    base=base.replace(f'<link rel="stylesheet" href="{sheet}">','<style>'+(DIST/sheet).read_text().replace('url(images/','url(vendor/images/')+'</style>')
(DIST/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#173f3a"/><path d="M16 5C12 11 8 15 8 20a8 8 0 0016 0c0-5-4-9-8-15Z" fill="#53d5ce"/><path d="M12 21h8M12 25h6" stroke="#173f3a" stroke-width="2"/></svg>')
start=base.index('<header>');end=base.index('</header>',start)+len('</header>')
base=base[:start]+'''<header><div class="eyebrow">Pesquisa aplicada • Paraíba</div><h1>ÁguaTwin IA</h1><p>Locais para investigar poços em comunidades rurais da Paraíba.</p><span class="status">Mapa de pesquisa • cadastro SGB/SIAGAS • localização e coordenadas</span></header>'''+base[end:]
start=base.index('<main><div class="notice">');end=base.index('</div>',start)+len('</div>')
base=base[:start]+'''<main><div class="notice"><b>Comece pelo mapa.</b> Os pontos azuis são sugestões para estudar em campo. A visita de uma equipe técnica é necessária para avaliar a possibilidade de perfuração.</div>'''+base[end:]
base=base.replace('<button class="active" data-tab="sim">','<button class="active" data-tab="ai">Mapa de poços</button><button data-tab="rural">Água útil e campo</button><button data-tab="sim">')
ai_panel=(ROOT/'ai_panel.html').read_text().replace('<details class="card data-sources">',(ROOT/'hydro_panel.html').read_text()+'\n<details class="card data-sources">')
base=base.replace('<section id="sim" class="panel active">',ai_panel+'\n'+(ROOT/'rural_panel.html').read_text()+'\n<section id="sim" class="panel">')
# Keep legacy research tools available to reproducibility checks, outside the simplified map interface.
for tab in ['rural','sim','nasa','wells','field','methods']:
    base=base.replace(f'<button data-tab="{tab}">',f'<button hidden data-tab="{tab}">')
base=base.replace('<p id="scenarioWell"','<p id="simClimateNote" class="small">Clima: Cabaceiras, −7,49°, −36,29°, NASA POWER 2024–2025.</p><p id="scenarioWell"')
base=base.replace('const byDate=new Map(daily.map(d=>[d.date,d]));','const byDate=new Map(daily.map(d=>[d.date,d]));\nlet simClimate=daily,simClimateSource=NASA.provenance;')
base=base.replace('function model(p){const period=daily.filter','function model(p){const period=simClimate.filter')
base=base.replace("version:'1.1',source:NASA.provenance", "version:'2.0',source:simClimateSource")
base=base.replace('window.AguaTwin={model,compareRows,parseCSV,daily,summary,monthly,wells,wellStats:WELL_DATA.stats,scenarioWellBinding,csvCell};renderSim();', '''
function setClimate(rows,source){if(!Array.isArray(rows)||rows.length!==731||rows.some(r=>!Number.isFinite(r.rain)||!Number.isFinite(r.solar)||!Number.isFinite(r.temp)))throw Error('Clima inválido.');simClimate=rows;simClimateSource=source;$('simClimateNote').textContent=`Clima: ponto ${source.latitude}°, ${source.longitude}°, NASA POWER 2024–2025. A comparação histórica na aba NASA conserva o ponto inicial de Cabaceiras.`;renderSim();}
function restoreClimate(){simClimate=daily;simClimateSource=NASA.provenance;$('simClimateNote').textContent='Clima: Cabaceiras, −7,49°, −36,29°, NASA POWER 2024–2025.';renderSim();}
window.AguaTwin={model,compareRows,parseCSV,daily,summary,monthly,wells,wellStats:WELL_DATA.stats,scenarioWellBinding,csvCell,setClimate,restoreClimate,getClimate:()=>({rows:simClimate,source:simClimateSource})};renderSim();''')
base=base.replace('<h2>Chuva mensal estimada pela NASA</h2>','<h2>Chuva NASA • referência Cabaceiras</h2>')
base=base.replace('<section id="nasa" class="panel">','<section id="nasa" class="panel"><div class="notice">Comparação histórica do ponto inicial de Cabaceiras (−7,49°, −36,29°). Consultas da API por coordenadas aparecem em “Hipóteses e cinco IAs” e atualizam o cenário de água e energia.</div>')
ref='''<div class="card"><h2>Trabalhos próximos e contribuição a testar</h2><p><a href="https://seer.ufu.br/index.php/revistabrasileiracartografia/article/view/65381" target="_blank" rel="noopener">Souza et al. (2023): potencial de águas subterrâneas no norte de Minas Gerais</a>. Comparou seis algoritmos usando vazões de 4.028 poços SIAGAS e variáveis ambientais. A relação entre IA e potencial hídrico já tem antecedentes.</p><p><a href="https://periodicos.ufal.br/contextogeografico/article/view/18434" target="_blank" rel="noopener">Vio et al. (2025): identificação de depósitos aluviais no Riacho do Tigre/PB</a>. Usou árvore de decisão e variáveis de sensoriamento remoto para classificar áreas aluviais; não é previsão direta de sucesso de perfuração.</p><p>A proposta ÁguaTwin combina comparação espacial transparente, salinidade e simulação operacional com clima NASA. Essa combinação é uma hipótese de contribuição; a busca apresentada não comprova ineditismo. Para um mestrado, precisamos acrescentar variáveis hidrogeológicas e validação independente nos locais escolhidos.</p></div>'''
base=base.replace('<section id="methods" class="panel">','<section id="methods" class="panel">'+ref)
base=base.replace('</body>','<script src="vendor/leaflet.js"></script><script src="well_map.js"></script><script src="ai.js"></script><script src="decision.js"></script><script src="rural.js"></script><script src="hydro.js"></script><script src="hydro_ui.js"></script></body>')
import json
validation=json.dumps(json.loads((DIST/'hydro_validation.json').read_text()),ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
base=base.replace('<script src="hydro.js"></script>',f'<script id="hydro-validation-data" type="application/json">{validation}</script><script src="hydro.js"></script>')
# New source hashes prevent a browser from pairing fresh controls with old cached scripts.
import hashlib,re
def version_script(match):
    path=match.group(1);file=DIST/path
    return f'<script src="{path}?v={hashlib.sha256(file.read_bytes()).hexdigest()[:12]}"></script>' if file.is_file() else match.group(0)
base=re.sub(r'<script src="([^"]+)"></script>',version_script,base)
(DIST/'index.html').write_text(base)
for src,dest in [(ROOT/'field_report_template.json','field_report_template.json'),(ROOT.parent/'docs/AGUA_RURAL_NORDESTE.md','protocolo_campo.md'),(ROOT.parent/'docs/RESULTADOS_V2_1.md','resultados_v2_1.md')]:
    if src.exists():(DIST/dest).write_bytes(src.read_bytes())
with zipfile.ZipFile(DIST/'metodos_IA.zip','w',zipfile.ZIP_DEFLATED) as z:
    for filename in ['compare_five_models.py','fetch_potential.py','fetch_paraiba.py','prepare_state_dataset.py','fetch_hydrogeology.py','train_hydrogeology.py','import_field_reports.py','field_report_template.json','verify_field_reports.py','README.md']:
        p=ROOT/filename
        if p.exists():z.write(p,filename)
print('site built',len(base),'characters')
