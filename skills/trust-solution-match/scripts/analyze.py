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

def hits(text:str, kws:List[str])->int:
    c=0
    for kw in kws:
        c += len(re.findall(re.escape(kw), text, flags=re.IGNORECASE))
    return c

def main():
    p=argparse.ArgumentParser(description='Skill analyzer')
    p.add_argument('--input', required=True)
    p.add_argument('--output')
    p.add_argument('--top', type=int, default=15)
    p.add_argument('--title', default='Skill Report')
    p.add_argument('--positive', default='支持,改善,完成,稳定,提升')
    p.add_argument('--negative', default='风险,处罚,违约,逾期,异常')
    a=p.parse_args()

    items=load_items(Path(a.input))
    pos=[x.strip() for x in a.positive.split(',') if x.strip()]
    neg=[x.strip() for x in a.negative.split(',') if x.strip()]
    rows=[]
    for i,it in enumerate(items,start=1):
        text=' '.join(str(v) for v in it.values())
        ph=hits(text,pos); nh=hits(text,neg)
        score=max(0,min(100,60+ph*4-nh*6))
        level='high' if score<45 else 'medium' if score<70 else 'low'
        rows.append({'id':it.get('id',f'R{i:03d}'),'score':score,'level':level,'ph':ph,'nh':nh})

    c=Counter(x['level'] for x in rows)
    lines=[f"# {a.title}",'','## 一、概览',f"- 样本数: {len(rows)}",f"- low: {c.get('low',0)}",f"- medium: {c.get('medium',0)}",f"- high: {c.get('high',0)}",'','## 二、重点条目']
    for x in sorted(rows,key=lambda z:z['score'])[:a.top]:
        lines.append(f"- {x['id']} | score={x['score']} | level={x['level']} | pos_hits={x['ph']} | neg_hits={x['nh']}")
    lines += ['','## 三、免责声明','- 本报告由系统自动生成，仅用于业务初筛。','- 结论需由业务、风控、法务人工复核后使用。','- 本报告不构成投资建议、授信决策或法律意见。']
    rep='
'.join(lines)

    if a.output:
        Path(a.output).write_text(rep,encoding='utf-8')
    else:
        sys.stdout.write(rep+'
')

if __name__=='__main__':
    main()
