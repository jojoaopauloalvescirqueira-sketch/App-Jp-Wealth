"""Lossless semantic extraction for the manuscript's limited Mermaid dialect.

The three layouts are deliberate document figures. Unsupported syntax or a
changed topology is refused, so a later edit cannot silently lose a branch.
"""
from pathlib import Path
import hashlib
import json
import math
import re
from PIL import Image, ImageDraw, ImageFont

IDENT = r'(?:\[\*\]|[A-Za-z][A-Za-z0-9_]*)'
NODE = IDENT + r'(?:\[[^\]]+\]|\{[^}]+\})?'
EDGE = re.compile(r'^\s*(' + NODE + r')\s*-->\s*(?:\|([^|]+)\|\s*)?('
                  + NODE + r')(?:\s*:\s*(.+))?\s*$')
NODE_PARTS = re.compile(r'^(' + IDENT + r')(?:\[([^\]]+)\]|\{([^}]+)\})?$')

def parse_graph(body):
    nodes = {}; edges = []; dialect = None
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if dialect is None:
            if line not in ('flowchart LR', 'stateDiagram-v2'):
                raise ValueError('Unsupported graph dialect: ' + line)
            dialect = line
            continue
        match = EDGE.fullmatch(line)
        if not match:
            raise ValueError('Unparsed graph statement: ' + line)
        a, pipe, b, colon = match.groups()
        if pipe and colon:
            raise ValueError('Two competing edge labels: ' + line)
        ids = []
        for token in (a, b):
            key, rectangle, decision = NODE_PARTS.fullmatch(token).groups()
            label = rectangle or decision or key
            node = {'label':label, 'shape':'decision' if decision else
                    ('initial' if key == '[*]' else 'box')}
            if key in nodes and (rectangle or decision) and nodes[key]['label'] != key and nodes[key] != node:
                raise ValueError('Conflicting node definition: ' + key)
            if key not in nodes or rectangle or decision:
                nodes[key] = node
            ids.append(key)
        edges.append({'from':ids[0], 'to':ids[1], 'label':pipe or colon or ''})
    if not edges:
        raise ValueError('Empty graph')
    return {'dialect':dialect, 'nodes':nodes, 'edges':edges,
            'source_sha256':hashlib.sha256(body.encode()).hexdigest()}

