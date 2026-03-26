from script.fetch_public_data import load_document
from script.rule_retriever import search_rules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description='Retrieve policy/rule passages from public docs')
    parser.add_argument('--source', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--topk', type=int, default=5)
    args = parser.parse_args()

    text = load_document(args.source)
    rows = search_rules(text, args.query, topk=args.topk)
    print(json.dumps({'query': args.query, 'results': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
