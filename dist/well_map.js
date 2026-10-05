/* Geographic display only: model scores are computed in ai.js / hydro.js. */
(() => {
  'use strict';
  const L=window.L, $=id=>document.getElementById(id);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=(n,d=5)=>Number(n).toLocaleString('pt-BR',{minimumFractionDigits:d,maximumFractionDigits:d});
  let map,boundaryLayer,recordsLayer,candidatesLayer,centerLayer,areaLayer,frame=null,current=[];
  function init(boundary){
    if(map)return;
    if(!L)throw Error('Não foi possível iniciar o mapa. Atualize a página.');
    map=L.map('aiMap',{preferCanvas:true,scrollWheelZoom:false}).setView([-7.49,-36.29],12);
    const tiles=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'}).addTo(map);
    tiles.on('tileerror',()=>{$('mapTileStatus').textContent='O fundo de ruas não carregou. Os pontos e suas coordenadas continuam disponíveis. Verifique a conexão.';});
    tiles.on('load',()=>{$('mapTileStatus').textContent='Fundo: OpenStreetMap • Poços: SGB/SIAGAS • Contorno da Paraíba: IBGE.';});
    boundaryLayer=L.geoJSON(boundary||{type:'FeatureCollection',features:[]},{style:{color:'#123d3a',weight:2,fill:false}}).addTo(map);
    recordsLayer=L.layerGroup().addTo(map);candidatesLayer=L.layerGroup().addTo(map);centerLayer=L.layerGroup().addTo(map);areaLayer=L.layerGroup().addTo(map);
    L.control.layers(null,{'Poços do cadastro':recordsLayer,'Locais para investigar':candidatesLayer,'Contorno da Paraíba':boundaryLayer},{collapsed:true}).addTo(map);
    L.control.scale({imperial:false,maxWidth:120}).addTo(map);
    $('mapRegion').addEventListener('click',()=>{const b=boundaryLayer.getBounds();if(b.isValid())map.invalidateSize().fitBounds(b,{padding:[20,20]});});
    $('mapLocal').addEventListener('click',local);
    document.querySelector('[data-tab="ai"]').addEventListener('click',()=>map.invalidateSize());
  }
  function local(){if(map&&frame)map.invalidateSize().fitBounds(frame,{padding:[25,25],maxZoom:14});}
  function render(center,records,candidates,radius,boundary,onSelect,anchor=center){
    init(boundary);current=candidates.slice(0,10);recordsLayer.clearLayers();candidatesLayer.clearLayers();centerLayer.clearLayers();areaLayer.clearLayers();
    for(const r of records){
      L.circleMarker([r.latitude,r.longitude],{radius:4,color:'#fff',weight:1,fillColor:r.label?'#087f78':'#bb733e',fillOpacity:.8}).bindPopup(`<b>Poço cadastrado ${esc(r.id)}</b><br>${esc(r.municipality)}<br>${r.label?'Produção de água registrada':'Situação registrada: seco'}<br>Latitude: ${fmt(r.latitude)}<br>Longitude: ${fmt(r.longitude)}<p>Registro histórico; situação atual não verificada.</p>`).addTo(recordsLayer);
    }
    current.forEach((c,i)=>{
      const icon=L.divIcon({className:'candidate-icon',html:`<span class="candidate-pin" data-candidate-index="${i}">${i+1}</span>`,iconSize:[30,30],iconAnchor:[15,15]});
      const marker=L.marker([c.latitude,c.longitude],{icon,title:`Local ${i+1} para investigar. Latitude ${c.latitude.toFixed(5)}, longitude ${c.longitude.toFixed(5)}.`,keyboard:true});
      marker.on('click',()=>onSelect(i));marker.addTo(candidatesLayer);
    });
    L.circleMarker([center[0],center[1]],{radius:7,color:'#123d3a',weight:3,fill:false}).bindTooltip('Centro escolhido').addTo(centerLayer);
    const circle=L.circle([anchor[0],anchor[1]],{radius:radius*1000,color:'#3368b2',weight:1,dashArray:'5 5',fill:false}).addTo(areaLayer);
    frame=circle.getBounds();local();
  }
  function clear(note){if(candidatesLayer)candidatesLayer.clearLayers();if(centerLayer)centerLayer.clearLayers();if(areaLayer)areaLayer.clearLayers();current=[];$('candidateSelection').textContent=note;}
  window.AguaTwinMap={render,clear,local,getMap:()=>map,getCandidates:()=>current};
})();
