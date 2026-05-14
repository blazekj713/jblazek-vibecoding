import json
from typing import Any, Dict

import requests

from skills import CodeGenerationSkill, CodeReviewSkill, Skill


class MCPClient:
    def __init__(self, server_url: str, model: str) -> None:
        self.server_url = server_url
        self.model = model

    def call(self, messages: Any) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
        }
        response = requests.post(self.server_url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()


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
