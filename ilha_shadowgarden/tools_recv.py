# recebe POST do Studio (HttpService) e grava em _audit/<path> - so localhost, so para auditoria
import http.server, os, urllib.parse
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_audit")
class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        p = urllib.parse.unquote(self.path.lstrip("/"))
        p = p.replace("..", "_")
        dst = os.path.join(BASE, p)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        n = int(self.headers.get("Content-Length", 0))
        with open(dst, "wb") as f:
            f.write(self.rfile.read(n))
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
os.chdir(os.path.dirname(os.path.abspath(__file__)))
http.server.ThreadingHTTPServer(("127.0.0.1", 8774), H).serve_forever()