def render_graph(body, number, output, font_path):
    graph = parse_graph(body)
    output = Path(output)
    font = ImageFont.truetype(str(font_path), 32)
    small = ImageFont.truetype(str(font_path), 30)
    ink = '#172333'; line = '#59718b'; fill = '#edf2f7'
    size = (1500, 720) if number == 1 else ((1500, 850) if number == 2 else (1500, 690))
    im = Image.new('RGB', size, 'white'); d = ImageDraw.Draw(im)

    def lines(text, width, selected=font):
        result = []; current = ''
        for word in text.split():
            proposed = (current + ' ' + word).strip()
            if d.textlength(proposed, font=selected) > width and current:
                result.append(current); current = word
            else:
                current = proposed
            if d.textlength(current, font=selected) > width:
                raise ValueError('Unbreakable text overflows figure: ' + current)
        return result + ([current] if current else [])

    def text_box(text, box, selected=font):
        x, y, w, h = box
        wrapped = lines(text, w-32, selected)
        step = selected.size + 7
        if len(wrapped)*step > h-18:
            raise ValueError('Text exceeds figure box: ' + text)
        yy = y + (h-len(wrapped)*step)/2
        for part in wrapped:
            d.text((x+16, yy), part, font=selected, fill=ink)
            yy += step

    def box(key, coords):
        x, y, w, h = coords
        d.rounded_rectangle((x,y,x+w,y+h), radius=12, fill=fill, outline=line, width=3)
        text_box(graph['nodes'][key]['label'], coords)

    def arrow(points):
        d.line(points, fill=line, width=4)
        end = points[-1]; previous = next(p for p in reversed(points[:-1]) if p != end)
        angle = math.atan2(end[1]-previous[1], end[0]-previous[0])
        tip = [end, (end[0]-15*math.cos(angle)+8*math.sin(angle), end[1]-15*math.sin(angle)-8*math.cos(angle)),
               (end[0]-15*math.cos(angle)-8*math.sin(angle), end[1]-15*math.sin(angle)+8*math.cos(angle))]
        d.polygon(tip, fill=line)

    pairs = [(e['from'], e['to']) for e in graph['edges']]
    if number == 1:
        expected = [('T','A'),('A','O'),('O','D'),('D','P'),('P','C'),('G','E'),('E','P')]
        if pairs != expected or any(e['label'] for e in graph['edges']):
            raise ValueError('Architecture topology changed; revise the layout')
        positions = {'T':(20,25,440,140), 'A':(530,25,440,140), 'O':(1040,25,440,140),
                     'D':(1040,275,440,140), 'P':(530,275,440,140), 'C':(20,275,440,140),
                     'G':(1040,535,440,140), 'E':(530,535,440,140)}
        routes = [[(460,95),(530,95)],[(970,95),(1040,95)],[(1260,165),(1260,275)],
                  [(1040,345),(970,345)],[(530,345),(460,345)],[(1040,605),(970,605)],
                  [(750,535),(750,415)]]
        for key, coords in positions.items(): box(key, coords)
        for route in routes: arrow(route)
    elif number == 2:
        if graph['dialect'] != 'stateDiagram-v2' or len(graph['edges']) != 9:
            raise ValueError('State graph changed; review transition table pagination')
        # A complete transition table avoids ambiguous crossed arrows and makes
        # the self-loop explicit. Each source edge is represented once, in order.
        xs = [20,345,670,1480]; y0 = 20; header = 70; row = 76
        d.rectangle((20,y0,1480,y0+header),fill=fill,outline=line,width=3)
        for n, label in enumerate(('Origem','Destino','Condição / motivo')):
            text_box(label,(xs[n],y0,xs[n+1]-xs[n],header),small)
        for i, edge in enumerate(graph['edges']):
            y = y0+header+i*row
            d.rectangle((20,y,1480,y+row), fill='white' if i%2 else '#f7f9fb', outline=line, width=1)
            for n, value in enumerate((edge['from'],edge['to'],edge['label'] or '—')):
                text_box(value,(xs[n],y,xs[n+1]-xs[n],row),small)
        for x in xs[1:-1]:d.line([(x,y0),(x,y0+header+9*row)],fill=line,width=1)
        d.text((25,800),'[*] indica o início. Origem igual ao destino indica continuidade no mesmo estado.',font=small,fill=ink)
    elif number == 3:
        if pairs != [('A','B'),('B','C'),('C','D'),('D','E'),('D','F')] or graph['nodes']['D']['shape'] != 'decision' or [e['label'] for e in graph['edges']] != ['','','','sim','não']:
            raise ValueError('Publication decision changed; revise layout')
        positions = {'A':(20,20,400,140),'B':(550,20,400,140),'C':(1080,20,400,140),
                     'E':(550,510,400,140),'F':(1080,510,400,140)}
        for key, coords in positions.items(): box(key,coords)
        d.polygon([(1280,245),(1450,335),(1280,425),(1110,335)],fill=fill,outline=line,width=3)
        text_box(graph['nodes']['D']['label'],(1150,296,260,75),small)
        for route in [[(420,90),(550,90)],[(950,90),(1080,90)],[(1280,160),(1280,245)],
                      [(1110,335),(750,335),(750,510)],[(1280,425),(1280,510)]]:arrow(route)
        d.text((895,290),'sim',font=font,fill=ink)
        d.text((1300,450),'não',font=font,fill=ink)
    else:
        raise ValueError('Unreviewed figure number')
    path = output/f'diagram-{number}.png'
    im.save(path)
    (output/f'diagram-{number}-semantics.json').write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n')
    return path
