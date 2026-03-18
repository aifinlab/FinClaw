#!/usr/bin/env node
const fs=require('fs');
function parse(argv){const a={};for(let i=2;i<argv.length;i++){const t=argv[i];if(!t.startsWith('--'))continue;const k=t.slice(2);const n=argv[i+1];if(!n||n.startsWith('--'))a[k]=true;else{a[k]=n;i++;}}return a;}
function load(fp){const raw=fs.readFileSync(fp,'utf8').trim();if(!raw)return [];if(raw.startsWith('[')){const d=JSON.parse(raw);if(!Array.isArray(d))throw new Error('JSON input must be an array.');return d.filter(x=>x&&typeof x==='object');}return raw.split(/?
/).map(x=>x.trim()).filter(Boolean).map((line,i)=>{const o=JSON.parse(line);if(!o||typeof o!=='object'||Array.isArray(o))throw new Error(`JSONL line ${i+1} must be object.`);return o;});}
function main(){const a=parse(process.argv);if(!a.input){console.error('Usage: node scripts/preprocess.js --input in.jsonl --output out.json');process.exit(1);}const rows=load(a.input);const out=rows.map(r=>{const vals=Object.values(r);const present=vals.filter(v=>v!==null&&v!==undefined&&v!=='').length;return {...r,data_completeness:vals.length?present/vals.length:0,full_text:vals.map(v=>String(v??'')).join(' ')};});const payload=JSON.stringify(out,null,a.pretty?2:0);if(a.output){fs.writeFileSync(a.output,payload,'utf8');console.log(`Processed ${out.length} records -> ${a.output}`);}else process.stdout.write(payload+'
');}
main();
