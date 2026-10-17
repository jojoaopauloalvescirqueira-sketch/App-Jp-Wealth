"""Consolida declarações de leitura sem promover extração ou amostra a leitura.

Produz anexos de pesquisa; não é o checker somente leitura do harness.
Os adaptadores são explícitos para os ledgers desta revisão.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re


def ranges(numbers):
    result = []
    for number in sorted(set(numbers)):
        if result and number == result[-1][1] + 1:
            result[-1][1] = number
        else:
            result.append([number, number])
    return result


def expand(intervals):
    return {p for a, b in intervals for p in range(a, b+1)}


def printed_page(book, text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    if book == 'REF':
        found = re.match(r'^(\d+)\b', lines[0])
    else:
        found = re.fullmatch(r'(\d+)', lines[-1])
    return int(found[1]) if found else None


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument('--corpus', type=Path, required=True)
    args = cli.parse_args()
    root = args.root.resolve()
    research = root/'research'
    read = {b: set() for b in ('REF', 'TRD', 'NN')}
    evidence = []

    def record(name, book, pages, note=''):
        path = research/name
        if not path.exists():
            return
        pages = set(pages)
        read[book].update(pages)
        evidence.append({'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'book': book, 'full_text_page_ranges': ranges(pages), 'note': note})

    def load(name):
        path = research/name
        return json.loads(path.read_text()) if path.exists() else {}

    d = load('engineering-coverage.json')
    for book in d.get('books', []):
        record('engineering-coverage.json', book['book'],
               expand(book['full_text_page_ranges_reviewed']))
    for name in ('nn-deep-coverage.json', 'root-frontmatter-coverage.json'):
        d = load(name)
        record(name, 'NN', expand(d.get('full_text_page_ranges', [])))
    record('nn-layers-coverage.json', 'NN', load('nn-layers-coverage.json').get('full_pages', []))
    record('nn-final-coverage.json', 'NN', load('nn-final-coverage.json').get('read_pages', []))
    record('trd-semantic-coverage.json', 'TRD',
           expand(load('trd-semantic-coverage.json').get('actual_read_page_intervals', [])))
    record('trd-common-coverage.json', 'TRD',
           expand(load('trd-common-coverage.json').get('actually_read_unique_pdf_intervals', [])))
    d = load('trd-files-coverage.json')
    record('trd-files-coverage.json', 'TRD', set(d.get('read_unique_pages', [])) |
           set(d.get('additional_part5', {}).get('read_pages', [])))
    # Future reader adapters must use the actual full-text page field; no section-length inference.
    extra_names = ['trd-chart-coverage.json', 'trd-trading-coverage.json', 'trd-final-coverage.json',
                   'trd-ui-finish-coverage.json', 'trd-extensions-coverage.json',
                   'reference-deep-coverage.json']
    extra_names += [p.name for p in sorted(research.glob('reference-batch-*-coverage.json'))]
    for name in extra_names:
        d = load(name)
        if d:
            if 'consolidation_full_text_pages' not in d:
                raise ValueError(f'{name}: add explicit consolidation_full_text_pages; no guessed adapter')
            record(name, d['book'], d['consolidation_full_text_pages'])

    manifest = load('source-manifest.json')
    by_book = {s['id']: s for s in manifest['sources']}
    summary = {'schema': 'stoikus-coverage-union/1',
               'method': 'Union of explicitly declared full-text pages, no propagation from family openings',
               'independent_full_source_audit': False,
               'native_status': 'NOT_RUN', 'evidence': evidence, 'books': {}}
    for book, source in by_book.items():
        pages = source['pages']
        if any(p < 1 or p > pages for p in read[book]):
            raise ValueError('Page outside source bounds')
        missing = set(range(1, pages+1)) - read[book]
        summary['books'][book] = {'pages': pages, 'extracted': pages,
                                 'full_text_read_unique': len(read[book]),
                                 'full_text_read_ranges': ranges(read[book]),
                                 'pending_full_text_ranges': ranges(missing),
                                 'textual_body_coverage': 'COMPLETE' if not missing else 'PARTIAL',
                                 'visual_and_executable_verification': 'SEPARATE_NOT_IMPLIED'}
    summary['corpus_semantic_status'] = ('COMPLETE_TEXTUAL_DECLARATIONS' if all(
        len(read[b]) == by_book[b]['pages'] for b in by_book) else 'PARTIAL')
    (research/'coverage-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')

    with (research/'coverage-matrix.jsonl').open('w') as out:
        for line in (research/'section-catalog.jsonl').read_text().splitlines():
            row = json.loads(line)
            book = row['book']
            span = set(range(row['start'], row['end']+1))
            present = span & read[book]
            row.update(full_text_pages_read=len(present), full_text_pages_total=len(span),
                       full_text_range_status='COMPLETE' if present == span else 'PARTIAL' if present else 'PENDING',
                       pending_full_text_ranges=ranges(span-present),
                       semantic_notes='See individual reader notes; page union is not independent re-review',
                       visual_review='SEE_DIRECTED_VISUAL_RECEIPT', executable_examples='NOT_RUN')
            out.write(json.dumps(row, ensure_ascii=False)+'\n')

    # Page hashes and counts only: never redistribute the extracted copyrighted text in the kit.
    pagination = {b: {'equal':0, 'different':[], 'unknown':[]} for b in by_book}
    with (research/'page-inventory.jsonl.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as gz:
            for book in by_book:
                count = 0
                with (args.corpus/book/'pages.jsonl').open() as pages:
                    for line in pages:
                        page = json.loads(line)
                        printed = printed_page(book, page['text'])
                        if printed is None:
                            pagination[book]['unknown'].append(page['page'])
                        elif printed == page['page']:
                            pagination[book]['equal'] += 1
                        else:
                            pagination[book]['different'].append({'physical':page['page'],'printed':printed})
                        row = {'book': book, 'physical_page': page['page'],
                               'printed_page_extracted': printed,
                               'printed_page_method': 'REF first-line number; TRD/NN last-line number; not visual proof',
                               'text_sha256': page['sha256'], 'characters': page['characters'],
                               'extraction_error': page['error'],
                               'declared_full_text_read': page['page'] in read[book]}
                        gz.write((json.dumps(row, ensure_ascii=False)+'\n').encode())
                        count += 1
                if count != by_book[book]['pages']:
                    raise ValueError('Incomplete extraction inventory')
    (research/'pagination-map.json').write_text(json.dumps(pagination,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({b: d['full_text_read_unique'] for b, d in summary['books'].items()}))


if __name__ == '__main__':
    main()
