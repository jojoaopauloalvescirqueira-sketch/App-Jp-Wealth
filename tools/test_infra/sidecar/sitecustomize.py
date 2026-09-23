"""Opt-in telemetry and HTTP-server capacity for JP Wealth's local tests.

Loaded by Python only when this directory is on PYTHONPATH. With no
JPW_INFRA_MODE it has no effect. This sidecar changes neither application
resources nor Playwright routes, assertions, timeouts, or retry policy.

Revision 3 adds the effective filesystem root to each server request and the
actual source path to each copied response. These are observer fields only:
they do not alter translation, file reads, response bytes, or request order.
"""

import hashlib
from html.parser import HTMLParser
import itertools
import json
import os
from pathlib import Path
import sys
import threading
import time
from urllib.parse import urlsplit


_MODE = os.environ.get("JPW_INFRA_MODE", "").strip()
if _MODE:
    from http import server as _http

    from playwright.sync_api import Browser, BrowserType

    _TRACE = os.environ.get("JPW_INFRA_TRACE", "").strip()
    if not _TRACE:
        raise SystemExit("JPW_INFRA_TRACE is required when JPW_INFRA_MODE is set")
    try:
        _BACKLOG = int(os.environ.get("JPW_INFRA_BACKLOG", "5"))
    except ValueError as exc:
        raise SystemExit("JPW_INFRA_BACKLOG must be 5 or 128") from exc
    if _BACKLOG not in (5, 128):
        raise SystemExit("JPW_INFRA_BACKLOG must be 5 or 128")

    _FD = os.open(_TRACE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    _WRITE_LOCK = threading.Lock()
    _NEXT = itertools.count(1)

    def _id(kind):
        return f"{os.getpid()}-{kind}-{next(_NEXT)}"

    def _emit(event, **fields):
        record = {"event": event, "pid": os.getpid(), "time_ns": time.time_ns(),
                  "monotonic_ns": time.monotonic_ns(), "mode": _MODE, **fields}
        line = (json.dumps(record, ensure_ascii=False, separators=(",", ":"),
                           default=str) + "\n").encode("utf-8")
        # One append write per event keeps concurrent test-server threads' JSONL
        # records intact. A short write is an observer failure, never a PASS.
        with _WRITE_LOCK:
            written = os.write(_FD, line)
        if written != len(line):
            raise OSError(f"JPW infrastructure trace short write: {written}/{len(line)}")

    _emit("sidecar_enabled", trace=_TRACE, backlog=_BACKLOG,
          python=sys.version.split()[0], cwd=str(Path.cwd().resolve()))

    _ORIGINAL_SERVER = _http.ThreadingHTTPServer

    class _LocalTestHTTPServer(_ORIGINAL_SERVER):
        """Retain stdlib behavior while making local capacity/lifecycle visible."""

        def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
            host = str(server_address[0]).lower()
            self._jpw_local = host in ("127.0.0.1", "localhost", "::1")
            self._jpw_server_id = _id("server")
            self._jpw_connections = {}
            self._jpw_connections_lock = threading.Lock()
            self._jpw_close_lock = threading.Lock()
            self._jpw_closed = False
            # Non-loopback users of the stdlib class retain its original queue.
            if self._jpw_local:
                self.request_queue_size = _BACKLOG
            super().__init__(server_address, RequestHandlerClass, bind_and_activate)
            if self._jpw_local:
                handler_type = getattr(RequestHandlerClass, "func", RequestHandlerClass)
                handler_keywords = getattr(RequestHandlerClass, "keywords", {}) or {}
                configured_directory = handler_keywords.get("directory")
                if configured_directory is not None:
                    root_hint = str(Path(configured_directory).resolve())
                    root_hint_source = "handler_partial_directory"
                elif isinstance(handler_type, type) and issubclass(
                        handler_type, _http.SimpleHTTPRequestHandler):
                    # Default SimpleHTTPRequestHandler uses cwd at handler
                    # construction; per-request server_root below is final.
                    root_hint = str(Path.cwd().resolve())
                    root_hint_source = "simple_handler_default_cwd"
                else:
                    root_hint = None
                    root_hint_source = "unknown_handler"
                _emit("server_created", server_id=self._jpw_server_id,
                      host=self.server_address[0], port=self.server_address[1],
                      request_queue_size=self.request_queue_size,
                      protocol=getattr(handler_type, "protocol_version", None),
                      server_root_hint=root_hint,
                      server_root_hint_source=root_hint_source)

        def server_bind(self):
            try:
                result = super().server_bind()
            except Exception as exc:
                if self._jpw_local:
                    _emit("server_bind_error", server_id=self._jpw_server_id,
                          error_type=type(exc).__name__, error=str(exc))
                raise
            if self._jpw_local:
                _emit("server_bound", server_id=self._jpw_server_id,
                      host=self.server_address[0], port=self.server_address[1])
            return result

        def server_activate(self):
            result = super().server_activate()
            if self._jpw_local:
                _emit("server_listening", server_id=self._jpw_server_id,
                      port=self.server_address[1], request_queue_size=self.request_queue_size)
            return result

        def get_request(self):
            request, client = super().get_request()
            if self._jpw_local:
                connection_id = _id("connection")
                with self._jpw_connections_lock:
                    self._jpw_connections[request.fileno()] = connection_id
                _emit("server_accept", server_id=self._jpw_server_id,
                      connection_id=connection_id, port=self.server_address[1],
                      peer_host=client[0], peer_port=client[1])
            return request, client

        def handle_error(self, request, client_address):
            if self._jpw_local:
                _emit("server_handler_error", server_id=self._jpw_server_id,
                      port=self.server_address[1], peer_host=client_address[0],
                      peer_port=client_address[1],
                      error_type=getattr(sys.exc_info()[0], "__name__", None),
                      error=str(sys.exc_info()[1]))
            return super().handle_error(request, client_address)

        def shutdown_request(self, request):
            fd = request.fileno()
            try:
                return super().shutdown_request(request)
            finally:
                if self._jpw_local:
                    with self._jpw_connections_lock:
                        connection_id = self._jpw_connections.pop(fd, None)
                    _emit("server_connection_closed", server_id=self._jpw_server_id,
                          connection_id=connection_id, port=self.server_address[1])

        def serve_forever(self, poll_interval=0.5):
            if self._jpw_local:
                _emit("server_loop_start", server_id=self._jpw_server_id,
                      port=self.server_address[1])
            try:
                return super().serve_forever(poll_interval)
            except Exception as exc:
                if self._jpw_local:
                    _emit("server_loop_error", server_id=self._jpw_server_id,
                          port=self.server_address[1],
                          error_type=type(exc).__name__, error=str(exc))
                raise
            finally:
                if self._jpw_local:
                    _emit("server_loop_end", server_id=self._jpw_server_id,
                          port=self.server_address[1])

        def shutdown(self):
            try:
                return super().shutdown()
            finally:
                if self._jpw_local:
                    _emit("server_shutdown", server_id=self._jpw_server_id,
                          port=self.server_address[1])
                    self.server_close()

        def server_close(self):
            if not self._jpw_local:
                return super().server_close()
            with self._jpw_close_lock:
                if self._jpw_closed:
                    return
                try:
                    super().server_close()
                finally:
                    self._jpw_closed = True
                    _emit("server_closed", server_id=self._jpw_server_id,
                          port=self.server_address[1])

    _http.ThreadingHTTPServer = _LocalTestHTTPServer

    def _local_handler(handler):
        return isinstance(getattr(handler, "server", None), _LocalTestHTTPServer) \
            and handler.server._jpw_local

    def _request_id(handler):
        request_id = getattr(handler, "_jpw_request_id", None)
        if not request_id:
            request_id = _id("request")
            handler._jpw_request_id = request_id
        return request_id

    def _request_fields(handler):
        server = handler.server
        with server._jpw_connections_lock:
            connection_id = server._jpw_connections.get(handler.connection.fileno())
        directory = getattr(handler, "directory", None)
        try:
            server_root = str(Path(directory).resolve()) if directory is not None else None
        except (OSError, TypeError, ValueError):
            server_root = None
        return {"server_id": server._jpw_server_id,
                "connection_id": connection_id,
                "request_id": _request_id(handler),
                "port": server.server_address[1],
                "method": getattr(handler, "command", None),
                "path": getattr(handler, "path", None),
                "server_root": server_root}

    _ORIGINAL_HANDLE_ONE = _http.BaseHTTPRequestHandler.handle_one_request
    _ORIGINAL_PARSE = _http.BaseHTTPRequestHandler.parse_request
    _ORIGINAL_SEND_RESPONSE = _http.BaseHTTPRequestHandler.send_response
    _ORIGINAL_END_HEADERS = _http.BaseHTTPRequestHandler.end_headers
    _ORIGINAL_COPYFILE = _http.SimpleHTTPRequestHandler.copyfile

    def _handle_one_request(handler):
        if _local_handler(handler):
            handler._jpw_request_id = _id("request")
        try:
            return _ORIGINAL_HANDLE_ONE(handler)
        except Exception as exc:
            if _local_handler(handler):
                _emit("server_request_error", **_request_fields(handler),
                      error_type=type(exc).__name__, error=str(exc))
            raise

    def _parse_request(handler):
        result = _ORIGINAL_PARSE(handler)
        if result and _local_handler(handler):
            _emit("server_request", **_request_fields(handler),
                  if_modified_since=handler.headers.get("If-Modified-Since"),
                  if_none_match=handler.headers.get("If-None-Match"))
        return result

    def _send_response(handler, code, message=None):
        if _local_handler(handler):
            _emit("server_status", **_request_fields(handler), status=code)
        return _ORIGINAL_SEND_RESPONSE(handler, code, message)

    def _end_headers(handler):
        length = None
        if _local_handler(handler):
            for raw in getattr(handler, "_headers_buffer", ()):
                if raw.lower().startswith(b"content-length:"):
                    try:
                        length = int(raw.split(b":", 1)[1].strip())
                    except ValueError:
                        length = None
            handler._jpw_content_length = length
        try:
            result = _ORIGINAL_END_HEADERS(handler)
        except Exception as exc:
            if _local_handler(handler):
                _emit("server_headers_error", **_request_fields(handler),
                      content_length=length, error_type=type(exc).__name__,
                      error=str(exc))
            raise
        if _local_handler(handler):
            _emit("server_headers_done", **_request_fields(handler),
                  content_length=length)
        return result

    class _CountingOutput:
        def __init__(self, output):
            self.output = output
            self.bytes_written = 0
            self.digest = hashlib.sha256()

        def write(self, data):
            result = self.output.write(data)
            accepted = len(data) if result is None else result
            self.bytes_written += accepted
            self.digest.update(memoryview(data)[:accepted])
            return result

    class _ScriptTags(HTMLParser):
        def __init__(self):
            super().__init__()
            self.sources = []

        def handle_starttag(self, tag, attrs):
            if tag.lower() == "script":
                src = dict(attrs).get("src")
                if src:
                    self.sources.append(src)

    def _copyfile(handler, source, outputfile):
        if not _local_handler(handler):
            return _ORIGINAL_COPYFILE(handler, source, outputfile)
        counted = _CountingOutput(outputfile)
        source_name = getattr(source, "name", None)
        try:
            source_path = str(Path(source_name).resolve()) if source_name is not None else None
        except (OSError, TypeError, ValueError):
            source_path = None
        _emit("server_copy_start", **_request_fields(handler),
              content_length=getattr(handler, "_jpw_content_length", None),
              source_path=source_path)
        try:
            result = _ORIGINAL_COPYFILE(handler, source, counted)
        except Exception as exc:
            _emit("server_copy_error", **_request_fields(handler),
                  bytes_written=counted.bytes_written,
                  sha256=counted.digest.hexdigest(),
                  error_type=type(exc).__name__, error=str(exc))
            raise
        index_scripts = None
        index_manifest_error = None
        index_manifest_sha256 = None
        if source_path is not None and Path(source_path).name == "index.html":
            try:
                index_bytes = Path(source_path).read_bytes()
                index_manifest_sha256 = hashlib.sha256(index_bytes).hexdigest()
                tags = _ScriptTags()
                tags.feed(index_bytes.decode("utf-8"))
                index_scripts = tags.sources
                if index_manifest_sha256 != counted.digest.hexdigest():
                    index_manifest_error = "Source changed while the response was copied"
            except (OSError, UnicodeError, ValueError) as exc:
                index_manifest_error = f"{type(exc).__name__}: {exc}"
        _emit("server_copy_done", **_request_fields(handler),
              bytes_written=counted.bytes_written,
              content_length=getattr(handler, "_jpw_content_length", None),
              sha256=counted.digest.hexdigest(), source_path=source_path,
              index_scripts=index_scripts,
              index_manifest_sha256=index_manifest_sha256,
              index_manifest_error=index_manifest_error)
        return result

    _http.BaseHTTPRequestHandler.handle_one_request = _handle_one_request
    _http.BaseHTTPRequestHandler.parse_request = _parse_request
    _http.BaseHTTPRequestHandler.send_response = _send_response
    _http.BaseHTTPRequestHandler.end_headers = _end_headers
    _http.SimpleHTTPRequestHandler.copyfile = _copyfile

    _ORIGINAL_LAUNCH = BrowserType.launch
    _ORIGINAL_NEW_CONTEXT = Browser.new_context
    _ORIGINAL_NEW_PAGE = Browser.new_page

    def _launch(browser_type, **options):
        safe_options = {name: options[name] for name in
                        ("executable_path", "channel", "headless", "args", "timeout", "slow_mo")
                        if name in options}
        browser_id = _id("browser")
        _emit("browser_launch_start", browser_id=browser_id,
              browser_type=browser_type.name, options=safe_options)
        try:
            browser = _ORIGINAL_LAUNCH(browser_type, **options)
        except Exception as exc:
            _emit("browser_launch_error", browser_id=browser_id,
                  error_type=type(exc).__name__, error=str(exc))
            raise
        browser._jpw_infra_id = browser_id
        _emit("browser_launched", browser_id=browser_id,
              browser_type=browser_type.name, version=browser.version,
              executable=str(options.get("executable_path") or browser_type.executable_path),
              options=safe_options)
        browser.on("disconnected", lambda *_args: _emit("browser_disconnected",
                                                      browser_id=browser_id))
        return browser

    def _attach_context(context, options, browser_id, context_id, entrypoint,
                        existing_page=None):
        # Browser.new_page() creates an implicit context inside Playwright; it
        # does not go through the public Browser.new_context() method. Attach
        # after creation but before the caller can navigate the returned page.
        existing_id = getattr(context, "_jpw_infra_id", None)
        if existing_id:
            if existing_page is not None:
                context._jpw_infra_attach_page(existing_page)
            _emit("context_already_attached", context_id=existing_id,
                  attempted_context_id=context_id, entrypoint=entrypoint)
            return context
        context._jpw_infra_id = context_id
        request_ids = {}
        frame_ids = {}
        responses = {}

        def request_id(request):
            key = id(request._impl_obj)
            if key not in request_ids:
                # Retain the implementation object to prevent Python id reuse
                # from conflating unrelated requests during a long gate.
                request_ids[key] = (request._impl_obj, _id("browser-request"))
            return request_ids[key][1]

        def frame_id(frame):
            key = id(frame._impl_obj)
            if key not in frame_ids:
                frame_ids[key] = (frame._impl_obj, _id("frame"))
            return frame_ids[key][1]

        def request_location(request):
            # Service-worker fetches have no document frame. Keep them distinct
            # from parser-initiated <script> requests in the index document.
            try:
                worker = request.service_worker
            except Exception as exc:
                return {"page_id": None, "frame_id": None,
                        "frame_is_main": None, "service_worker_url": None,
                        "frame_error": str(exc)}
            if worker is not None:
                return {"page_id": None, "frame_id": None,
                        "frame_is_main": None, "service_worker_url": worker.url}
            try:
                frame = request.frame
                page = frame.page
                return {"page_id": getattr(page, "_jpw_infra_page_id", None),
                        "frame_id": frame_id(frame),
                        "frame_is_main": frame.parent_frame is None,
                        "service_worker_url": None}
            except Exception as exc:
                # Playwright can report a navigation before its frame exists.
                # Record that limitation instead of guessing a page identity.
                return {"page_id": None, "frame_id": None,
                        "frame_is_main": None, "service_worker_url": None,
                        "frame_error": str(exc)}

        def loopback_js(url):
            parsed = urlsplit(url)
            return parsed.scheme in ("http", "https") \
                and parsed.hostname in ("127.0.0.1", "localhost", "::1") \
                and parsed.path.lower().endswith(".js")

        def loopback_index(url):
            parsed = urlsplit(url)
            return parsed.scheme in ("http", "https") \
                and parsed.hostname in ("127.0.0.1", "localhost", "::1") \
                and parsed.path == "/index.html"

        def on_request(request):
            _emit("browser_request", context_id=context_id,
                  request_id=request_id(request), url=request.url,
                  method=request.method, resource_type=request.resource_type,
                  is_navigation_request=request.is_navigation_request(),
                  **request_location(request))

        def on_response(response):
            req_id = request_id(response.request)
            responses[req_id] = response
            _emit("browser_response", context_id=context_id,
                  request_id=req_id, url=response.url,
                  status=response.status,
                  from_service_worker=response.from_service_worker,
                  **request_location(response.request))

        def on_finished(request):
            req_id = request_id(request)
            _emit("browser_request_finished", context_id=context_id,
                  request_id=req_id, url=request.url,
                  **request_location(request))
            is_js = loopback_js(request.url)
            is_index = loopback_index(request.url) and \
                request.resource_type == "document"
            if not is_js and not is_index:
                return
            event_stem = "browser_js_body" if is_js else "browser_index_body"
            response = responses.get(req_id)
            if response is None:
                _emit(event_stem + "_error", context_id=context_id,
                      request_id=req_id, url=request.url,
                      resource_type=request.resource_type,
                      error_type="MissingResponse",
                      error="requestfinished had no matching response event",
                      **request_location(request))
                return
            try:
                # The original test continues unchanged. A body-read failure
                # remains an explicit observer error for the external verifier.
                body = response.body()
            except Exception as exc:
                _emit(event_stem + "_error", context_id=context_id,
                      request_id=req_id, url=request.url,
                      resource_type=request.resource_type,
                      status=response.status,
                      from_service_worker=response.from_service_worker,
                      error_type=type(exc).__name__, error=str(exc),
                      **request_location(request))
                return
            scripts = None
            if is_index:
                try:
                    tags = _ScriptTags()
                    tags.feed(body.decode("utf-8"))
                    scripts = tags.sources
                except (UnicodeError, ValueError) as exc:
                    _emit("browser_index_body_error", context_id=context_id,
                          request_id=req_id, url=request.url,
                          resource_type=request.resource_type,
                          status=response.status,
                          from_service_worker=response.from_service_worker,
                          error_type=type(exc).__name__, error=str(exc),
                          **request_location(request))
                    return
            _emit(event_stem, context_id=context_id,
                  request_id=req_id, url=request.url,
                  resource_type=request.resource_type,
                  status=response.status,
                  from_service_worker=response.from_service_worker,
                  bytes_received=len(body), sha256=hashlib.sha256(body).hexdigest(),
                  **({"index_scripts": scripts} if is_index else {}),
                  **request_location(request))

        def on_failed(request):
            _emit("browser_request_failed", context_id=context_id,
                  request_id=request_id(request), url=request.url,
                  failure=request.failure, **request_location(request))

        def on_page(page):
            if getattr(page, "_jpw_infra_page_id", None):
                return
            page_id = _id("page")
            page._jpw_infra_page_id = page_id
            _emit("browser_page", context_id=context_id, page_id=page_id)

            def on_frame_navigated(frame):
                if frame.parent_frame is None:
                    _emit("browser_main_frame_navigated", context_id=context_id,
                          page_id=page_id, frame_id=frame_id(frame), url=frame.url)

            def on_load(*_args):
                frame = page.main_frame
                _emit("browser_main_frame_load", context_id=context_id,
                      page_id=page_id, frame_id=frame_id(frame), url=page.url)
                parsed = urlsplit(page.url)
                if parsed.hostname not in ("127.0.0.1", "localhost", "::1") \
                        or not parsed.path.endswith("/index.html"):
                    return
                try:
                    symbols = page.evaluate(
                        "() => ({dollar: typeof $, bindConfig: typeof bindConfig})")
                except Exception as exc:
                    _emit("browser_load_symbols_error", context_id=context_id,
                          page_id=page_id, frame_id=frame_id(frame), url=page.url,
                          error_type=type(exc).__name__, error=str(exc))
                    return
                _emit("browser_load_symbols", context_id=context_id,
                      page_id=page_id, frame_id=frame_id(frame), url=page.url,
                      dollar_type=symbols["dollar"],
                      bind_config_type=symbols["bindConfig"])

            page.on("framenavigated", on_frame_navigated)
            page.on("load", on_load)
            page.on("pageerror", lambda error: _emit("browser_pageerror",
                    context_id=context_id, page_id=page_id, url=page.url,
                    error=str(error)))
            page.on("crash", lambda *_args: _emit("browser_page_crash",
                    context_id=context_id, page_id=page_id, url=page.url))

        context._jpw_infra_attach_page = on_page
        context.on("request", on_request)
        context.on("response", on_response)
        context.on("requestfinished", on_finished)
        context.on("requestfailed", on_failed)
        context.on("page", on_page)
        context.on("close", lambda *_args: _emit("browser_context_closed",
                                          context_id=context_id))
        if existing_page is not None:
            on_page(existing_page)
        _emit("context_created", context_id=context_id,
              browser_id=browser_id, entrypoint=entrypoint)
        return context

    def _new_context(browser, **options):
        context_id = _id("context")
        browser_id = getattr(browser, "_jpw_infra_id", None)
        _emit("context_create_start", context_id=context_id,
              browser_id=browser_id, entrypoint="browser.new_context",
              viewport=options.get("viewport"),
              service_workers=options.get("service_workers", "allow"),
              timezone_id=options.get("timezone_id"))
        try:
            context = _ORIGINAL_NEW_CONTEXT(browser, **options)
        except Exception as exc:
            _emit("context_create_error", context_id=context_id,
                  entrypoint="browser.new_context",
                  error_type=type(exc).__name__, error=str(exc))
            raise
        return _attach_context(context, options, browser_id, context_id,
                               "browser.new_context")

    def _new_page(browser, **options):
        context_id = _id("context")
        browser_id = getattr(browser, "_jpw_infra_id", None)
        _emit("context_create_start", context_id=context_id,
              browser_id=browser_id, entrypoint="browser.new_page",
              viewport=options.get("viewport"),
              service_workers=options.get("service_workers", "allow"),
              timezone_id=options.get("timezone_id"))
        try:
            page = _ORIGINAL_NEW_PAGE(browser, **options)
        except Exception as exc:
            _emit("context_create_error", context_id=context_id,
                  entrypoint="browser.new_page",
                  error_type=type(exc).__name__, error=str(exc))
            raise
        _attach_context(page.context, options, browser_id, context_id,
                        "browser.new_page", existing_page=page)
        return page

    BrowserType.launch = _launch
    Browser.new_context = _new_context
    Browser.new_page = _new_page
