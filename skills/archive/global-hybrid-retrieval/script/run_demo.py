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
    run([sys.executable, str(SCRIPT / "hybrid_retrieval.py"), "--corpus", str(data_dir / "corpus.jsonl"), "--query", '业绩预告 初步测算 具体财务数据为准', "--top-k", "5"])

if __name__ == "__main__":
    main()
