#!/usr/bin/env python3
"""Exercise the validator's actual resource guard in isolation, without gates/network.

The AST loader executes definitions and the one guard expression only. Importing
validate_project.py itself would run unrelated syntax checks and rebuild output.
Literal fixture expectations are independent of the policy implementation.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re


MESSAGE = "dependencia externa de CSS/JS encontrada no index"
CASES = [
    ("anchor_https_navigation", '<a href="https://www.metatrader5.com/pt/download">Windows</a>', False),
    ("anchor_http_navigation", "<a href='http://docs.example.test/help'>Help</a>", False),
    ("anchor_protocol_relative_navigation", '<a href="//docs.example.test/help">Help</a>', False),
    ("anchor_mixed_case_unquoted_navigation", '<A HrEf=HtTpS://docs.example.test/help>Help</A>', False),
    ("local_script_and_stylesheet", '<script src="src/app.js"></script><link rel="stylesheet" href="src/app.css">', False),
    ("local_image", '<img src="assets/logo.png">', False),
    ("remote_resource_tokens_in_comments_are_unsupported", '<!-- <script src="https://cdn.example.test/app.js"></script> -->', True),
    ("resource_markup_in_script_text_is_unsupported", '<script>const example = \'<img src="https://docs.example.test/example.png">\';</script>', True),
    ("external_script", '<script src="https://cdn.example.test/app.js"></script>', True),
    ("external_stylesheet", '<link rel="stylesheet" href="https://cdn.example.test/app.css">', True),
    ("external_image", '<img src="https://cdn.example.test/logo.png">', True),
    ("external_iframe", '<iframe src="https://frames.example.test/view"></iframe>', True),
    ("protocol_relative_script", '<script src="//cdn.example.test/app.js"></script>', True),
    ("protocol_relative_stylesheet", '<link rel="stylesheet" href="//cdn.example.test/app.css">', True),
    ("mixed_case_single_quoted_script", "<ScRiPt SrC='HtTpS://cdn.example.test/app.js'></ScRiPt>", True),
    ("mixed_case_unquoted_iframe", '<IFRAME SrC=HtTp://frames.example.test/view></IFRAME>', True),
    ("entity_encoded_scheme", '<img src="&#104;ttps://cdn.example.test/logo.png">', True),
    ("leading_whitespace", '<img src="  https://cdn.example.test/logo.png  ">', True),
    ("external_base_is_not_navigation", '<base href="https://cdn.example.test/">', True),
    ("anchor_src_is_not_href_navigation", '<a src="https://cdn.example.test/content">Help</a>', True),
    ("svg_xlink_resource", '<svg><use xlink:href="https://cdn.example.test/icons.svg#logo"></use></svg>', True),
    ("mixed_navigation_and_script", '<a href="https://docs.example.test/help">Help</a><script src="https://cdn.example.test/app.js"></script>', True),
    ('tab_inside_https_scheme', '<script src="h&#9;ttps://cdn.example.test/app.js"></script>', True),
    ('lf_between_scheme_and_slashes', '<script src="https:&#10;//cdn.example.test/app.js"></script>', True),
    ('cr_between_scheme_and_slashes', '<link rel="stylesheet" href="https:&#13;//cdn.example.test/app.css">', True),
    ('backslash_https_authority', '<script src="https:\\\\cdn.example.test/app.js"></script>', True),
    ('mixed_slash_protocol_relative', '<script src="/\\cdn.example.test/app.js"></script>', True),
    ('resource_markup_in_textarea_is_unsupported', "<textarea><img src='https://cdn.example.test/example.png'></textarea>", True),
    ('resource_markup_in_title_is_unsupported', "<title><img src='https://cdn.example.test/example.png'></title>", True),
    ('local_fragment', '<a href="#section">Local</a><svg><use href="#icon"></use></svg>', False),
    ('local_query', '<img src="assets/icon.svg?origin=https://docs.example.test/">', False),
    ('external_ampersand_entities', '<script src="&#x2f;&#x2f;cdn.example.test/app.js"></script>', True),
    ('textarea_endtag_with_attribute_then_resource', '<textarea></textarea data-example><script src="https://cdn.example.test/app.js"></script>', True),
    ('title_endtag_with_attribute_then_resource', '<title></title data-example><img src="https://cdn.example.test/logo.png">', True),
    ('script_endtag_with_attribute_then_resource', '<script></script data-example><script src="https://cdn.example.test/app.js"></script>', True),
    ('style_endtag_with_attribute_then_resource', '<style></style data-example><link rel="stylesheet" href="https://cdn.example.test/app.css">', True),
    ('textarea_endtag_with_slash_then_resource', '<textarea></textarea/><script src="https://cdn.example.test/app.js"></script>', True),
    ('script_endtag_with_slash_then_resource', '<script></script/><script src="https://cdn.example.test/app.js"></script>', True),
    ('textarea_selfclosing_start_literal_unsupported', '<textarea/><img src="https://cdn.example.test/example.png"></textarea>', True),
    ('title_selfclosing_start_literal_unsupported', '<title/><img src="https://cdn.example.test/example.png"></title>', True),
    ('ordinary_textarea_end_then_resource', '<textarea>literal</textarea><script src="https://cdn.example.test/app.js"></script>', True),
    ('local_backslash_path', '<img src="assets\\logo.png">', False),
    ('svg_title_html_integration_point', '<svg><title><img src="https://cdn.example.test/logo.png"></title></svg>', True),
    ('textarea_space_after_endtag_opener_is_literal_unsupported', '<textarea></ textarea><img src="https://cdn.example.test/example.png"></textarea>', True),
    ('svg_title_plain_text_local', '<svg><title>A local icon</title><use href="#icon"></use></svg>', False),
    ('resource_markup_in_style_text_is_unsupported', '<style>.example::after{content:\'<img src="https://cdn.example.test/example.png">\';}</style>', True),
    ('script_comment_marker_cannot_hide_later_resource', '<script>const marker="<!--";</script><script src="https://cdn.example.test/app.js"></script>', True),
    ('anchor_title_cannot_hide_legacy_reference', '<a title=\'href="https://cdn.example.test/example"\' href="#local">Local</a>', True),
    ('allowed_anchor_does_not_whitelist_later_resource', '<a href="https://www.metatrader5.com/pt/download">Docs</a><script>const marker="<!--";</script><link rel="stylesheet" href="https://www.metatrader5.com/pt/download">', True),
    ('canonical_anchor_and_local_image', '<a class="help" href="https://docs.example.test/help" target="_blank" rel="noopener">Help</a><img src="assets/icon.png">', False),
    ('href_value_is_not_a_global_resource_exception', '<a href=\'https://docs.example.test/?example=src="https://cdn.example.test/app.js"\'>Docs</a>', True),
    ('canonical_navigation_token_in_script_literal_allowed', '<script>const example = \'<a href="https://docs.example.test/help">Help</a>\';</script>', False),
    ('canonical_navigation_token_in_style_literal_allowed', '<style>.example::after{content:\'<a href="https://docs.example.test/help">Help</a>\';}</style>', False),
    ('canonical_navigation_token_in_textarea_literal_allowed', '<textarea><a href="https://docs.example.test/help">Help</a></textarea>', False),
    ('canonical_navigation_token_in_title_literal_allowed', '<title><a href="https://docs.example.test/help">Help</a></title>', False),
    ('script_comment_marker_singlequoted_resource', '<script>const marker="<!--";</script><script src=\'https://cdn.example.test/app.js\'></script>', True),
    ('script_comment_marker_protocol_relative_resource', '<script>const marker="<!--";</script><script src="//cdn.example.test/app.js"></script>', True),
    ('script_comment_marker_entity_encoded_resource', '<script>const marker="<!--";</script><script src="&#104;ttps://cdn.example.test/app.js"></script>', True),
    ('script_comment_marker_unquoted_resource', '<script>const marker="<!--";</script><script src=https://cdn.example.test/app.js></script>', True),
    ('multiline_canonical_anchor', '<!doctype html>\r\n<a\n class="help"\n href="https://docs.example.test/help"\n target="_blank">Help</a>', False),
    ('canonical_anchor_cannot_hide_earlier_title', '<a title=\'src="https://cdn.example.test/app.js"\' href="https://docs.example.test/help">Help</a>', True),
    ('malformed_adjacent_attribute_no_exception', '<a href="https://docs.example.test/help"src="https://cdn.example.test/app.js">Help</a>', True),
    ('canonical_anchor_cannot_hide_other_element', '<a href="https://docs.example.test/help">Help</a><use xlink:href="https://cdn.example.test/icon.svg#x">', True),
    ('canonical_anchor_with_entities_in_value', '<a href="https://docs.example.test/help?x=1&amp;y=2">Help</a>', False),
    ('local_text_no_remote_tokens', '<script>const example="assets/icon.png";</script><textarea>local</textarea>', False),
    ('closed_js_comment_markers_hide_singlequoted_script', '<script>const begin="<!--";</script><script src=\'https://cdn.example.test/app.js\'></script><script>const end="-->";</script>', True),
    ('closed_js_comment_markers_hide_protocol_relative_script', '<script>const begin="<!--";</script><script src="//cdn.example.test/app.js"></script><script>const end="-->";</script>', True),
    ('closed_js_comment_markers_hide_entity_scheme_script', '<script>const begin="<!--";</script><script src="&#104;ttps://cdn.example.test/app.js"></script><script>const end="-->";</script>', True),
    ('closed_js_comment_markers_hide_unquoted_script', '<script>const begin="<!--";</script><script src=https://cdn.example.test/app.js></script><script>const end="-->";</script>', True),
    ('closed_js_comment_markers_hide_singlequoted_stylesheet', '<script>const begin="<!--";</script><link rel=\'stylesheet\' href=\'https://cdn.example.test/app.css\'><script>const end="-->";</script>', True),
    ('closed_js_comment_markers_doublequoted_absolute_control', '<script>const begin="<!--";</script><script src="https://cdn.example.test/app.js"></script><script>const end="-->";</script>', True),
    ('closed_js_comment_markers_no_remote_resource', '<script>const begin="<!--";</script><p>Local content</p><script>const end="-->";</script>', False),
    ('markers_contained_in_same_script_control', '<script>const markers=["<!--","-->"];</script><script src=\'https://cdn.example.test/app.js\'></script>', True),
    ('earlier_local_singlequoted_token_swallows_real_script', '<script>const begin="<!-- src=\'local";</script><script src=\'https://cdn.example.test/app.js\'></script><script>const end="-->";</script>', True),
    ('earlier_local_singlequoted_token_swallows_real_stylesheet', '<script>const begin="<!-- href=\'local";</script><link rel="stylesheet" href=\'https://cdn.example.test/app.css\'><script>const end="-->";</script>', True),
    ('earlier_local_quoted_token_swallows_protocol_relative_script', '<script>const begin="<!-- src=\'local";</script><script src="//cdn.example.test/app.js"></script><script>const end="--> \'";</script>', True),
    ('earlier_local_quoted_token_swallows_unquoted_script', '<script>const begin="<!-- src=\'local";</script><script src=https://cdn.example.test/app.js></script><script>const end="--> \'";</script>', True),
    ('legacy_doublequoted_absolute_control', '<script>const begin="<!-- src=\'local";</script><script src="https://cdn.example.test/app.js"></script><script>const end="--> \'";</script>', True),
    ('local_token_and_local_resource_control', '<script>const begin="<!-- src=\'local";</script><script src=\'assets/app.js\'></script><script>const end="-->";</script>', False),
    ('canonical_navigation_span_cannot_cross_real_stylesheet', '<script>const a=\'<a href="\';</script><link href=\'https://cdn.test/x.css\'><script>const b=\'">\';</script>', True),
    ('canonical_navigation_span_cannot_cross_protocol_relative_resource', '<script>const a=\'<a href="\';</script><link href=\'//cdn.test/x.css\'><script>const b=\'">\';</script>', True),
    ('canonical_navigation_span_cannot_cross_unquoted_resource', '<script>const a=\'<a href="\';</script><link href=https://cdn.test/x.css><script>const b=\'">\';</script>', True),
    ('encoded_angle_navigation_control', '<a href="https://docs.example.test/?q=%3Cvalue%3E">Docs</a>', False),
]


def guard_from_source(path: Path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    guards = [
        node for node in tree.body if isinstance(node, ast.If)
        and any(isinstance(child, ast.Constant) and child.value == MESSAGE
                for statement in node.body for child in ast.walk(statement))
    ]
    if len(guards) != 1:
        raise AssertionError(f"expected one actual resource guard, found {len(guards)}")
    definitions = [node for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    isolated = ast.Module(body=[
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
        *definitions,
    ], type_ignores=[])
    namespace = {"HTMLParser": HTMLParser, "re": re, "unescape": unescape}
    exec(compile(ast.fix_missing_locations(isolated), str(path), "exec"), namespace)
    expression = compile(ast.Expression(guards[0].test), str(path), "eval")
    return lambda html: bool(eval(expression, {**namespace, "index": html}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validator", type=Path, required=True)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    detector = guard_from_source(args.validator)
    cases = list(CASES)
    if args.index:
        cases.append(("real_index_documentation_navigation", args.index.read_text(encoding="utf-8"), False))
    results = []
    for name, html, expected in cases:
        observed = detector(html)
        results.append({"case": name, "expected_blocked": expected,
                        "observed_blocked": observed, "pass": observed == expected})
    report = {
        "validator": str(args.validator),
        "validator_sha256": hashlib.sha256(args.validator.read_bytes()).hexdigest(),
        "scope": "actual guard expression and definitions only; no full validator, network, browser or rebuild",
        "cases": results,
        "passed": sum(row["pass"] for row in results),
        "total": len(results),
    }
    report["result"] = "PASS" if report["passed"] == report["total"] else "FAIL"
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f'{report["result"]}: {report["passed"]}/{report["total"]} isolated resource-policy cases')
    for row in results:
        if not row["pass"]:
            print(f'FAIL {row["case"]}: expected blocked={row["expected_blocked"]}, observed={row["observed_blocked"]}')
    return int(report["result"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
