# LLM-MAS-Finance-Architecture

> Companion repository for the paper *"Evolution Pathways of LLM-based Multi-Agent Collaboration Systems and a Four-Layer Reference Architecture for Financial Intelligence Applications: A Reference Architecture, Evolution Taxonomy, and Synthesized Empirical Analysis"* (EAAI submission, 2026).

This repository provides reference implementations, schemas, and benchmark reproduction scripts for the **four-layer reference architecture (L1 Model / L2 Capability / L3 Collaboration / L4 Governance)** and the **seven-dimensional evaluation framework** introduced in the paper.

## Repository Contents

| Directory | Contents |
|---|---|
| [`docs/`](docs/) | Architecture, evolution-model, and evaluation-framework specifications |
| [`src/`](src/) | Reference implementations in Python (LangGraph) and TypeScript (CrewAI) |
| [`schemas/`](schemas/) | Audit-log JSON schema, permission YAML templates, evaluation metric definitions |
| [`benchmarks/`](benchmarks/) | Reproduction scripts and raw data for the Golchian (2026) framework comparison and the Bertalanič (2026) cost-of-consensus ablation |
| [`compliance/`](compliance/) | L4 governance mapping to EU AI Act, GDPR, PIPL, and NIST AI RMF |
| [`figures/`](figures/) | All nine architecture and analysis diagrams (SVG + PNG) |
| [`.github/`](.github/) | Issue templates and CI workflows |

## Quick Start

```bash
git clone https://github.com/[your-org]/llm-mas-finance-architecture
cd llm-mas-finance-architecture
pip install -r requirements.txt
python src/l1_model.py        # run the L1 model-layer example
python src/l2_capability.py   # run the L2 capability-layer example
python src/l3_collaboration.py
python src/l4_governance.py
```

## What is the Four-Layer Architecture?

The paper proposes that production-grade LLM-based Multi-Agent Systems (MAS) for high-stakes domains (finance, healthcare, legal) should be decomposed into four orthogonal layers:

- **L1 Model Layer** — base LLM selection, tiered invocation, model routing
- **L2 Capability Layer** — tools, memory (short-term / long-term), retrieval-augmented generation
- **L3 Collaboration Layer** — orchestration topology (SOP, state machine, role-play, blackboard)
- **L4 Governance Layer** — permissions, audit, compliance, failure recovery, human-in-the-loop

The L4 layer is, to the best of our knowledge, the first work to formalize Governance as a **mandatory, runtime-enforced architectural layer** specifically for high-stakes MAS deployments. The paper shows that 76.5% of MAST-taxonomy failure modes (Cemri et al., 2025) can be mitigated by L4-style governance primitives.

## What is the Seven-Dimensional Evaluation Framework?

The paper proposes a standardized evaluation framework covering:

1. Task Completion Rate
2. Communication Cost (token overhead, latency)
3. Context Drift (CDS, Context Divergence Score)
4. Cumulative Return (financial)
5. Sharpe Ratio (financial)
6. Maximum Drawdown (financial)
7. Win Rate vs. Benchmarks (financial)

…plus three auxiliary indicators (Verification Pass Rate, Sycophantic Convergence Rate, Citation Coverage & Audit Completeness) tied directly to MAST failure categories. See [`docs/evaluation-framework.md`](docs/evaluation-framework.md) for metric definitions and reference implementations.

## Reproduced Benchmarks

The repository ships with two reproduced benchmark suites:

| Benchmark | Source | Status |
|---|---|---|
| Framework Comparison (LangGraph vs CrewAI vs AutoGen) | Golchian (2026) | ⚠️ Caveat: independent reproduction not yet established; see [`benchmarks/golchian_reproduction.md`](benchmarks/golchian_reproduction.md) |
| Cost of Consensus (homogeneous multi-agent debate) | Bertalanič (2026) | ✅ Script provided; raw data follows the original 2.1–3.4× token overhead with no accuracy gain |

## License

This repository is released under the **MIT License**. See [`LICENSE`](LICENSE).

The paper itself is © 2026 the authors, all rights reserved.

## Citation

If you use this architecture, evaluation framework, or benchmark reproductions, please cite the accompanying paper:

```bibtex
@misc{llm-mas-finance-architecture-2026,
  author       = {[Your Name]},
  title        = {Evolution Pathways of LLM-based Multi-Agent Collaboration Systems
                  and a Four-Layer Reference Architecture for Financial
                  Intelligence Applications: A Reference Architecture, Evolution
                  Taxonomy, and Synthesized Empirical Analysis},
  year         = {2026},
  eprint       = {TODO: insert arXiv ID after acceptance},
  archiveprefix = {arXiv},
  howpublished = {\url{https://github.com/[your-org]/llm-mas-finance-architecture}}
}
```

## Acknowledgments

This work synthesizes empirical findings from the open-source multi-agent community: MetaGPT, CrewAI, AutoGen, LangGraph, PilotDeck, TradingAgents, MASFIN, and FinSight. The MAST taxonomy (Cemri et al., 2025) underpins the failure-mode mapping in §6. The LangGraph framework-comparison benchmark (Golchian, 2026) and the cost-of-consensus benchmark (Bertalanič, 2026) provide the empirical data for the evaluation framework. We thank the maintainers of these projects for releasing reproducible code and data.
