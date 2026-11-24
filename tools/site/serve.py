"""Serve the site locally like GitHub Pages does for large files: with HTTP Range support.

Usage: python3 -I serve.py <site-dir> [port]   (default port 8001, bound to 127.0.0.1)

`python3 -m http.server` ignores Range headers, and Lichtblick streams the Errol bag with range requests.
"""
import http.server
import os
import re
import sys
from functools import partial


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.mcap': 'application/octet-stream', '.glb': 'model/gltf-binary', '.wasm': 'application/wasm',
                      '.foxe': 'application/zip', '.js': 'text/javascript'}

    def send_head(self):
        m = re.fullmatch(r'bytes=(\d*)-(\d*)', self.headers.get('Range', '').strip())
        path = self.translate_path(self.path)
        if not m or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        a, b = m.groups()
        start = int(a) if a else max(0, size - int(b))
        end = min(size - 1, int(b)) if a and b else size - 1
        if start >= size or start > end:
            self.send_error(416, 'Range Not Satisfiable')
            return None
        f = open(path, 'rb'); f.seek(start)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self._left = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, '_left', None)
        if left is None:
            return super().copyfile(source, outputfile)
        while left > 0:
            buf = source.read(min(1 << 16, left))
            if not buf:
                break
            outputfile.write(buf); left -= len(buf)
        self._left = None

    def end_headers(self):
        if self.headers.get('Range') is None:
            self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()


if __name__ == '__main__':
    site = sys.argv[1]; port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
    http.server.ThreadingHTTPServer(('127.0.0.1', port), partial(RangeHandler, directory=site)).serve_forever()
