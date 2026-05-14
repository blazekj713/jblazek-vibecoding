import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from skills import (
    CodeGenerationSkill,
    CodeReviewSkill,
    FinalApprovalSkill,
    RequirementAnalysisSkill,
    Skill,
    TestGenerationSkill,
)


class MCPClient:
    def __init__(self, server_url: str, model: str) -> None:
        self.server_url = server_url
        self.model = model

    def call(self, messages: Any) -> Dict[str, Any]:
        payload = json.dumps({"model": self.model, "messages": messages}, ensure_ascii=False)
        request = Request(
            self.server_url,
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except HTTPError as exc:
            raise RuntimeError(f"MCP server returned HTTP {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"Nelze se připojit k MCP serveru: {exc.reason}") from exc


class CodingSubagent:
    def __init__(self, skill: Skill, client: MCPClient) -> None:
        self.skill = skill
        self.client = client

    def execute(self, task: str, context: str = "") -> str:
        messages = self.skill.build_messages(task, context)
        response = self.client.call(messages)
        return response.get("result", "Žádný výsledek.")


class AgentOrchestrator:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.codex_config = config["agents"]["codex"]
        self.claude_config = config["agents"]["claude_code"]

    def _create_subagent(self, agent_config: Dict[str, str], skill: Skill) -> CodingSubagent:
        client = MCPClient(agent_config["server_url"], agent_config["model"])
        return CodingSubagent(skill, client)

    def _run(self, agent_config: Dict[str, str], skill: Skill, task: str, context: str = "") -> str:
        subagent = self._create_subagent(agent_config, skill)
        return subagent.execute(task, context)

    def execute(self, task: str, max_revisions: int = 2) -> Dict[str, str]:
        results: Dict[str, str] = {}

        results["requirement_summary"] = self._run(
            self.claude_config,
            RequirementAnalysisSkill(self.claude_config),
            task,
        )

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    self._run,
                    self.codex_config,
                    CodeGenerationSkill(self.codex_config),
                    task,
                    results["requirement_summary"],
                ): "code",
                executor.submit(
                    self._run,
                    self.codex_config,
                    TestGenerationSkill(self.codex_config),
                    task,
                ): "tests",
            }
            for future in futures:
                results[futures[future]] = future.result()

        for revision in range(1, max_revisions + 1):
            results["review"] = self._run(
                self.claude_config,
                CodeReviewSkill(self.claude_config),
                task,
                f"{results['code']}\n\n{results['tests']}",
            )
            if "doporučuji" not in results["review"].lower() and "upravit" not in results["review"].lower():
                break

            results[f"revision_{revision}"] = self._run(
                self.codex_config,
                CodeGenerationSkill(self.codex_config),
                task,
                f"Review a požadavky na úpravu: {results['review']}",
            )
            results["code"] = results[f"revision_{revision}"]

        results["final_approval"] = self._run(
            self.claude_config,
            FinalApprovalSkill(self.claude_config),
            task,
            f"Kód:\n{results['code']}\n\nTesty:\n{results['tests']}\n\nReview:\n{results['review']}",
        )
        return results


class CodingAgent:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.orchestrator = AgentOrchestrator(config)

    def run_workflow(self, task: str) -> Dict[str, str]:
        return self.orchestrator.execute(task)
