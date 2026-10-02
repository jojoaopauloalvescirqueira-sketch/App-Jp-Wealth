"""HTTP transport for local browser fixtures; never substitutes app responses.

The classic-script bootstrap opens many connections at once. The socketserver
default accept queue of five can drop those connections before request threads
exist, yielding missing scripts and unrelated downstream failures. A bounded
128-connection queue serves the same bytes with the same handlers and deadlines.
"""

from http.server import ThreadingHTTPServer as _ThreadingHTTPServer


class BrowserFixtureServer(_ThreadingHTTPServer):
    request_queue_size = 128
