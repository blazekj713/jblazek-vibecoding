from abc import ABC, abstractmethod
from typing import Dict

class Skill(ABC):
    def __init__(self, config: Dict[str, str]):
        self.name = config.get("name", "unknown")
        self.description = config.get("description", "")
        self.model = config.get("model", "")

    @abstractmethod
    def build_prompt(self, task: str) -> str:
        raise NotImplementedError

    def build_messages(self, task: str):
        return [
            {
                "role": "system",
                "content": f"Jsi kódovací agent {self.name}. {self.description}",
            },
            {
                "role": "user",
                "content": self.build_prompt(task),
            },
        ]

class CodeGenerationSkill(Skill):
    def build_prompt(self, task: str) -> str:
        return (
            "Vytvoř nebo uprav kód na základě následujícího požadavku. "
            f"Uživatel chce: {task}"
        )

class CodeReviewSkill(Skill):
    def build_prompt(self, task: str) -> str:
        return (
            "Proveď review a analýzu kódu nebo návrhu, který je uveden níže. "
            f"Uživatel zadal: {task}"
        )
