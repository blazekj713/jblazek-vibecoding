# Úkol 02_AE: Demonstrace agentské orchestrace (workflow | multi-agent)

## Cíl
Vytvořte projekt s praktickým použitím SDK pro kódovacích agentů. Cílem je, aby projekt demonstroval libovolnou orchestraci, tzn. workflow nebo multi-agent, a zároveň měl praktické použití.

- Kódovací agenti: Codex | Claude Code
- Workflow: Sekvenční | Paralelní | Loop | Conditional
- Multi-agent: Collaboration | Supervisor | Swarm

## Navržené řešení
Tento adresář obsahuje lokální demonstraci orchestrace mezi dvěma kódovacími agenty:

- `Codex` pro generování kódu a testů
- `Claude Code` pro analýzu, review a finální schválení

Orchestrace kombinuje:

- sekvenční krok: analýza požadavku -> generování -> review -> schválení
- paralelní krok: současné generování kódu a unit testů
- podmíněný loop: opakovaná revisní smyčka, pokud review navrhne změnu
- supervisor pattern: Claude Code jako konečný schvalovatel

## Struktura projektu
- `agent_config.json` – konfigurace agentů a lokálního MCP serveru
- `mock_mcp_server.py` – jednoduchý lokální MCP server pro `Codex` a `Claude Code`
- `skills.py` – definice specializovaných skillů pro každý krok workflow
- `subagents.py` – klient MCP, subagent a orchestrátor workflow
- `run_agent.py` – spouštění celé orchestrace s definovaným vstupem

## Jak spustit
1. Spusťte lokální MCP server:
   ```bash
   python task_02_AE/mock_mcp_server.py
   ```
2. Ve druhém terminálu spusťte orchestraci s úkolem:
   ```bash
   python task_02_AE/run_agent.py --task "Napiš funkci v Pythonu, která vypočítá cenu po slevě a vytvoř testy."
   ```

## Co demonstruje řešení
- `Codex` a `Claude Code` spolupracují jako tým agentů
- workflow obsahuje analýzu, generování, paralelní testy, review, loop a finální schválení
- architektura je rozšiřitelná: nové kroky lze přidat jako další skill a subagent
- řešení je plně lokální a nepotřebuje externí pluginy ani tržiště
