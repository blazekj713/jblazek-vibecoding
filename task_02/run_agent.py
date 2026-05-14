import argparse
import json
import os
import sys

from subagents import CodingAgent


def load_config() -> dict:
    directory = os.path.dirname(__file__)
    config_path = os.path.join(directory, "agent_config.json")
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spustí lokální kódovacího agenta přes MCP subagent." 
    )
    parser.add_argument(
        "--agent",
        choices=["codex", "claude_code"],
        default="codex",
        help="Vyberte, který kódovací agent má zpracovat úkol.",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Popis úkolu, který má agent vyřešit.",
    )
    return parser.parse_args()


def main() -> int:
    config = load_config()
    args = parse_args()

    print(f"Používám agent: {args.agent}")
    print(f"Zadání: {args.task}\n")

    agent = CodingAgent(config)

    try:
        result = agent.run(args.agent, args.task)
        print("Výsledek:")
        print(result)
        return 0
    except Exception as exc:
        print("Chyba při spuštění agenta:", exc)
        print(
            "Ujistěte se, že běží MCP server. "
            "Spusťte nejprve `python mock_mcp_server.py`."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
