from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve().parent

def run(cmd):
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    data_dir = ROOT / "data"
    run([sys.executable, str(SCRIPT / "fetch_public_data.py"), "--data-dir", str(data_dir)])
    run([sys.executable, str(SCRIPT / "keyword_retrieval.py"), "--corpus", str(data_dir / "corpus.jsonl"), "--query", '风险 信息披露', "--top-k", "5"])

if __name__ == "__main__":
    main()
