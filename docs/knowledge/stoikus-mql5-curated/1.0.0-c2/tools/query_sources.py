"""Consulta local do catálogo e das próprias notas, sem rede ou escrita.

Exemplo: python3 -B tools/query_sources.py OnInit --book REF
O resultado localiza evidência; não confere o contrato da API nem executa MQL5.
"""
import argparse
import json
from pathlib import Path

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('query')
    cli.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    cli.add_argument('--book',choices=['REF','TRD','NN'])
    cli.add_argument('--limit',type=int,default=20)
    args=cli.parse_args()
    research=args.root.resolve()/'research'
    query=args.query.casefold()
    records=[]
    with (research/'coverage-matrix.jsonl').open() as source:
        for raw in source:
            row=json.loads(raw)
            if (not args.book or row['book']==args.book) and (query in row['title'].casefold() or query==row['id'].casefold()):
                records.append(row)
    hits=[]
    for path in sorted(research.glob('*review.md')):
        for number,line in enumerate(path.read_text().splitlines(),1):
            if query in line.casefold():
                hits.append({'path':str(path.relative_to(args.root.resolve())),'line':number,'excerpt':line[:500]})
    print(json.dumps({'catalog_matches':len(records),'catalog':records[:max(0,args.limit)],
                      'own_note_hits':len(hits),'notes':hits[:max(0,args.limit)],
                      'limit':'Text matches only; a parent section does not certify descendants. Read the cited original and the reader scope.'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
