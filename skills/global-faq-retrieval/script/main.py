import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import argparse
import json
from script.fetch_public_data import load_document
from script.faq_retriever import search_faq


def main():
    parser = argparse.ArgumentParser(description='FAQ retrieval on public legal/company docs')
    parser.add_argument('--source', required=True)
    parser.add_argument('--question', required=True)
    parser.add_argument('--topk', type=int, default=5)
    args = parser.parse_args()

    text = load_document(args.source)
    rows = search_faq(text, args.question, topk=args.topk)
    print(json.dumps({'question': args.question, 'results': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
