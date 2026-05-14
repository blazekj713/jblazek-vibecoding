import argparse
import json
import os

from subagents import CodingAgent


def load_config() -> dict:
    directory = os.path.dirname(__file__)
    config_path = os.path.join(directory, "agent_config.json")
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spustí orchestraci více kódovacích agentů pro praktickou ukázku workflow."
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Popis úkolu, který má workflow vyřešit.",
    )
    return parser.parse_args()


def main() -> int:
    config = load_config()
    args = parse_args()

    print("Spouštím workflow agentské orchestrace:")
    print(f"Zadání: {args.task}\n")

    agent = CodingAgent(config)
    try:
        result = agent.run_workflow(args.task)
        print("=== Shrnutí požadavku ===")
        print(result["requirement_summary"], "\n")
        print("=== Generovaný kód ===")
        print(result["code"], "\n")
        print("=== Generované testy ===")
        print(result["tests"], "\n")
        print("=== Review ===")
        print(result["review"], "\n")
        print("=== Finální schválení ===")
        print(result["final_approval"])
        return 0
    except Exception as exc:
        print("Chyba při spuštění workflow:", exc)
        print("Ujistěte se, že běží MCP server: python mock_mcp_server.py")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
