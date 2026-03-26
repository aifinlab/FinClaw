from __future__ import annotations
from pathlib import Path
from utils import build_corpus, DEFAULT_SOURCES
import argparse

def main():
    parser = argparse.ArgumentParser(description="下载公开法规与公司报告，构建检索语料。")
    parser.add_argument("--data-dir", default="data", help="输出目录")
    args = parser.parse_args()
    corpus_path = build_corpus(Path(args.data_dir), DEFAULT_SOURCES)
    print(f"corpus built: {corpus_path}")

if __name__ == "__main__":
    main()
