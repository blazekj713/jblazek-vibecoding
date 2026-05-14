import json
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from skills import CodeGenerationSkill, CodeReviewSkill, Skill


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

    def execute(self, task: str) -> str:
        messages = self.skill.build_messages(task)
        response = self.client.call(messages)
        return response.get("result", "Žádný výsledek.")


class CodingAgent:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def create_subagent(self, agent_name: str) -> CodingSubagent:
        agent_config = self.config["agents"].get(agent_name)
        if agent_config is None:
            raise ValueError(f"Neznámý agent: {agent_name}")

        if agent_name == "codex":
            skill = CodeGenerationSkill(agent_config)
        else:
            skill = CodeReviewSkill(agent_config)

        client = MCPClient(agent_config["server_url"], agent_config["model"])
        return CodingSubagent(skill, client)

    def run(self, agent_name: str, task: str) -> str:
        subagent = self.create_subagent(agent_name)
        return subagent.execute(task)
