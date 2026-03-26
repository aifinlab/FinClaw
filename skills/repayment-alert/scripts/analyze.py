#!/usr/bin/env python3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List
import argparse, json, re, sys
# ===== AkShare开源数据支持（新增） =====
from skillsChoice.common.unified_data_api import (
    get_data_api,
)
# ====================================

def load_items(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding='utf-8').strip()
    if not raw: return []
    if raw.lstrip().startswith('['):
        data=json.loads(raw)
        if not isinstance(data,list): raise ValueError('JSON input must be an array.')
        return [x for x in data if isinstance(x,dict)]
    items=[]
    for idx,line in enumerate(raw.splitlines(),start=1):
        t=line.strip()
        if not t: continue
        obj=json.loads(t)
        if not isinstance(obj,dict): raise ValueError(f'JSONL line {idx} must be object.')
        items.append(obj)
    return items

def load_json(path: Path)->Dict[str,Any]:
    return json.loads(path.read_text(encoding='utf-8'))

def hits(text:str, kws:List[str])->int:
    c=0
    for kw in kws:
        c += len(re.findall(re.escape(kw), text, flags=re.IGNORECASE))
    return c

def lvl(s:int,cuts:Dict[str,Any])->str:
    if s>=int(cuts.get('low_risk',75)): return 'low_risk'
    if s>=int(cuts.get('medium_risk',55)): return 'medium_risk'
    return 'high_risk'

def main():
    p=argparse.ArgumentParser(description='Complex skill analyzer')
    p.add_argument('--input',required=True)
    p.add_argument('--rules',required=True)
    p.add_argument('--baseline',required=True)
    p.add_argument('--output')
    p.add_argument('--top',type=int,default=15)
    p.add_argument('--title',default='Skill Report')
    a=p.parse_args()

    items=load_items(Path(a.input)); rules=load_json(Path(a.rules)); base=load_json(Path(a.baseline))
    pos=rules.get('positive_keywords',[]); neg=rules.get('negative_keywords',[])
    score_base=int(rules.get('score_base',60))
    out=[]
    for i,it in enumerate(items,start=1):
        txt=str(it.get('full_text','')) or ' '.join(str(v) for v in it.values())
        ph=hits(txt,pos); nh=hits(txt,neg)
        comp=float(it.get('data_completeness',0) or 0)
        score=score_base+min(ph*2,10)-min(nh*5,25)
        reasons=[]
        if ph: reasons.append(f'positive_hits={ph}')
        if nh: reasons.append(f'negative_hits={nh}')
        if comp<0.6: score-=8; reasons.append('data_completeness_low')
        elif comp>0.9: score+=2; reasons.append('data_completeness_high')
        score=max(0,min(100,score))
        out.append({'id':it.get('id',f'R{i:03d}'),'score':score,'level':lvl(score,rules.get('level_cutoffs',{})),'reasons':reasons})

    c=Counter(x['level'] for x in out)
    lines=[f"# {a.title}",'','## 一、概览',f"- 样本数: {len(out)}",f"- low_risk: {c.get('low_risk',0)}",f"- medium_risk: {c.get('medium_risk',0)}",f"- high_risk: {c.get('high_risk',0)}",'','## 二、重点条目']
    for x in sorted(out,key=lambda z:z['score'])[:a.top]:
        lines.append(f"- {x['id']} | score={x['score']} | level={x['level']} | reasons={'; '.join(x['reasons'][:4]) or 'N/A'}")
    lines += ['','## 三、基线',f"- baseline_version: {base.get('version','unknown')}",'','## 四、免责声明','- 本报告由系统自动生成，仅用于业务初筛。','- 结论需由业务、风控、法务人工复核后使用。','- 本报告不构成投资建议、授信决策或法律意见。']
    rep='\n'.join(lines)
    if a.output: Path(a.output).write_text(rep,encoding='utf-8')
    else: sys.stdout.write(rep+'\n')

if __name__=='__main__':
    main()
