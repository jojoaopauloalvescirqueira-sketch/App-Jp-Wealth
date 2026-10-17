"""Read-only Markdown/DOCX/PDF structural comparison, not visual/native acceptance.

Requires pypdf and pdfplumber for PDF inspection, separately from the stdlib harness.
Writes JSON to stdout only. Pass the exact rendered PDF with --pdf.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pypdf import PdfReader
import pdfplumber


def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text) if c.isalnum())


def segments(md):
    # Preserve prose order while testing figures and display math separately.
    md = re.sub(r'```[^\n]*\n.*?```', '', md, flags=re.S)
    md = re.sub(r'(?m)^\$\$\s*$.*?^\$\$\s*$', '', md, flags=re.S | re.M)
    md = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', md)
    for block in re.split(r'\n\s*\n', md):
        block = re.sub(r'(?m)^#{1,6}\s+|^[-*]\s+|^\d+\.\s+', '', block)
        if block.strip():
            yield norm(block)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument('--pdf', type=Path, required=True)
    args = cli.parse_args()
    root = args.root.resolve()
    mdpath = root/'MANUAL.md'
    docpath = root/'publication/Stoikus_Engenharia_MQL5_Manual.docx'
    md = mdpath.read_text()
    with zipfile.ZipFile(docpath) as z:
        badzip = z.testzip()
        document = ET.fromstring(z.read('word/document.xml'))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
              'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
        text = ''.join(e.text or '' for e in document.iter() if e.tag in (
            '{'+ns['w']+'}t', '{'+ns['m']+'}t'))
        equations = len(document.findall('.//m:oMathPara', ns))
        allmath = len(document.findall('.//m:oMath', ns))
        images = len([n for n in z.namelist() if n.startswith('word/media/')])
    expected_equations = len(re.findall(r'(?m)^\$\$\s*$', md))//2
    expected_figures = len(re.findall(r'(?m)^```mermaid\s*$', md))
    expected = list(segments(md))
    docnorm = norm(text)
    missing_docx = [i+1 for i, p in enumerate(expected) if p not in docnorm]
    reader = PdfReader(args.pdf)
    # PDF stream order places repeated header/footer between split paragraphs.
    # Exclude only the exact known header and page-number lines, not body text.
    header = norm('JP Wealth | Stoikus | Engenharia em MQL5')
    pdftext = '\n'.join(line for page in reader.pages for line in page.extract_text().splitlines()
                        if norm(line) != header and not re.fullmatch(r'Página\s*\d+', line.strip()))
    pdfnorm = norm(pdftext)
    missing_pdf = [i+1 for i, p in enumerate(expected) if p not in pdfnorm]
    bounds = []
    with pdfplumber.open(args.pdf) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            outside = [c for c in page.chars if c['x0'] < -1 or c['x1'] > page.width+1
                       or c['top'] < -1 or c['bottom'] > page.height+1]
            if outside:
                bounds.append({'page': number, 'characters_outside_page': len(outside)})
    result = {
        'schema': 'stoikus-publication-structure/1',
        'hashes': {str(p.relative_to(root)) if p.is_relative_to(root) else p.name:
                   hashlib.sha256(p.read_bytes()).hexdigest() for p in (mdpath, docpath, args.pdf)},
        'prose_segments_checked': len(expected), 'missing_docx_segments': missing_docx,
        'missing_pdf_segments': missing_pdf, 'docx_zip_error': badzip,
        'display_equations_expected': expected_equations, 'native_OMML_paragraphs': equations,
        'native_math_objects_total': allmath, 'figures_expected': expected_figures,
        'docx_embedded_images': images, 'pdf_pages': len(reader.pages),
        'characters_outside_pdf_pages': bounds,
        'visual_inspection': 'SEPARATE_RECEIPT_REQUIRED',
        'MS_Word_native_reopen': 'NOT_RUN', 'MQL5_MT5': 'NOT_RUN',
        'limits': 'Alphanumeric-normalized prose presence; not equation equivalence, figure meaning, reading quality or runtime proof.'
    }
    passed = not any((badzip, missing_docx, missing_pdf, bounds)) and equations == expected_equations and images == expected_figures
    result['structural_result'] = 'PASS' if passed else 'REVIEW_REQUIRED'
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
