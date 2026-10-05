(function(root){'use strict';
function finite(v,name,min,max=Infinity){if(!Number.isFinite(v)||v<min||v>max)throw Error(name+': valor inválido.');return v;}
function conditions(c){for(const k of ['available_kwh_day','energy_brl_kwh','concentrate_brl_m3','daily_budget_brl'])finite(c[k],k,0);finite(c.tds_limit_mg_l,'Limite de sais',0);finite(c.demand_m3_day,'Demanda',.000001);return c;}
function evaluate(o,c){
 conditions(c);for(const k of ['flow_m3_h','hours_day','tds_mg_l','dynamic_head_m','fixed_cost_brl_day'])finite(o[k],k,0);finite(o.hours_day,'Horas',0,24);finite(o.recovery,'Recuperação',.01,.99);finite(o.rejection,'Rejeição',0,1);finite(o.pump_efficiency,'Eficiência da bomba',.01,1);finite(o.ro_kwh_per_m3_permeate,'Consumo de tratamento',.01);
 const pump_per_feed=1000*9.80665*o.dynamic_head_m/(3600000*o.pump_efficiency),energy_per_feed=pump_per_feed+o.recovery*o.ro_kwh_per_m3_permeate;
 const variable_per_feed=energy_per_feed*c.energy_brl_kwh+(1-o.recovery)*c.concentrate_brl_m3,potential_feed=o.flow_m3_h*o.hours_day,budget_eligible=o.fixed_cost_brl_day<=c.daily_budget_brl;
 const feed=budget_eligible?Math.max(0,Math.min(potential_feed,c.available_kwh_day/energy_per_feed,variable_per_feed?(c.daily_budget_brl-o.fixed_cost_brl_day)/variable_per_feed:Infinity)):0;
 const permeate=feed*o.recovery,concentrate=feed-permeate,permeate_tds=o.tds_mg_l*(1-o.rejection),concentrate_tds=concentrate?(feed*o.tds_mg_l-permeate*permeate_tds)/concentrate:null;
 const energy=feed*energy_per_feed,cost=o.fixed_cost_brl_day+energy*c.energy_brl_kwh+concentrate*c.concentrate_brl_m3,conditional_volume=permeate_tds<=c.tds_limit_mg_l?permeate:0;
 return {id:o.id,potential_feed_m3:potential_feed,feed_m3:feed,permeate_m3:permeate,concentrate_m3:concentrate,permeate_tds_mg_l:permeate_tds,concentrate_tds_mg_l:concentrate_tds,energy_kwh:energy,cost_brl:cost,budget_eligible,conditional_volume_m3:conditional_volume,cost_per_conditional_m3:conditional_volume?cost/conditional_volume:null,demand_coverage:Math.min(1,conditional_volume/c.demand_m3_day),volume_balance_m3:feed-permeate-concentrate,salt_balance_kg:feed*o.tds_mg_l/1000-permeate*permeate_tds/1000-(concentrate_tds===null?0:concentrate*concentrate_tds/1000)};
}
function compare(options,c){
 if(!Array.isArray(options)||!options.length)throw Error('Informe alternativas medidas ou de cenário.');const ids=new Set();for(const o of options){if(!o.id||ids.has(o.id))throw Error('Identificadores precisam ser únicos.');ids.add(o.id);}
 const results=options.map(o=>evaluate(o,c)),eligible=results.filter(r=>r.budget_eligible&&r.feed_m3>0),byRaw=(a,b)=>b.potential_feed_m3-a.potential_feed_m3||a.id.localeCompare(b.id),byUseful=(a,b)=>b.conditional_volume_m3-a.conditional_volume_m3||a.cost_brl-b.cost_brl||a.id.localeCompare(b.id);
 const select=list=>list.length?list[0].id:null;
 return {results,strategies:{production:select([...eligible].sort(byRaw)),production_and_feed_salinity:select(eligible.filter(r=>options.find(o=>o.id===r.id).tds_mg_l<=c.tds_limit_mg_l).sort(byRaw)),conditional_treated_water:select(eligible.filter(r=>r.conditional_volume_m3>0).sort(byUseful))},conditions:{...c},limitations:['Conditional volume uses only an experimental salt criterion; it does not certify potability or irrigation suitability','Ideal daily steady-state RO; no fouling, intermittent power or tank constraints','Input costs must include amortized capital, operation, maintenance and concentrate handling','Inputs require pumping, water, treatment and energy measurements for field use']};
}
const api={evaluate,compare,conditions};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AguaTwinDecision=api;
})(typeof window!=='undefined'?window:globalThis);
