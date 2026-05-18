from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import cgi
import json
import os
import shutil
import time


APP_DIR = Path(os.environ.get("APP_DIR", "/app"))
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
HTML_FILE = APP_DIR / "stock-buscador.html"
STOCK_FILE = DATA_DIR / "stock.xlsx"
META_FILE = DATA_DIR / "stock.json"
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(100 * 1024 * 1024)))


class StockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            return self.send_file(HTML_FILE, "text/html; charset=utf-8")

        if self.path.startswith("/api/current"):
            if not STOCK_FILE.exists() or not META_FILE.exists():
                return self.send_text("No hay planilla cargada", status=404)
            return self.send_file(META_FILE, "application/json; charset=utf-8", no_cache=True)

        if self.path.startswith("/api/stock.xlsx"):
            if not STOCK_FILE.exists():
                return self.send_text("No hay planilla cargada", status=404)
            return self.send_file(
                STOCK_FILE,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                no_cache=True,
            )

        return self.send_text("No encontrado", status=404)

    def do_POST(self):
        if self.path != "/api/upload":
            return self.send_text("No encontrado", status=404)

        length = int(self.headers.get("content-length", "0"))
        if length <= 0:
            return self.send_text("Archivo vacio", status=400)
        if length > MAX_UPLOAD_BYTES:
            return self.send_text("La planilla supera el limite permitido", status=413)

        content_type = self.headers.get("content-type", "")
        if "multipart/form-data" not in content_type:
            return self.send_text("La subida debe ser multipart/form-data", status=400)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": str(length),
            },
        )

        field = form["stock"] if "stock" in form else None
        if field is None or not getattr(field, "filename", ""):
            return self.send_text("No recibi el archivo stock", status=400)
        if not field.filename.lower().endswith(".xlsx"):
            return self.send_text("El archivo debe ser .xlsx", status=400)

        tmp_file = DATA_DIR / "stock.xlsx.tmp"
        with tmp_file.open("wb") as output:
            shutil.copyfileobj(field.file, output)
        tmp_file.replace(STOCK_FILE)

        meta = {
            "name": Path(field.filename).name,
            "uploadedAt": int(time.time()),
            "size": STOCK_FILE.stat().st_size,
        }
        META_FILE.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        self.send_json(meta)

    def send_file(self, path, content_type, no_cache=False):
        if not path.exists():
            return self.send_text("No encontrado", status=404)

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if no_cache:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_text(self, text, status=200):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), StockHandler)
    print(f"Stock server listening on {port}", flush=True)
    server.serve_forever()
