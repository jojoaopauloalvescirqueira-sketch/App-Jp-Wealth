"""Regressions for the three actual manuscript graphs, not general Mermaid."""
from pathlib import Path
import re
import unittest
from render_diagrams import parse_graph

ROOT = Path(__file__).resolve().parents[1]

class Diagrams(unittest.TestCase):
    def graphs(self):
        return [parse_graph(body) for path in sorted((ROOT/'chapters').glob('*.md'))
                for body in re.findall(r'```mermaid\n(.*?)```', path.read_text(), re.S)]

    def test_all_actual_graphs_are_lossless(self):
        a, b, c = self.graphs()
        self.assertEqual(len(a['nodes']), 8)
        self.assertEqual(len(a['edges']), 7)
        self.assertEqual(len(b['edges']), 9)
        self.assertIn({'from':'[*]', 'to':'Espera', 'label':''}, b['edges'])
        self.assertIn({'from':'Auditando', 'to':'Auditando', 'label':'próxima fatia'}, b['edges'])
        self.assertEqual(sum(bool(e['label']) for e in b['edges']), 8)
        self.assertEqual(c['nodes']['D'], {'label':'Concluído?', 'shape':'decision'})
        self.assertEqual(len(c['edges']), 5)
        self.assertIn({'from':'D', 'to':'E', 'label':'sim'}, c['edges'])
        self.assertIn({'from':'D', 'to':'F', 'label':'não'}, c['edges'])

    def test_unknown_syntax_is_refused(self):
        with self.assertRaises(ValueError):
            parse_graph('flowchart LR\nA -.-> B')

    def test_conflicting_node_labels_are_refused(self):
        with self.assertRaises(ValueError):
            parse_graph('flowchart LR\nA[um] --> B\nA[dois] --> C')

if __name__ == '__main__':
    unittest.main()
