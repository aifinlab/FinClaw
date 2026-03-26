from script.fetch_public_data import load_document
from script.locator import locate_passages
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description='Locate clauses in legal texts or company reports')
    parser.add_argument('--source', required=True, help='URL or local file path')
    parser.add_argument('--query', required=True, help='Query text, e.g. 利润分配 回购 关联交易')
    parser.add_argument('--topk', type=int, default=5)
    args = parser.parse_args()

    text = load_document(args.source)
    rows = locate_passages(text, args.query, topk=args.topk)
    print(json.dumps({'query': args.query, 'results': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
