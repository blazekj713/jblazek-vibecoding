import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict


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
        prompt = prompt_text.lower()
        if "unit test" in prompt or "testy" in prompt or "pytest" in prompt:
            return (
                "# Generované testy\n"
                "```python\n"
                "import pytest\n\n"
                "from solution import calculate_discount\n\n"
                "def test_calculate_discount_full_price():\n"
                "    assert calculate_discount(100, 0) == 100\n\n"
                "def test_calculate_discount_with_rate():\n"
                "    assert calculate_discount(200, 0.25) == 150\n\n"
                "def test_calculate_discount_lower_bound():\n"
                "    assert calculate_discount(0, 0.2) == 0\n"
                "```\n"
                "Testy ověřují funkčnost počítání slevy pro běžné scénáře."
            )
        if "revize" in prompt or "upravit" in prompt or "zlepšit" in prompt:
            return (
                "# Aktualizovaný kód podle review\n"
                "```python\n"
                "def calculate_discount(price: float, discount_rate: float) -> float:\n"
                "    \"\"\"Vrátí cenu po uplatnění slevy.\"\"\"\n"
                "    if price < 0 or discount_rate < 0:\n"
                "        raise ValueError('Cena i sleva musí být nezáporné.')\n"
                "    final_price = price * (1 - discount_rate)\n"
                "    return round(final_price, 2)\n"
                "```\n"
                "Revidovaný kód přidal kontrolu vstupu a přesné zaokrouhlení výsledku."
            )
        return (
            "# Generovaný kód\n"
            "```python\n"
            "def calculate_discount(price: float, discount_rate: float) -> float:\n"
            "    \"\"\"Spočítá cenu po slevě.\"\"\"\n"
            "    return price * (1 - discount_rate)\n"
            "```\n"
            "Funkce vrací výslednou cenu po uplatnění slevy."
        )

    def _claude_code_result(self, prompt_text: str) -> str:
        prompt = prompt_text.lower()
        if "shrnutí požadavku" in prompt or "analyzuj" in prompt:
            return (
                "# Shrnutí požadavku\n"
                "1. Uživatel chce funkci, která vypočítá výslednou cenu po slevě.\n"
                "2. Výsledek by měl být přesný a validovat vstupy.\n"
                "3. Součástí má být testovací sada, která ověří běžné scénáře."
            )
        if "review" in prompt or "recenzi" in prompt or "kontrolu" in prompt:
            return (
                "# Review kódu\n"
                "- Kód funguje, ale doporučuji přidat kontrolu vstupních hodnot.\n"
                "- Uživatel očekává přesný výsledek, takže zaokrouhlení je výhodné.\n"
                "- Testy jsou správně navržené, ale chybí kontrola nulové ceny.\n"
                "- Doporučení: uprav kód podle komentářů a znovu schval.\n"
            )
        if "schválení" in prompt or "approval" in prompt or "konečný" in prompt:
            return (
                "# Finální schválení\n"
                "Kód i testy jsou připravené.\n"
                "Návrh je konzistentní, obsahuje validaci vstupů a ověřené testy.\n"
                "Výsledek doporučuji nasadit."
            )
        return (
            "# Analýza úkolu\n"
            "Agent zhodnotil zadaný úkol a doporučuje vytvořit funkci a testy."
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
