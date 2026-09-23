#!/usr/bin/env python3
"""Validate sidecar-v3 delivery with explicit per-server source scope.

Revision 5 keeps frozen-app, alternate-build, fixture, and unknown-root
evidence separate. It never treats an alternate source mismatch against the
frozen application as a product or transport failure. It also never discards
failures from fixtures, background cache, or observer body collection.

This is an external receipt, not a replacement for a canonical test, quality
gate, or product assertion. Its positive result covers observable local script
delivery and server cleanup only. In particular, server and browser request
IDs are generated independently; matching them by path/port is aggregate,
not packet-level proof that a particular browser received particular bytes.
Every observed loopback JavaScript response must expose a body whose length
and SHA-256 equal its evidenced source. The script tags from the corresponding
index must appear once per main-document navigation. HTTP 304 is conditional
server revalidation, not a substitute for checking the browser's body.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit


LOOPBACK = {"127.0.0.1", "localhost", "::1"}
SERVER_ERRORS = {
    "server_bind_error", "server_handler_error", "server_request_error",
    "server_headers_error", "server_copy_error", "server_loop_error",
}
BROWSER_EVENTS = {
    "browser_request", "browser_response", "browser_request_finished",
    "browser_request_failed", "browser_js_body", "browser_js_body_error",
    "browser_index_body", "browser_index_body_error",
}
SERVER_REQUEST_EVENTS = {
    "server_request", "server_status", "server_headers_done",
    "server_copy_start", "server_copy_done", "server_copy_error",
}
MAX_ISSUE_EXAMPLES = 50


class _ScriptTags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)


def _local_js_url(value):
    """Return (port, decoded path), or None for non-loopback/non-JS URLs."""
    try:
        parts = urlsplit(value)
        if parts.scheme not in ("http", "https") or parts.hostname not in LOOPBACK:
            return None
        if not unquote(parts.path).lower().endswith(".js"):
            return None
        return parts.port, unquote(parts.path)
    except (TypeError, ValueError):
        return None


def _server_js_path(value):
    try:
        path = unquote(urlsplit(value).path)
        return path if path.lower().endswith(".js") else None
    except (TypeError, ValueError):
        return None


def _source(root, url_path):
    """Map an HTTP path to a source, rejecting traversal and symlink escape."""
    if not isinstance(url_path, str) or not url_path.startswith("/"):
        return None, None
    candidate = (root / url_path.lstrip("/")).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        return None, None
    return candidate, relative.as_posix()


def _within(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except (TypeError, ValueError, OSError):
        return False


class Report:
    def __init__(self, trace, root):
        self.trace = trace
        self.root = root.resolve()
        self.counts = Counter()
        self.issue_counts = Counter()
        self.issues = []
        self.has_fail = False
        self.has_incomplete = False
        self.has_runtime = False
        self.source_hashes = {}
        self.scope_counts = Counter()
        self.scope_issues = defaultdict(Counter)
        self.scope_severities = defaultdict(Counter)

    def issue(self, severity, code, **details):
        scope = details.pop("scope", "GLOBAL")
        self.issue_counts[code] += 1
        self.scope_issues[scope][code] += 1
        self.scope_severities[scope][severity] += 1
        self.has_fail |= severity == "fail"
        self.has_incomplete |= severity == "incomplete"
        self.has_runtime |= severity == "runtime"
        if len(self.issues) < MAX_ISSUE_EXAMPLES:
            self.issues.append({"severity": severity, "code": code,
                                "scope": scope, **details})

    def expected_source(self, path, root=None, scope="UNKNOWN", fallback=None):
        if root is None:
            self.issue("incomplete", "SOURCE_ROOT_UNOBSERVED", scope=scope,
                       path=path)
            return None, None
        root = Path(root).resolve()
        source, relative = _source(root, path)
        if source is None:
            self.issue("fail", "SOURCE_PATH_OUTSIDE_ROOT", scope=scope,
                       root=str(root), path=path)
            return None, relative
        if not source.is_file():
            if fallback is not None and scope != "FROZEN_APP":
                self.scope_counts[f"{scope}:source_from_server_copy_only"] += 1
                return fallback, relative
            self.issue("incomplete", "SOURCE_MISSING", scope=scope,
                       root=str(root), path=path, relative=relative)
            return None, relative
        cache_key = (str(root), relative)
        if cache_key not in self.source_hashes:
            digest = hashlib.sha256()
            length = 0
            try:
                with source.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        length += len(chunk)
                        digest.update(chunk)
            except OSError as exc:
                self.issue("incomplete", "SOURCE_UNREADABLE", scope=scope,
                           root=str(root), path=path,
                           relative=relative, error=str(exc))
                return None, relative
            self.source_hashes[cache_key] = (length, digest.hexdigest())
        return self.source_hashes[cache_key], relative

    def expected_file(self, filename, scope="UNKNOWN", fallback=None):
        """Check the actual opened file, including custom-handler paths."""
        if not isinstance(filename, str) or not Path(filename).is_absolute():
            self.issue("incomplete", "SOURCE_FILE_PROVENANCE_MISSING",
                       scope=scope, source_path=filename)
            return None
        source = Path(filename).resolve()
        if not source.is_file():
            if fallback is not None and scope != "FROZEN_APP":
                self.scope_counts[f"{scope}:source_from_server_copy_only"] += 1
                return fallback
            self.issue("incomplete", "SOURCE_FILE_UNAVAILABLE", scope=scope,
                       source_path=str(source))
            return None
        cache_key = (str(source), "ACTUAL_FILE")
        if cache_key not in self.source_hashes:
            digest = hashlib.sha256()
            length = 0
            try:
                with source.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        length += len(chunk)
                        digest.update(chunk)
            except OSError as exc:
                self.issue("incomplete", "SOURCE_FILE_UNREADABLE", scope=scope,
                           source_path=str(source), error=str(exc))
                return None
            self.source_hashes[cache_key] = (length, digest.hexdigest())
        observed = self.source_hashes[cache_key]
        if fallback is not None and observed != fallback and scope != "FROZEN_APP":
            # A temporary test root can be changed or removed after the
            # response. Its later bytes are not evidence of the bytes served.
            self.issue("incomplete", "SOURCE_CHANGED_AFTER_CAPTURE", scope=scope,
                       source_path=str(source), current_length=observed[0],
                       current_sha256=observed[1], served_length=fallback[0],
                       served_sha256=fallback[1])
            return fallback
        return observed

    def as_dict(self, **fields):
        classification = ("INFRA_FAIL" if self.has_fail else
                          "OBSERVABILITY_INCOMPLETE" if self.has_incomplete else
                          "INFRA_OK")
        overall = (classification if classification != "INFRA_OK" else
                   "PRODUCT_ERROR_CANDIDATE" if self.has_runtime else
                   "INFRA_OK")
        known_scopes = set(self.scope_severities)
        known_scopes.update(key.split(":", 1)[0] for key in self.scope_counts)
        scope_classifications = {scope: (
            "INFRA_FAIL" if self.scope_severities[scope]["fail"] else
            "OBSERVABILITY_INCOMPLETE" if self.scope_severities[scope]["incomplete"] else
            "PRODUCT_ERROR_CANDIDATE" if self.scope_severities[scope]["runtime"] else
            "INFRA_OK") for scope in sorted(known_scopes)}
        return {
            "schema_version": 5,
            "classification": classification,
            "overall_verdict": overall,
            "runtime_classification": (
                "PRODUCT_ERROR_CANDIDATE" if self.has_runtime and
                classification == "INFRA_OK" else
                "RUNTIME_ERROR_CAUSE_UNRESOLVED" if self.has_runtime else
                "NO_OBSERVED_APP_RUNTIME_ERROR"),
            "classification_scope": (
                "External observation of local JS delivery, page errors, and "
                "server lifecycle; canonical test/gate verdict remains separate."
            ),
            "trace": str(self.trace),
            "frozen_source_root": str(self.root),
            "counts": dict(sorted(self.counts.items())),
            "issue_counts": dict(sorted(self.issue_counts.items())),
            "issue_examples": self.issues,
            "issue_examples_truncated": sum(self.issue_counts.values()) > len(self.issues),
            "scope_counts": dict(sorted(self.scope_counts.items())),
            "scope_issue_counts": {scope: dict(sorted(c.items())) for scope, c in
                                   sorted(self.scope_issues.items())},
            "scope_classifications": scope_classifications,
            "frozen_app_classification": scope_classifications.get(
                "FROZEN_APP", "NOT_OBSERVED"),
            "correlation_limit": (
                "Browser and server IDs have no common token. Each browser "
                "JavaScript request is instead verified by its own body hash "
                "and length against the scoped source, including cache and "
                "service-worker responses. Server 304 is accepted only with a "
                "logged conditional header. Browser 304 has no accessible body "
                "and is labeled cache continuity inferred only after a prior "
                "same-partition verified 2xx, unchanged source, and no intervening "
                "2xx. Matching server 304 by path/time is aggregate corroboration, "
                "not a shared request ID or proof of background cache provenance."
            ),
            **fields,
        }


def validate(trace, root):
    report = Report(trace, root)
    pids = set()
    sidecars = defaultdict(list)
    servers = defaultdict(lambda: defaultdict(list))
    server_requests = defaultdict(lambda: defaultdict(list))
    browser_requests = defaultdict(lambda: defaultdict(list))
    browser_launches = defaultdict(list)
    page_errors = []
    server_error_events = []
    main_navigations = []
    main_loads = []
    load_symbols = []
    load_symbol_errors = []
    pages = Counter()

    try:
        handle = trace.open("rb")
    except OSError as exc:
        report.issue("incomplete", "TRACE_UNREADABLE", error=str(exc))
        return report.as_dict(pids=[], applicability="UNKNOWN")

    with handle:
        for line_no, raw_line in enumerate(handle, 1):
            report.counts["lines"] += 1
            if not raw_line.endswith(b"\n"):
                report.issue("incomplete", "JSONL_LINE_UNTERMINATED", line=line_no)
            try:
                event = json.loads(raw_line.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                report.issue("incomplete", "JSONL_INVALID", line=line_no, error=str(exc))
                continue
            if not isinstance(event, dict) or not isinstance(event.get("event"), str) or \
                    not isinstance(event.get("pid"), int):
                report.issue("incomplete", "EVENT_SCHEMA_INVALID", line=line_no)
                continue
            kind = event["event"]
            pid = event["pid"]
            pids.add(pid)
            if not isinstance(event.get("time_ns"), int) or \
                    not isinstance(event.get("monotonic_ns"), int) or \
                    not isinstance(event.get("mode"), str):
                report.issue("incomplete", "EVENT_CLOCK_OR_MODE_MISSING",
                             pid=pid, line=line_no, event=kind)
            report.counts["valid_events"] += 1
            report.counts["event_" + kind] += 1
            if kind == "sidecar_enabled":
                sidecars[pid].append(event)
            elif kind in ("server_created", "server_shutdown", "server_closed",
                          "server_loop_start", "server_loop_end"):
                server_id = event.get("server_id")
                if not server_id:
                    report.issue("incomplete", "SERVER_ID_MISSING", pid=pid, line=line_no)
                else:
                    servers[(pid, server_id)][kind].append(event)
            elif kind in SERVER_ERRORS:
                server_error_events.append(event)
                if kind in SERVER_REQUEST_EVENTS:
                    request_id = event.get("request_id")
                    if request_id:
                        server_requests[(pid, request_id)][kind].append(event)
            elif kind in SERVER_REQUEST_EVENTS:
                request_id = event.get("request_id")
                if not request_id:
                    report.issue("incomplete", "SERVER_REQUEST_ID_MISSING",
                                 pid=pid, event=kind, line=line_no)
                else:
                    server_requests[(pid, request_id)][kind].append(event)
            elif kind in BROWSER_EVENTS:
                context_id, request_id = event.get("context_id"), event.get("request_id")
                if not context_id or not request_id:
                    report.issue("incomplete", "BROWSER_REQUEST_KEY_MISSING",
                                 pid=pid, event=kind, line=line_no)
                else:
                    browser_requests[(pid, context_id, request_id)][kind].append(event)
            elif kind == "browser_main_frame_navigated":
                main_navigations.append(event)
            elif kind == "browser_main_frame_load":
                main_loads.append(event)
            elif kind == "browser_load_symbols":
                load_symbols.append(event)
            elif kind == "browser_load_symbols_error":
                load_symbol_errors.append(event)
            elif kind in ("browser_pageerror", "browser_page_crash"):
                page_errors.append(event)
            elif kind in ("browser_launch_start", "browser_launched",
                          "browser_launch_error", "browser_disconnected"):
                browser_launches[(pid, event.get("browser_id"))].append(kind)
                if kind == "browser_launch_error":
                    report.issue("fail", "BROWSER_LAUNCH_ERROR", pid=pid,
                                 error=event.get("error"))
            elif kind == "browser_page":
                pages[pid] += 1

    if report.counts["lines"] == 0:
        report.issue("incomplete", "TRACE_EMPTY")
    for pid in sorted(pids):
        count = len(sidecars[pid])
        if count != 1:
            report.issue("incomplete", "SIDECAR_ENABLED_COUNT", pid=pid, count=count)
    if not root.is_dir():
        report.issue("incomplete", "SOURCE_ROOT_UNREADABLE", root=str(root))

    expected_sources = []
    index_path = report.root / "index.html"
    try:
        index_bytes = index_path.read_bytes()
        tags = _ScriptTags()
        tags.feed(index_bytes.decode("utf-8"))
        expected_sources = tags.sources
    except (OSError, UnicodeDecodeError) as exc:
        report.issue("incomplete", "INDEX_HTML_UNREADABLE", error=str(exc))
    if not expected_sources:
        report.issue("incomplete", "INDEX_SCRIPT_MANIFEST_EMPTY")
    report.counts["frozen_index_script_tags"] = len(expected_sources)

    tracked_ports = {}
    lifecycle = []
    for (pid, server_id), events in sorted(servers.items()):
        created = events.get("server_created", [])
        shutdown = events.get("server_shutdown", [])
        closed = events.get("server_closed", [])
        if len(created) != 1:
            report.issue("incomplete", "SERVER_CREATED_COUNT", pid=pid,
                         server_id=server_id, count=len(created))
        port = created[0].get("port") if created else None
        if isinstance(port, int):
            key = (pid, port)
            if key in tracked_ports and tracked_ports[key] != server_id:
                report.issue("incomplete", "SERVER_PORT_REUSED", pid=pid, port=port)
            tracked_ports[key] = server_id
        else:
            report.issue("incomplete", "SERVER_PORT_MISSING", pid=pid,
                         server_id=server_id)
        if len(shutdown) != 1 or len(closed) != 1:
            report.issue("fail", "SERVER_CLEANUP_INCOMPLETE", pid=pid,
                         server_id=server_id, shutdown=len(shutdown), closed=len(closed))
        lifecycle.append({"pid": pid, "server_id": server_id, "port": port,
                          "created": len(created), "shutdown": len(shutdown),
                          "closed": len(closed),
                          "server_root_hint": created[0].get("server_root_hint")
                          if created else None,
                          "server_root_hint_source": created[0].get(
                              "server_root_hint_source") if created else None,
                          "loop_started": len(events.get("server_loop_start", [])),
                          "loop_ended": len(events.get("server_loop_end", []))})

    # A server may serve a generated build or a fixture, and temporary roots
    # may have been removed before this external validator runs. The effective
    # per-request directory and the file actually opened are primary evidence;
    # the creation hint is shown but never promoted to proof of source bytes.
    roots_by_port = defaultdict(set)
    root_missing_by_port = Counter()
    copies_by_path = defaultdict(list)
    index_manifests = defaultdict(list)
    for (pid, request_id), events in server_requests.items():
        first = next((item for kind in ("server_request", "server_status",
                                      "server_copy_start", "server_copy_done")
                      for item in events.get(kind, [])), None)
        if not first or not isinstance(first.get("port"), int):
            continue
        port = first["port"]
        root_value = first.get("server_root")
        if isinstance(root_value, str) and Path(root_value).is_absolute():
            roots_by_port[(pid, port)].add(str(Path(root_value).resolve()))
        else:
            root_missing_by_port[(pid, port)] += 1
        path = _server_js_path(first.get("path"))
        if path is not None:
            for done in events.get("server_copy_done", []):
                copies_by_path[(pid, port, path)].append(done)
        if urlsplit(first.get("path") or "").path == "/index.html":
            for done in events.get("server_copy_done", []):
                index_manifests[(pid, port)].append(done)

    alternate_index_ports = set(index_manifests)
    def port_root(pid, port):
        roots = roots_by_port[(pid, port)]
        if len(roots) == 1 and root_missing_by_port[(pid, port)] == 0:
            return next(iter(roots))
        return None

    def port_scope(pid, port, actual_source=None):
        root_value = port_root(pid, port)
        if root_value is None:
            return "UNKNOWN"
        if actual_source and not _within(actual_source, root_value):
            return "FIXTURE_OR_OTHER"
        if Path(root_value) == report.root:
            return "FROZEN_APP"
        if (pid, port) in alternate_index_ports or \
                (Path(root_value) / "index.html").is_file():
            return "ALTERNATE_BUILD"
        return "FIXTURE_OR_OTHER"

    for key in tracked_ports:
        pid, port = key
        roots = roots_by_port[key]
        if not roots or root_missing_by_port[key]:
            report.issue("incomplete", "SERVER_REQUEST_ROOT_UNOBSERVED",
                         scope="UNKNOWN", pid=pid, port=port,
                         known_roots=sorted(roots),
                         missing_request_count=root_missing_by_port[key])
        elif len(roots) != 1:
            report.issue("incomplete", "SERVER_REQUEST_ROOT_AMBIGUOUS",
                         scope="UNKNOWN", pid=pid, port=port,
                         known_roots=sorted(roots))
        else:
            report.scope_counts[f"{port_scope(pid, port)}:servers"] += 1
    for item in lifecycle:
        key = (item["pid"], item["port"])
        item["observed_request_roots"] = sorted(roots_by_port[key])
        item["missing_request_root_count"] = root_missing_by_port[key]
        item["scope"] = port_scope(*key)
    for event in server_error_events:
        pid, port = event["pid"], event.get("port")
        if not isinstance(port, int):
            created = servers.get((pid, event.get("server_id")), {}).get(
                "server_created", [])
            port = created[0].get("port") if created else None
        report.issue("fail", "SERVER_ERROR",
                     scope=port_scope(pid, port) if isinstance(port, int) else "UNKNOWN",
                     pid=pid, event=event["event"],
                     server_id=event.get("server_id"),
                     request_id=event.get("request_id"),
                     error=event.get("error"))

    for event in page_errors:
        url = event.get("url")
        try:
            parts = urlsplit(url)
            tracked = (event["pid"], parts.port) in tracked_ports and \
                parts.hostname in LOOPBACK
        except (TypeError, ValueError):
            tracked = False
        if tracked:
            severity = "fail" if event["event"] == "browser_page_crash" else "runtime"
            report.issue(severity, "BROWSER_RUNTIME_ERROR",
                         scope=port_scope(event["pid"], parts.port),
                         pid=event["pid"],
                         event=event["event"], context_id=event.get("context_id"),
                         page_id=event.get("page_id"), url=url,
                         error=event.get("error"))
        else:
            report.counts["non_app_page_errors"] += 1

    # Server requests have their own IDs; verify every observed local JS copy.
    copies = Counter()
    server_js_requests = Counter()
    conditional_304 = []
    for (pid, request_id), events in server_requests.items():
        first = next((item for kind in ("server_request", "server_status",
                                      "server_copy_start", "server_copy_done")
                      for item in events.get(kind, []) if item.get("path")), None)
        path = _server_js_path(first.get("path")) if first else None
        if path is None:
            continue
        port = first.get("port")
        if not isinstance(port, int):
            report.issue("incomplete", "SERVER_JS_PORT_MISSING", pid=pid,
                         request_id=request_id)
            continue
        key = (pid, port, path)
        scope = port_scope(pid, port)
        report.scope_counts[f"{scope}:server_js_requests"] += 1
        server_js_requests[key] += 1
        report.counts["server_js_requests"] += 1
        statuses = events.get("server_status", [])
        headers = events.get("server_headers_done", [])
        done = events.get("server_copy_done", [])
        if len(statuses) == 1:
            status = statuses[0].get("status")
            if status == 304:
                # A conditional response has no body by design. Require the
                # request validator and check browser cache bodies separately.
                requests = events.get("server_request", [])
                conditional = (requests[0].get("if_modified_since") or
                               requests[0].get("if_none_match")) if len(requests) == 1 else None
                if len(headers) != 1 or done:
                    report.issue("incomplete", "SERVER_JS_304_CHAIN_INVALID",
                                 scope=scope, pid=pid,
                                 request_id=request_id, path=path,
                                 headers=len(headers), copy_done=len(done))
                elif not conditional:
                    report.issue("fail", "SERVER_JS_304_WITHOUT_CONDITION",
                                 scope=scope, pid=pid, request_id=request_id, path=path)
                else:
                    conditional_304.append({
                        "pid": pid, "port": port, "path": path,
                        "request_id": request_id,
                        "request_time": requests[0].get("monotonic_ns"),
                        "status_time": statuses[0].get("monotonic_ns")})
                    report.counts["server_js_304"] += 1
                continue
            if not isinstance(status, int) or not 200 <= status < 300:
                report.issue("fail", "SERVER_JS_NON_2XX", scope=scope, pid=pid,
                             request_id=request_id, path=path, status=status)
        if len(statuses) != 1 or len(headers) != 1 or len(done) != 1:
            report.issue("incomplete", "SERVER_JS_CHAIN_INCOMPLETE", scope=scope, pid=pid,
                         request_id=request_id, path=path,
                         status_count=len(statuses), header_count=len(headers),
                         copy_done_count=len(done))
            continue
        if not isinstance(status, int) or not 200 <= status < 300:
            continue
        content_length = headers[0].get("content_length")
        copy_length = done[0].get("content_length")
        bytes_written = done[0].get("bytes_written")
        if not isinstance(content_length, int) or not isinstance(bytes_written, int) \
                or not isinstance(copy_length, int):
            report.issue("incomplete", "SERVER_JS_LENGTH_MISSING", scope=scope, pid=pid,
                         request_id=request_id, path=path)
            continue
        if not (bytes_written == content_length == copy_length):
            report.issue("fail", "SERVER_JS_LENGTH_MISMATCH", scope=scope, pid=pid,
                         request_id=request_id, path=path,
                         bytes_written=bytes_written, content_length=content_length,
                         copy_length=copy_length)
            continue
        source_path = done[0].get("source_path")
        scope = port_scope(pid, port, source_path)
        if scope == "UNKNOWN":
            report.issue("incomplete", "SERVER_JS_ROOT_UNKNOWN", scope=scope,
                         pid=pid, request_id=request_id, path=path)
        if source_path and not _within(source_path, port_root(pid, port)):
            report.scope_counts[f"{scope}:actual_source_outside_declared_root"] += 1
        source = report.expected_file(source_path, scope=scope,
                                      fallback=(bytes_written, done[0].get("sha256")))
        if source is None:
            continue
        source_length, source_hash = source
        if bytes_written != source_length or done[0].get("sha256") != source_hash:
            report.issue("fail", "SERVER_JS_SOURCE_MISMATCH", scope=scope, pid=pid,
                         request_id=request_id, path=path, source_path=source_path,
                         bytes_written=bytes_written, source_length=source_length,
                         observed_sha256=done[0].get("sha256"),
                         source_sha256=source_hash)
            continue
        copies[key] += 1
        report.counts["server_js_copies_verified"] += 1
        report.scope_counts[f"{scope}:server_js_copies_verified"] += 1

    verified_browser_keys = set()
    verified_browser_history = defaultdict(list)
    observed_2xx_history = defaultdict(list)
    main_script_requests = []
    document_requests = []
    index_document_requests_any = []
    browser_records = 0
    ordered_browser_requests = sorted(browser_requests.items(), key=lambda pair:
        min((item.get("monotonic_ns", 0) for kind in pair[1].values()
             for item in kind), default=0))
    for (pid, context_id, request_id), events in ordered_browser_requests:
        request = events.get("browser_request", [])
        base = request[0] if request else next(
            (items[0] for items in events.values() if items), None)
        url = base.get("url") if base else None
        if request and request[0].get("resource_type") == "document":
            document_url = request[0].get("url")
            try:
                document_parts = urlsplit(document_url)
                is_index = document_parts.hostname in LOOPBACK and \
                    document_parts.path == "/index.html"
            except (TypeError, ValueError):
                is_index = False
            if is_index:
                index_document_requests_any.append(request[0])
                if request[0].get("frame_is_main") is not True or \
                        not request[0].get("page_id"):
                    report.issue("incomplete", "INDEX_DOCUMENT_FRAME_UNOBSERVED",
                                 pid=pid, context_id=context_id,
                                 request_id=request_id, url=document_url)
            if request[0].get("frame_is_main") is True:
                document_requests.append(request[0])
        local = _local_js_url(url)
        if local is None:
            if request:
                try:
                    host = urlsplit(url).hostname
                except (TypeError, ValueError):
                    host = None
                report.counts["other_local_requests" if host in LOOPBACK
                              else "external_or_fixture_requests"] += 1
            continue
        port, path = local
        if (pid, port) not in tracked_ports:
            report.counts["unobserved_local_js"] += 1
            report.issue("incomplete", "LOCAL_JS_SERVER_UNOBSERVED",
                         scope="UNKNOWN", pid=pid, context_id=context_id,
                         request_id=request_id, port=port, path=path)
            continue
        browser_records += 1
        key_by_path = (pid, port, path)
        source_copies = copies_by_path[key_by_path]
        paths = {item.get("source_path") for item in source_copies}
        body_versions = {(item.get("bytes_written"), item.get("sha256"))
                         for item in source_copies}
        if len(paths) > 1 or len(body_versions) > 1:
            report.issue("incomplete", "BROWSER_JS_SOURCE_VERSION_AMBIGUOUS",
                         scope=port_scope(pid, port), pid=pid, port=port,
                         path=path, actual_sources=sorted(str(p) for p in paths),
                         observed_versions=len(body_versions))
            source = None
            relative = None
            scope = port_scope(pid, port)
        elif source_copies:
            source_path = source_copies[0].get("source_path")
            scope = port_scope(pid, port, source_path)
            source = report.expected_file(source_path, scope=scope,
                                          fallback=next(iter(body_versions)))
            relative = source_path
        else:
            scope = port_scope(pid, port)
            source, relative = report.expected_source(
                path, root=port_root(pid, port), scope=scope)
        report.scope_counts[f"{scope}:browser_local_js_requests"] += 1
        report.counts["browser_local_js_requests"] += 1
        if len(request) != 1:
            report.issue("incomplete", "BROWSER_REQUEST_EVENT_COUNT", scope=scope, pid=pid,
                         context_id=context_id, request_id=request_id,
                         count=len(request), url=url)
        response = events.get("browser_response", [])
        finished = events.get("browser_request_finished", [])
        failed = events.get("browser_request_failed", [])
        body = events.get("browser_js_body", [])
        body_errors = events.get("browser_js_body_error", [])
        partition = (pid, context_id, request[0].get("page_id") if request else None,
                     request[0].get("frame_id") if request else None,
                     request[0].get("method") if request else None,
                     request[0].get("resource_type") if request else None,
                     url, port_root(pid, port))
        if request and request[0].get("resource_type") == "script" and \
                request[0].get("frame_is_main") is True:
            main_script_requests.append((request[0], (pid, context_id, request_id)))
        if failed:
            report.issue("fail", "BROWSER_LOCAL_JS_REQUEST_FAILED", scope=scope, pid=pid,
                         context_id=context_id, request_id=request_id,
                         url=url, failure=failed[0].get("failure"))
        if len(response) != 1 or len(finished) != 1 or failed:
            if not failed:
                report.issue("incomplete", "BROWSER_JS_CHAIN_INCOMPLETE", scope=scope, pid=pid,
                             context_id=context_id, request_id=request_id,
                             url=url, responses=len(response), finished=len(finished),
                             failed=len(failed))
            continue
        status = response[0].get("status")
        if status == 304:
            finished_at = finished[0].get("monotonic_ns")
            earlier = [item for item in verified_browser_history[partition]
                       if isinstance(item[0], int) and
                       isinstance(finished_at, int) and item[0] < finished_at]
            matches = [item for item in conditional_304
                       if (item["pid"], item["port"], item["path"]) ==
                       (pid, port, path) and
                       isinstance(item["request_time"], int) and
                       isinstance(finished_at, int) and
                       item["request_time"] <= finished_at and
                       (not earlier or item["request_time"] > earlier[-1][0])]
            prior = earlier[-1] if earlier else None
            intermediate_2xx = [item for item in observed_2xx_history[partition]
                                if prior and item[0] > prior[0] and
                                isinstance(finished_at, int) and item[0] < finished_at]
            unavailable = len(body) == 0 and len(body_errors) == 1 and \
                body_errors[0].get("status") == 304 and \
                "unavailable" in str(body_errors[0].get("error", "")).lower()
            if prior and matches and unavailable and not intermediate_2xx and \
                    source == (prior[1], prior[2]):
                verified_browser_keys.add((pid, context_id, request_id))
                report.counts["browser_js_cache_continuity_inferred"] += 1
                report.scope_counts[f"{scope}:cache_continuity_inferred"] += 1
                report.counts["browser_304_with_aggregate_server_corroboration"] += 1
                continue
            report.issue("incomplete", "BROWSER_JS_304_CACHE_CHAIN_UNVERIFIED",
                         scope=scope, pid=pid, context_id=context_id,
                         request_id=request_id, url=url, prior_verified=bool(prior),
                         matching_conditional_count=len(matches),
                         body_unavailable=unavailable,
                         intermediate_2xx=len(intermediate_2xx),
                         source_matches_prior=bool(prior and source ==
                                                   (prior[1], prior[2])))
            continue
        if isinstance(status, int) and 200 <= status < 300:
            observed_2xx_history[partition].append(
                (response[0].get("monotonic_ns"), request_id))
        if not isinstance(status, int) or not 200 <= status < 300:
            severity = "incomplete" if status == 304 else "fail"
            report.issue(severity, "BROWSER_LOCAL_JS_NON_2XX", pid=pid,
                         scope=scope, context_id=context_id, request_id=request_id,
                         url=url, status=status)
            continue
        if body_errors:
            report.issue("incomplete", "BROWSER_JS_BODY_COLLECTION_ERROR", scope=scope, pid=pid,
                         context_id=context_id, request_id=request_id, url=url,
                         errors=[item.get("error") for item in body_errors[:2]])
        if len(body) != 1:
            report.issue("incomplete", "BROWSER_JS_BODY_EVENT_COUNT", scope=scope, pid=pid,
                         context_id=context_id, request_id=request_id, url=url,
                         count=len(body))
            continue
        observed = body[0]
        resource_type = request[0].get("resource_type") if request else None
        if observed.get("url") != url or observed.get("resource_type") != resource_type \
                or observed.get("status") != status or \
                observed.get("from_service_worker") != response[0].get("from_service_worker"):
            report.issue("incomplete", "BROWSER_JS_BODY_METADATA_CONFLICT", scope=scope, pid=pid,
                         context_id=context_id, request_id=request_id, url=url)
            continue
        if source is None:
            continue
        source_length, source_hash = source
        if observed.get("bytes_received") != source_length or \
                observed.get("sha256") != source_hash:
            report.issue("fail", "BROWSER_JS_BODY_SOURCE_MISMATCH", scope=scope, pid=pid,
                         context_id=context_id, request_id=request_id, url=url,
                         relative=relative,
                         observed_length=observed.get("bytes_received"),
                         source_length=source_length,
                         observed_sha256=observed.get("sha256"),
                         source_sha256=source_hash)
            continue
        verified_browser_keys.add((pid, context_id, request_id))
        verified_browser_history[partition].append(
            (observed.get("monotonic_ns"), source_length, source_hash, request_id))
        report.counts["browser_js_bodies_verified"] += 1
        report.scope_counts[f"{scope}:browser_js_bodies_verified"] += 1
        report.counts["browser_js_verified_" + str(resource_type)] += 1
        if observed.get("from_service_worker"):
            report.counts["browser_js_verified_from_service_worker"] += 1

    # Server and browser request IDs are independent. We cannot label any
    # individual server 304 as the browser's revalidation, especially for SW
    # background fetches. Preserve the count as unresolved provenance.
    report.counts["server_conditional_304_unlinked"] = len(conditional_304)

    def index_identity(event):
        try:
            parts = urlsplit(event.get("url"))
            if parts.hostname in LOOPBACK and parts.path == "/index.html" and \
                    (event.get("pid"), parts.port) in tracked_ports:
                return event.get("pid"), event.get("context_id"), \
                    event.get("page_id"), event.get("frame_id")
        except (TypeError, ValueError):
            pass
        return None

    index_navigations = sorted((event for event in main_navigations
                                if index_identity(event)),
                               key=lambda event: (event["pid"],
                                                  event.get("monotonic_ns", 0)))
    frozen_intent_ports = {(item["pid"], item["port"]) for item in lifecycle
                           if item.get("server_root_hint") == str(report.root)}
    frozen_intent_navigations = sum(
        1 for event in index_navigations
        if (event["pid"], urlsplit(event["url"]).port) in frozen_intent_ports)
    index_loads = [event for event in main_loads if index_identity(event)]
    index_document_requests = [event for event in document_requests
                               if index_identity(event)]
    if index_document_requests_any and not index_navigations:
        report.issue("incomplete", "INDEX_NAVIGATION_EVENT_MISSING",
                     document_requests=len(index_document_requests_any))
    report.counts["main_index_navigations"] = len(index_navigations)
    report.counts["main_index_loads"] = len(index_loads)
    complete_navigations = 0
    frozen_complete_navigations = 0
    matched_load_ids = set()

    def index_sources_for(navigation):
        parts = urlsplit(navigation["url"])
        key = (navigation["pid"], parts.port)
        scope = port_scope(*key)
        nav_time = navigation.get("monotonic_ns")
        identity = index_identity(navigation)
        docs = [item for item in index_document_requests
                if index_identity(item) == identity and
                isinstance(item.get("monotonic_ns"), int) and
                item["monotonic_ns"] <= nav_time]
        if not docs:
            report.issue("incomplete", "INDEX_DOCUMENT_REQUEST_MISSING",
                         scope=scope, pid=key[0], port=key[1],
                         navigation_time=nav_time)
            return [], scope
        document = max(docs, key=lambda item: item["monotonic_ns"])
        record = browser_requests.get((document["pid"], document["context_id"],
                                       document["request_id"]), {})
        response = record.get("browser_response", [])
        finished = record.get("browser_request_finished", [])
        failed = record.get("browser_request_failed", [])
        bodies = record.get("browser_index_body", [])
        errors = record.get("browser_index_body_error", [])
        if len(response) != 1 or len(finished) != 1 or failed or len(bodies) != 1 \
                or errors:
            report.issue("incomplete", "INDEX_BROWSER_BODY_CHAIN_INCOMPLETE",
                         scope=scope, pid=key[0], port=key[1],
                         navigation_time=nav_time, response_count=len(response),
                         finished_count=len(finished), failed_count=len(failed),
                         body_count=len(bodies), body_errors=len(errors))
            return [], scope
        body = bodies[0]
        status = response[0].get("status")
        if not isinstance(status, int) or not 200 <= status < 300 or \
                body.get("status") != status or body.get("url") != document.get("url") or \
                body.get("resource_type") != "document" or \
                body.get("from_service_worker") != response[0].get("from_service_worker"):
            report.issue("incomplete", "INDEX_BROWSER_BODY_METADATA_INVALID",
                         scope=scope, pid=key[0], port=key[1],
                         navigation_time=nav_time, status=status)
            return [], scope
        sources = body.get("index_scripts")
        if not isinstance(sources, list) or not sources or \
                not all(isinstance(s, str) for s in sources):
            report.issue("incomplete", "INDEX_BROWSER_MANIFEST_INVALID",
                         scope=scope, pid=key[0], port=key[1],
                         navigation_time=nav_time)
            return [], scope

        candidates = [item for item in index_manifests[key]
                      if isinstance(item.get("monotonic_ns"), int) and
                      item["monotonic_ns"] <= body["monotonic_ns"]]
        if candidates:
            distinct_versions = {(item.get("bytes_written"), item.get("sha256"))
                                 for item in candidates}
            if len(distinct_versions) != 1:
                report.issue("incomplete", "INDEX_SERVER_VERSION_AMBIGUOUS",
                             scope=scope, pid=key[0], port=key[1],
                             navigation_time=nav_time,
                             observed_versions=len(distinct_versions))
                return [], scope
            item = max(candidates, key=lambda event: event["monotonic_ns"])
            scope = port_scope(*key, item.get("source_path"))
            expected = (item.get("bytes_written"), item.get("sha256"))
            if item.get("index_manifest_error") or \
                    item.get("index_manifest_sha256") != item.get("sha256") or \
                    item.get("index_scripts") != sources:
                report.issue("incomplete", "INDEX_SERVER_MANIFEST_INVALID",
                             scope=scope, pid=key[0], port=key[1],
                             navigation_time=nav_time,
                             error=item.get("index_manifest_error"))
                return [], scope
        else:
            root_value = port_root(*key)
            if scope != "FROZEN_APP":
                report.issue("incomplete", "INDEX_SOURCE_PROVENANCE_UNVERIFIED",
                             scope=scope, pid=key[0], port=key[1],
                             navigation_time=nav_time,
                             reason="No server copy for alternate document")
                return [], scope
            expected, _relative = report.expected_source(
                "/index.html", root=root_value, scope=scope)
            if expected is None:
                report.issue("incomplete", "INDEX_SOURCE_PROVENANCE_UNVERIFIED",
                             scope=scope, pid=key[0], port=key[1],
                             navigation_time=nav_time)
                return [], scope
            report.scope_counts[f"{scope}:index_from_cache_without_server_copy"] += 1
        if (body.get("bytes_received"), body.get("sha256")) != expected:
            report.issue("fail", "INDEX_BROWSER_BODY_SOURCE_MISMATCH",
                         scope=scope, pid=key[0], port=key[1],
                         navigation_time=nav_time,
                         observed_length=body.get("bytes_received"),
                         observed_sha256=body.get("sha256"),
                         expected_length=expected[0], expected_sha256=expected[1])
            return [], scope
        report.scope_counts[f"{scope}:browser_index_bodies_verified"] += 1
        return sources, scope

    for nav_index, navigation in enumerate(index_navigations):
        identity = index_identity(navigation)
        pid, context_id, page_id, frame_id = identity
        nav_sources, scope = index_sources_for(navigation)
        report.scope_counts[f"{scope}:main_index_navigations"] += 1
        nav_time = navigation.get("monotonic_ns")
        if not isinstance(nav_time, int) or not page_id or not frame_id:
            report.issue("incomplete", "INDEX_NAVIGATION_IDENTITY_MISSING",
                         pid=pid, context_id=context_id, page_id=page_id)
            continue
        following = [event.get("monotonic_ns") for event in
                     index_navigations[nav_index + 1:]
                     if index_identity(event) == identity and
                     isinstance(event.get("monotonic_ns"), int)]
        next_time = min(following) if following else float("inf")
        load_candidates = [event for event in main_loads
                           if index_identity(event) == identity and
                           isinstance(event.get("monotonic_ns"), int) and
                           nav_time <= event["monotonic_ns"] < next_time]
        if len(load_candidates) != 1:
            report.issue("incomplete", "INDEX_LOAD_EVENT_COUNT", pid=pid,
                         context_id=context_id, page_id=page_id,
                         navigation_time=nav_time, count=len(load_candidates))
        if not load_candidates:
            continue
        load = min(load_candidates, key=lambda event: event["monotonic_ns"])
        matched_load_ids.add(id(load))
        load_time = load["monotonic_ns"]
        document_starts = [event["monotonic_ns"] for event in index_document_requests
                           if index_identity(event) == identity and
                           isinstance(event.get("monotonic_ns"), int) and
                           event["monotonic_ns"] <= nav_time]
        start_time = max(document_starts) if document_starts else nav_time
        expected = Counter()
        for source in nav_sources:
            resolved = _local_js_url(urljoin(navigation["url"], source))
            if resolved is None:
                report.issue("incomplete", "INDEX_SCRIPT_URL_UNSUPPORTED", scope=scope,
                             pid=pid, source=source, navigation_url=navigation["url"])
            else:
                expected[resolved] += 1
        observed = defaultdict(list)
        for request_event, key in main_script_requests:
            if (request_event.get("pid"), request_event.get("context_id"),
                    request_event.get("page_id"), request_event.get("frame_id")) != identity:
                continue
            request_time = request_event.get("monotonic_ns")
            if not isinstance(request_time, int) or not start_time <= request_time <= load_time:
                continue
            path = _local_js_url(request_event.get("url"))
            if path is not None:
                observed[path].append(key)
        navigation_complete = bool(nav_sources)
        for path, count in expected.items():
            matches = observed[path]
            if len(matches) != count:
                navigation_complete = False
                report.issue("incomplete", "INDEX_SCRIPT_REQUEST_COUNT", scope=scope, pid=pid,
                             context_id=context_id, page_id=page_id,
                             navigation_time=nav_time, path=path[1],
                             expected=count, observed=len(matches))
            for key in matches:
                if key not in verified_browser_keys:
                    navigation_complete = False
                    report.issue("incomplete", "INDEX_SCRIPT_BODY_UNVERIFIED", scope=scope,
                                 pid=pid, context_id=context_id, page_id=page_id,
                                 navigation_time=nav_time, path=path[1],
                                 request_id=key[2])
        symbol_events = [event for event in load_symbols
                         if index_identity(event) == identity and
                         isinstance(event.get("monotonic_ns"), int) and
                         load_time <= event["monotonic_ns"] < next_time]
        symbol_errors = [event for event in load_symbol_errors
                         if index_identity(event) == identity and
                         isinstance(event.get("monotonic_ns"), int) and
                         load_time <= event["monotonic_ns"] < next_time]
        if symbol_errors or len(symbol_events) != 1:
            navigation_complete = False
            report.issue("incomplete", "INDEX_SYMBOL_SNAPSHOT_MISSING", scope=scope, pid=pid,
                         context_id=context_id, page_id=page_id,
                         navigation_time=nav_time,
                         snapshots=len(symbol_events), errors=len(symbol_errors))
        elif symbol_events[0].get("dollar_type") != "function" or \
                symbol_events[0].get("bind_config_type") != "function":
            navigation_complete = False
            severity = "runtime" if all(
                len(observed[path]) == count and all(
                    key in verified_browser_keys for key in observed[path])
                for path, count in expected.items()) else "incomplete"
            report.issue(severity, "INDEX_BOOT_SYMBOL_UNAVAILABLE", scope=scope, pid=pid,
                         context_id=context_id, page_id=page_id,
                         navigation_time=nav_time,
                         dollar_type=symbol_events[0].get("dollar_type"),
                         bind_config_type=symbol_events[0].get("bind_config_type"))
        if navigation_complete:
            complete_navigations += 1
            if scope == "FROZEN_APP":
                frozen_complete_navigations += 1
        report.counts["main_index_expected_scripts"] += sum(expected.values())
        report.counts["main_index_observed_scripts"] += sum(
            len(observed[path]) for path in expected)
    report.counts["main_index_complete_navigations"] = complete_navigations
    report.counts["frozen_main_index_complete_navigations"] = frozen_complete_navigations
    for load in index_loads:
        if id(load) not in matched_load_ids:
            report.issue("incomplete", "INDEX_LOAD_WITHOUT_NAVIGATION",
                         pid=load.get("pid"), context_id=load.get("context_id"),
                         page_id=load.get("page_id"), frame_id=load.get("frame_id"),
                         url=load.get("url"),
                         load_time=load.get("monotonic_ns"))
    main_bootstrap = ("NOT_APPLICABLE" if not index_navigations and
                      not index_document_requests_any and not index_loads else
                      "INTEGRITY_OK" if complete_navigations == len(index_navigations)
                      and len(index_navigations) == len(index_document_requests_any)
                      and len(index_navigations) == len(index_document_requests)
                      and len(index_navigations) == len(index_loads) else
                      "INCOMPLETE")
    if main_bootstrap == "INCOMPLETE" and not report.has_fail and \
            not report.has_incomplete and not report.has_runtime:
        report.issue("incomplete", "MAIN_DOCUMENT_BOOTSTRAP_UNVERIFIED")

    if servers and not browser_records:
        report.issue("incomplete", "SERVER_WITHOUT_BROWSER_APP_JS",
                     server_count=len(servers))

    if not servers and report.counts["unobserved_local_js"]:
        applicability = "UNOBSERVED_SERVER"
    elif not servers and browser_records == 0:
        applicability = "NOT_APPLICABLE_NO_LOCAL_SERVER_OR_APP_JS"
    else:
        applicability = "LOCAL_TEST_SERVER"
    return report.as_dict(
        pids=sorted(pids), applicability=applicability,
        candidate_applicability=(
            ("FROZEN_BOOTSTRAP_WITH_CACHE_INFERENCE" if report.scope_counts[
                "FROZEN_APP:cache_continuity_inferred"] else
             "FROZEN_BOOTSTRAP_VERIFIED") if frozen_complete_navigations > 0 and
            frozen_complete_navigations == report.scope_counts[
                "FROZEN_APP:main_index_navigations"] and
            not report.scope_severities["FROZEN_APP"]["fail"] and
            not report.scope_severities["FROZEN_APP"]["incomplete"] else
            "FROZEN_BOOTSTRAP_INCOMPLETE" if report.scope_counts[
                "FROZEN_APP:main_index_navigations"] or
            frozen_intent_navigations else
            "NOT_ASSESSED_NO_FROZEN_MAIN_NAVIGATION"),
        main_document_bootstrap=main_bootstrap,
        background_sw_cache_provenance=(
            "NO_CONDITIONAL_304" if not conditional_304 else
            "UNRESOLVED_NO_BROWSER_SERVER_REQUEST_ID"),
        server_lifecycle=lifecycle,
        browser_count=len(browser_launches),
        browser_pages=sum(pages.values()),
        source_hashes_checked=len(report.source_hashes),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True, help="Raw sidecar JSONL")
    parser.add_argument("--root", type=Path, required=True,
                        help="Frozen runtime copy used by the test")
    parser.add_argument("--out", type=Path, required=True,
                        help="External JSON receipt path")
    args = parser.parse_args(argv)
    try:
        args.out.resolve().relative_to(args.root.resolve())
    except ValueError:
        pass
    else:
        parser.error("--out must remain outside the frozen runtime copy")
    result = validate(args.trace, args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                   sort_keys=True) + "\n", encoding="utf-8")
    print(result["overall_verdict"])
    return {"INFRA_OK": 0, "INFRA_FAIL": 2,
            "OBSERVABILITY_INCOMPLETE": 3,
            "PRODUCT_ERROR_CANDIDATE": 4}[result["overall_verdict"]]


if __name__ == "__main__":
    sys.exit(main())
