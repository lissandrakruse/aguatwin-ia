const {spawnSync}=require('node:child_process'),path=require('node:path');
for(const file of ['verify_ai.cjs','verify_v2_1.cjs']){const r=spawnSync(process.execPath,[path.join(__dirname,file)],{stdio:'inherit'});if(r.status!==0)process.exit(r.status||1);}
const p=spawnSync('python3',[path.join(__dirname,'verify_field_reports.py')],{stdio:'inherit'});if(p.status!==0)process.exit(p.status||1);
