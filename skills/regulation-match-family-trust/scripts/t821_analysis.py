#!/usr/bin/env python3
import argparse, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

def load_items(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw.lstrip().startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array.")
        return [x for x in data if isinstance(x, dict)]
    items=[]
    for idx,line in enumerate(raw.splitlines(),start=1):
        t=line.strip()
        if not t: continue
        obj=json.loads(t)
        if not isinstance(obj,dict):
            raise ValueError(f"JSONL line {idx} must be object.")
        items.append(obj)
    return items

def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def hits(text:str, kws:List[str])->int:
    c=0
    for kw in kws:
        c += len(re.findall(re.escape(kw), text, flags=re.IGNORECASE))
    return c

def level(score:int,cuts:Dict[str,Any])->str:
    if score>=int(cuts.get('low_risk',75)): return 'low_risk'
    if score>=int(cuts.get('medium_risk',55)): return 'medium_risk'
    return 'high_risk'

def render(title:str, rs:List[Dict[str,Any]], baseline:Dict[str,Any], top:int)->str:
    cnt=Counter([x['level'] for x in rs])
    lines=[f"# {title}（自动报告）","","## 一、样本概览",f"- 样本数: {len(rs)}",f"- low_risk: {cnt.get('low_risk',0)}",f"- medium_risk: {cnt.get('medium_risk',0)}",f"- high_risk: {cnt.get('high_risk',0)}","","## 二、重点条目"]
    for x in sorted(rs,key=lambda z:z['score'])[:top]:
        lines.append(f"- {x['id']} | score={x['score']} | level={x['level']} | reasons={'; '.join(x['reasons'][:4]) or 'N/A'}")
    lines += ["","## 三、基线参考",f"- baseline_version: {baseline.get('version','unknown')}","","## 四、免责声明","- 本报告由系统自动生成，仅用于业务初筛。","- 结论需由业务、风控、法务人工复核后使用。","- 本报告不构成投资建议、授信决策或法律意见。"]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(description='Complex skill analyzer')
    p.add_argument('--input',required=True)
    p.add_argument('--rules',required=True)
    p.add_argument('--baseline',required=True)
    p.add_argument('--output')
    p.add_argument('--top',type=int,default=15)
    p.add_argument('--title',default='法规匹配助手-家族信托版（T821）')
    a=p.parse_args()
    items=load_items(Path(a.input)); rules=load_json(Path(a.rules)); baseline=load_json(Path(a.baseline))
    pos=rules.get('positive_keywords',[]); neg=rules.get('negative_keywords',[])
    base=int(rules.get('score_base',60))
    rs=[]
    for i,it in enumerate(items, start=1):
        txt=str(it.get('full_text','')) or ' '.join(str(v) for v in it.values())
        ph=hits(txt,pos); nh=hits(txt,neg)
        comp=float(it.get('data_completeness',0) or 0)
        score=base + min(ph*2,10) - min(nh*5,25)
        reasons=[]
        if ph: reasons.append(f'positive_hits={ph}')
        if nh: reasons.append(f'negative_hits={nh}')
        if comp<0.6:
            score -= 8; reasons.append('data_completeness_low')
        elif comp>0.9:
            score += 2; reasons.append('data_completeness_high')
        score=max(0,min(100,score))
        rs.append({'id':it.get('id',f'R{i:03d}'),'score':score,'level':level(score,rules.get('level_cutoffs',{})),'reasons':reasons})
    rep=render(a.title,rs,baseline,a.top)
    if a.output: Path(a.output).write_text(rep,encoding='utf-8')
    else: sys.stdout.write(rep+'\n')

if __name__=='__main__':
    main()
