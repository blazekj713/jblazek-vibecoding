from abc import ABC, abstractmethod
from typing import Dict, List


class Skill(ABC):
    def __init__(self, config: Dict[str, str]) -> None:
        self.name = config.get("name", "unknown")
        self.description = config.get("description", "")
        self.model = config.get("model", "")

    @abstractmethod
    def build_prompt(self, task: str, context: str = "") -> str:
        raise NotImplementedError

    def build_messages(self, task: str, context: str = "") -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": f"Jsi kódovací agent {self.name}. {self.description}",
            },
            {
                "role": "user",
                "content": self.build_prompt(task, context),
            },
        ]


class RequirementAnalysisSkill(Skill):
    def build_prompt(self, task: str, context: str = "") -> str:
        return (
            "Shrň, co je v zadání nejdůležitější, a popiš hlavní kroky řešení.\n"
            f"Zadání: {task}"
        )


class CodeGenerationSkill(Skill):
    def build_prompt(self, task: str, context: str = "") -> str:
        prompt = (
            "Vytvoř kód podle následujícího zadání.\n"
            f"Zadání: {task}\n"
        )
        if context:
            prompt += f"Dodatečné informace:\n{context}\n"
        prompt += "Výstup by měl být včetně kompletní funkce v Pythonu."
        return prompt


class TestGenerationSkill(Skill):
    def build_prompt(self, task: str, context: str = "") -> str:
        return (
            "Napiš sadu jednotkových testů pro následující funkci.\n"
            f"Zadání: {task}\n"
            "Použij pytest a zahrň běžné i okrajové scénáře."
        )


class CodeReviewSkill(Skill):
    def build_prompt(self, task: str, context: str = "") -> str:
        return (
            "Proveď detailní review kódu a testů.\n"
            f"Kontext: {task}\n"
            f"Kód: {context}\n"
            "Uveď doporučení pro opravy a vylepšení."
        )


class FinalApprovalSkill(Skill):
    def build_prompt(self, task: str, context: str = "") -> str:
        return (
            "Jsi supervizor projektu. Zhodnoť finální řešení a rozhodni, zda je připravené k nasazení.\n"
            f"Kontext: {task}\n"
            f"Podklady: {context}\n"
            "Uveď stručné shrnutí a doporučení."
        )
