import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import argparse
import json
from script.fetch_public_data import load_document
from script.product_knowledge import search_product_knowledge


def main():
    parser = argparse.ArgumentParser(description='Retrieve product knowledge from public docs')
    parser.add_argument('--source', required=True, help='URL or local file path')
    parser.add_argument('--query', required=True, help='Product query text')
    parser.add_argument('--topk', type=int, default=5)
    args = parser.parse_args()

    text = load_document(args.source)
    rows = search_product_knowledge(text, args.query, topk=args.topk)
    print(json.dumps({'query': args.query, 'results': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
