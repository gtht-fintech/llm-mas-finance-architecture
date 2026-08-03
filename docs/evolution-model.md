# Four-Stage Evolution Model

The paper proposes a **four-stage evolution model** for LLM-based Multi-Agent Systems, charting the progression from 2023 H2 (MetaGPT) to 2026 H1 (Agent Operating Systems). This document specifies each stage with concrete framework exemplars and the dominant engineering tradeoff at each stage.

## Stage 1: Role-Driven Frameworks (2023 H1 - 2023 H4)

**Characteristic**: SOP (Standard Operating Procedure) encoded as Python code. Each agent is a class with a fixed role; communication is via a structured message-passing protocol.

**Exemplar frameworks**:
- **MetaGPT** (Hong et al., 2023, arXiv:2308.00352) — "SOP-as-code" pattern, 60k+ GitHub stars
- **CAMEL** (Li et al., 2023, arXiv:2303.17760) — Inception-prompting, role-play with two-agent inception

**Dominant tradeoff**: Determinism vs flexibility. SOP-encoded workflows are deterministic and auditable, but cannot adapt to unforeseen task types. Every new task requires code changes to the SOP.

**Key publications**:
- Hong et al. (2023). "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework." arXiv:2308.00352
- Li et al. (2023). "CAMEL: Communicative Agents for 'Mind' Exploration of Large Language Model Society." arXiv:2303.17760

## Stage 2: Role-Plus-Tool Coordination (2024 H1 - 2024 H4)

**Characteristic**: Dynamic role assignment plus structured tool invocation. Agents can be spawned at runtime, and each agent can call external tools (search, code execution, APIs).

**Exemplar frameworks**:
- **AutoGen** (Wu et al., 2023, arXiv:2308.08155) — Group chat with dynamic speaker selection
- **CrewAI** — Role-based, tool-rich, native Python decorator for tool registration

**Dominant tradeoff**: Flexibility vs predictability. Dynamic role assignment enables adaptation but makes the system harder to debug, audit, and reproduce.

**Key publications**:
- Wu et al. (2023). "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155

## Stage 3: State-Managed Systems (2024 H3 - 2025 H4)

**Characteristic**: Explicit state machine. The orchestration topology is a directed graph with named states and explicit transitions. State can be inspected, replayed, and branched (human-in-the-loop).

**Exemplar frameworks**:
- **LangGraph** — LangChain's state-machine-based orchestration; supports time-travel debugging, persistent state, and HITL interrupts
- **OpenAI Agents SDK** (2024-2024) — Handoffs, tracing, and persistent context

**Dominant tradeoff**: Auditability vs deployment complexity. State machines are auditable and reproducible, but the orchestration code is more verbose than SOP or role-play patterns.

**Key publications**:
- LangChain. "LangGraph: Building Stateful, Multi-Actor Applications with LLMs." (Product documentation, 2024)

## Stage 4: Agent Operating Systems (2025 H4 - 2026 H1, emerging)

**Characteristic**: The orchestration layer converges with operating-system concepts: process isolation, memory management, I/O scheduling, permission gates, and observability hooks. Frameworks at this stage begin to look more like OS kernels than agent libraries.

**Exemplar frameworks** (in development or early production):
- **PilotDeck** — Pilot deployment of a finance-domain Agent OS; integrates L1-L4 governance as first-class
- **AgentOS** — A proposed abstraction over LangGraph + CrewAI + AutoGen; position paper at NeurIPS 2025 Workshop
- **Anthropic Claude Tool Use + Computer Use** — Treating the LLM as a process with explicit I/O contracts

**Dominant tradeoff**: Power vs adoption barrier. Agent OS patterns are powerful but require significant engineering investment to deploy correctly; smaller teams may prefer the simpler Stage 2/3 patterns.

**Key publications**:
- PilotDeck technical whitepaper (forthcoming, 2026)
- AgentOS position paper (NeurIPS 2025 Workshop on AI Engineering)

## Empirical Mapping to the MAST Failure Taxonomy

Each stage exhibits a characteristic failure-mode profile (per Cemri et al., 2025, arXiv:2503.13657):

| Stage | Dominant Failure Mode | Mitigation in Next Stage |
|---|---|---|
| 1. Role-Driven | Task verification failure (no explicit verification) | Add tool invocation (Stage 2) |
| 2. Role+Tool | Inter-agent non-coordination (dynamic roles without state) | Add state management (Stage 3) |
| 3. State-Managed | System design issues (no formal permission model) | Add governance (Stage 4) |
| 4. Agent OS | Remaining: single-agent reasoning errors, fact hallucination | Future: improved L1 base models |

## Diagram

See [`figures/fig2_evolution_roadmap.svg`](../figures/fig2_evolution_roadmap.svg) for a visual timeline of the four stages with example frameworks.
