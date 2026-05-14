import json
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Any


class MCPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path not in ("/mcp/codex", "/mcp/claude_code"):
            self._send_json({"error": "Neznámá MCP cesta."}, status=404)
            return

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json({"error": "Neplatné JSON tělo."}, status=400)
            return

        messages = payload.get("messages", [])
        prompt_text = self._extract_prompt(messages)
        result = self._build_result(prompt_text)
        self._send_json({"result": result})

    def _extract_prompt(self, messages: Any) -> str:
        if not isinstance(messages, list):
            return ""
        for message in reversed(messages):
            if isinstance(message, dict) and message.get("role") == "user":
                return message.get("content", "")
        return ""

    def _build_result(self, prompt_text: str) -> str:
        if self.path == "/mcp/codex":
            return self._codex_result(prompt_text)
        return self._claude_code_result(prompt_text)

    def _codex_result(self, prompt_text: str) -> str:
        if "refactor" in prompt_text.lower():
            return (
                "# Návrh refaktorizace:\n"
                "```python\n"
                "def add(a, b):\n"
                "    return a + b\n"
                "```\n"
                "Refaktorizoval jsem kód do čisté funkce s jasnou odpovědností."
            )
        if "funkci" in prompt_text.lower() or "kód" in prompt_text.lower():
            return (
                "# Generovaný kód:\n"
                "```python\n"
                "def greet(name: str) -> str:\n"
                "    return f\"Ahoj, {name}!\"\n"
                "```\n"
                "Funkce vrací přátelské pozdravení.",
            )
        return "Codex zpracoval zadání a navrhl kód podle popisu."

    def _claude_code_result(self, prompt_text: str) -> str:
        if "chybu" in prompt_text.lower() or "review" in prompt_text.lower():
            return (
                "# Review kódu:\n"
                "- Zkontrolujte pojmenování proměnných.\n"
                "- Rozdělte logiku do menších funkcí.\n"
                "- Přidejte typovou kontrolu a testy."
            )
        return (
            "# Analýza kódu:\n"
            "Agent zhodnotil postup a doporučil lepší strukturu, komentáře a testy."
        )

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server_address = (host, port)
    with HTTPServer(server_address, MCPRequestHandler) as httpd:
        print(f"Spouštím lokální MCP server na http://{host}:{port}")
        print("Podporované cesty: /mcp/codex, /mcp/claude_code")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
