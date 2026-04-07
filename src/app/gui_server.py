import argparse
import json
import mimetypes
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.app.config import (
    DEFAULT_BET_SIZES,
    DEFAULT_FIM,
    DEFAULT_HISTORY,
    DEFAULT_INICIO,
    DEFAULT_PRESET_NAMES,
    DEFAULT_QTD,
    DEFAULT_SEED,
    DEFAULT_SEED_COUNT,
    FULL_BET_SIZES,
    FULL_PRESET_NAMES,
    REPORT_DIR,
    STATISTICAL_PRESETS,
)
from src.app.service import preview_backtest_workflow, run_backtest_workflow, run_future_workflow


ROOT_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"


def _default_options() -> dict:
    return {
        "qtd": DEFAULT_QTD,
        "tamanho_aposta": None,
        "tamanhos_aposta": list(DEFAULT_BET_SIZES),
        "history": DEFAULT_HISTORY,
        "inicio": DEFAULT_INICIO,
        "fim": DEFAULT_FIM,
        "seed": DEFAULT_SEED,
        "seed_count": DEFAULT_SEED_COUNT,
        "presets": list(DEFAULT_PRESET_NAMES),
        "completo": False,
        "future": False,
    }


def _build_config_payload() -> dict:
    defaults = _default_options()
    preview = preview_backtest_workflow(defaults)
    return {
        "defaults": defaults,
        "presets": sorted(STATISTICAL_PRESETS.keys()),
        "default_presets": list(DEFAULT_PRESET_NAMES),
        "bet_sizes": list(FULL_BET_SIZES),
        "default_bet_sizes": list(DEFAULT_BET_SIZES),
        "preview": preview["summary"],
        "full_presets": list(FULL_PRESET_NAMES),
    }


def _normalize_run_options(payload: dict) -> dict:
    defaults = _default_options()
    options = dict(defaults)
    options.update(payload)
    if options.get("tamanho_aposta") in ("", 0):
        options["tamanho_aposta"] = None
    if options.get("tamanho_aposta") is not None:
        options["tamanho_aposta"] = int(options["tamanho_aposta"])
    options["tamanhos_aposta"] = [
        int(value) for value in options.get("tamanhos_aposta", defaults["tamanhos_aposta"])
    ]
    options["qtd"] = int(options["qtd"])
    options["history"] = None if options.get("history") in ("", None) else int(options["history"])
    options["inicio"] = None if options.get("inicio") in ("", None) else int(options["inicio"])
    options["fim"] = None if options.get("fim") in ("", None) else int(options["fim"])
    options["seed"] = int(options["seed"])
    options["seed_count"] = int(options["seed_count"])
    options["completo"] = bool(options.get("completo", False))
    options["future"] = bool(options.get("future", False))
    options["presets"] = list(options.get("presets", defaults["presets"]))
    return options


def _report_url(path: str) -> str:
    report_path = Path(path).resolve()
    report_root = REPORT_DIR.resolve()
    relative = report_path.relative_to(report_root)
    return f"/reports/{relative.as_posix()}"


def _load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _build_response_payload(result: dict) -> dict:
    artifact_urls = {
        name: _report_url(path)
        for name, path in result["artifact_paths"].items()
    }
    payload = {
        "mode": result["mode"],
        "report_dir": str(result["report_dir"]),
        "artifact_paths": result["artifact_paths"],
        "artifact_urls": artifact_urls,
        "summary": result["summary"],
    }
    if "tickets_csv" in result:
        payload["tickets_csv"] = result["tickets_csv"]
        payload["tickets_csv_url"] = _report_url(result["tickets_csv"])
    markdown_path = result["artifact_paths"].get("markdown")
    if markdown_path:
        payload["markdown"] = _load_text(markdown_path)
    return payload


class GuiRequestHandler(BaseHTTPRequestHandler):
    server_version = "QulottoGUI/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path.startswith("/static/"):
            relative = parsed.path.removeprefix("/static/")
            self._serve_static_file(relative)
            return
        if parsed.path == "/api/config":
            self._send_json(_build_config_payload())
            return
        if parsed.path.startswith("/reports/"):
            relative = parsed.path.removeprefix("/reports/")
            self._serve_report_file(relative)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Rota nao encontrada.")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            self.send_error(HTTPStatus.NOT_FOUND, "Rota nao encontrada.")
            return

        try:
            payload = self._read_json_body()
            options = _normalize_run_options(payload)
            if options["future"]:
                result = run_future_workflow(options)
            else:
                result = run_backtest_workflow(options)
            self._send_json(_build_response_payload(result))
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(
                {
                    "error": str(exc),
                },
                status=HTTPStatus.BAD_REQUEST,
            )

    def log_message(self, format: str, *args) -> None:
        return

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw_body) if raw_body else {}

    def _serve_report_file(self, relative_path: str) -> None:
        requested_path = (REPORT_DIR / relative_path).resolve()
        report_root = REPORT_DIR.resolve()
        if report_root not in requested_path.parents and requested_path != report_root:
            self.send_error(HTTPStatus.FORBIDDEN, "Caminho invalido.")
            return
        if not requested_path.exists() or not requested_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo nao encontrado.")
            return
        content_type, _ = mimetypes.guess_type(requested_path.name)
        self._serve_file(requested_path, content_type or "application/octet-stream")

    def _serve_static_file(self, relative_path: str) -> None:
        requested_path = (STATIC_DIR / relative_path).resolve()
        static_root = STATIC_DIR.resolve()
        if static_root not in requested_path.parents and requested_path != static_root:
            self.send_error(HTTPStatus.FORBIDDEN, "Caminho invalido.")
            return
        if not requested_path.exists() or not requested_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo nao encontrado.")
            return
        content_type, _ = mimetypes.guess_type(requested_path.name)
        self._serve_file(requested_path, content_type or "application/octet-stream")

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo nao encontrado.")
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--browser", help="Navegador a abrir, por exemplo firefox ou chrome")
    parser.add_argument("--no-open", action="store_true")
    return parser.parse_args()


def _open_browser(url: str, browser_name: str | None) -> None:
    if browser_name:
        webbrowser.get(browser_name).open(url)
        return
    webbrowser.open(url)


def main() -> None:
    args = _parse_args()
    server = ThreadingHTTPServer((args.host, args.port), GuiRequestHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"GUI disponivel em: {url}")
    print(f"Projeto raiz: {ROOT_DIR}")
    if not args.no_open:
        try:
            _open_browser(url, args.browser)
        except webbrowser.Error as exc:
            print(f"Nao foi possivel abrir o navegador automaticamente: {exc}")
    server.serve_forever()


if __name__ == "__main__":
    main()
