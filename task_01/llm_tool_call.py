import os
import json
import requests
import ast
import operator as op

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the environment variable OPENAI_API_KEY")

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"

# Bezpečný evaluátor výrazu pro jednoduché matematické výpočty.
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}


def safe_eval(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        operator = ALLOWED_OPERATORS[type(node.op)]
        return operator(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        operator = ALLOWED_OPERATORS[type(node.op)]
        return operator(operand)
    raise ValueError(f"Unsupported expression: {node}")


def calculate(expression: str) -> str:
    """Provede jednoduchý bezpečný výpočet aritmetického výrazu."""
    try:
        parsed = ast.parse(expression, mode="eval").body
        result = safe_eval(parsed)
        return str(result)
    except Exception as exc:
        return f"Chyba při výpočtu: {exc}"


def call_openai(messages, functions=None, function_call="auto"):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2,
        "function_call": function_call,
    }
    if functions is not None:
        payload["functions"] = functions

    authorization_value = f"Bearer {OPENAI_API_KEY}"
    try:
        authorization_value.encode("latin-1")
    except UnicodeEncodeError:
        raise ValueError(
            "OPENAI_API_KEY contains unsupported characters. "
            "Use a valid OpenAI API key without non-ASCII characters."
        )

    response = requests.post(
        OPENAI_API_URL,
        headers={
            "Authorization": authorization_value,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    messages = [
        {
            "role": "system",
            "content": "Jsi asistent, který může volat nástroj pro matematické výpočty a následně vrátit odpověď uživateli.",
        },
        {
            "role": "user",
            "content": "Vypočítej prosím výraz: 52 * (13 - 5) + 120 / 4.",
        },
    ]

    functions = [
        {
            "name": "calculate",
            "description": "Provádí matematické výpočty jednoduchých aritmetických výrazů.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Aritmetický výraz, který je potřeba vypočítat.",
                    }
                },
                "required": ["expression"],
            },
        }
    ]

    response = call_openai(messages, functions=functions)
    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        print(f"LLM požádal o volání nástroje: {function_name}")

        if function_name == "calculate":
            tool_result = calculate(function_args.get("expression", ""))
        else:
            tool_result = "Neznámý nástroj."

        messages.append(message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": tool_result,
            }
        )

        final_response = call_openai(messages, function_call="none")
        assistant_message = final_response["choices"][0]["message"]["content"]
        print("\nKonečná odpověď LLM:")
        print(assistant_message)
    else:
        print("LLM nepožádal o volání nástroje, odpověď:")
        print(message.get("content", ""))


if __name__ == "__main__":
    main()
