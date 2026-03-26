from __future__ import annotations
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve().parent

def run(cmd):
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    data_dir = ROOT / "data"
    run([sys.executable, str(SCRIPT / "fetch_public_data.py"), "--data-dir", str(data_dir)])
    run([sys.executable, str(SCRIPT / "citation_traceback.py"), "--corpus", str(data_dir / "corpus.jsonl"), "--claim", '公司半年度报告应当真实、准确、完整，不得有虚假记载、误导性陈述或者重大遗漏。', "--top-k", "5"])

if __name__ == "__main__":
    main()
