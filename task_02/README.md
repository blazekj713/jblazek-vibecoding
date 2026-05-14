# Úkol 02: Nastavení kódovacího agenta (Codex | Claude Code)

## Cíl
Tento adresář obsahuje lokální demonstraci kódovacího agenta, který využívá:
- MCP server simulovaný v Pythonu
- oddělené skilly pro generování kódu a review
- subagenta, který orchestrace požadavky mezi skill a MCP

Všechno je implementováno bez použití pluginů nebo marketplace.

## Soubory
- `agent_config.json` – konfigurace MCP agentů a lokálního serveru
- `mock_mcp_server.py` – jednoduchý lokální MCP server pro `Codex` a `Claude Code`
- `skills.py` – definice skillů `CodeGenerationSkill` a `CodeReviewSkill`
- `subagents.py` – MCP klient, subagent a hlavní `CodingAgent`
- `run_agent.py` – spuštění agenta s konfigurovatelným vstupem

## Jak spustit
1. Spusťte lokální MCP server:
   ```bash
   python task_02/mock_mcp_server.py
   ```
2. V otevřeném druhém terminálu spusťte agenta s požadavkem:
   ```bash
   python task_02/run_agent.py --agent codex --task "Napiš funkci v Pythonu, která vypočítá faktoriál čísla."
   ```
3. Stejně tak lze použít `claude_code` pro analýzu a review:
   ```bash
   python task_02/run_agent.py --agent claude_code --task "Proveď review tohoto pseudo-kódu a popiš jeho silné stránky."
   ```

## Architektura
- `CodingAgent` vybírá z konfiguračního souboru `agent_config.json` odpovídajícího agenta.
- `CodingSubagent` spojuje vybraný skill a MCP klienta.
- `Skill` vytvoří prompt pro MCP server.
- `MCPClient` posílá zprávy na zadaný server.

## Popis nastavení
- `Codex` je definován jako agent pro generování a úpravy kódu.
- `Claude Code` je definován jako agent pro analýzu kódu a review.
- Oba jsou provozované lokálně přes `mock_mcp_server.py`.

## Poznámky
- V tomto řešení není použit žádný externí plugin nebo marketplace.
- Pokud chcete použít skutečný MCP server, upravte `agent_config.json` a nastavte `server_url` na reálný endpoint.
- Díky oddělení skillů a subagenta je možné přidat další agenty bez změny základní logiky.

