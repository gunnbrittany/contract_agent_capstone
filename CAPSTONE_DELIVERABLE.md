# Capstone Deliverable: Knowledge + MCP Layer

**Owner:** Brittany Gunn  
**Project:** Enterprise Multi-Agent Contract Intelligence Platform  
**Roadmap Position:** Phase 2 — Knowledge + MCP Layer  
**Deadline:** April 24, 2026  

---

## 1. Executive Summary

In enterprise contract review, LLMs cannot evaluate contracts against legal policy accurately if that knowledge is merely baked into model weights or left to prompt instructions. Doing so leads to hallucinations, missed policy breaches, and arbitrary risk assessments.

The **Knowledge + MCP Layer** acts as the authoritative memory and governance interface for the entire multi-agent platform. It connects the **Agent Orchestrator** to legal playbooks, clause benchmarks, and historical precedent data through standard **Model Context Protocol (MCP)** interfaces.

```
┌────────────────────────────────────────────────────────┐
│                   Agent Orchestrator                   │
│   (Clause Extraction, Policy Validation, Risk Agents)  │
└───────────────────────────┬────────────────────────────┘
                            │ (Calls MCP Tools)
┌───────────────────────────▼────────────────────────────┐
│                  Knowledge + MCP Layer                 │
│  ├── search_clause_library                             │
│  ├── get_playbook_rule                                 │
│  ├── search_prior_approved_clauses                     │
│  └── fetch_metadata                                    │
└─────────────┬────────────────────────────┬─────────────┘
              │ (Connected Mode)           │ (Standalone / Fallback)
┌─────────────▼──────────────┐ ┌───────────▼─────────────┐
│    Platform Neo4j Graph    │ │  Embedded Vector Store  │
│  - Gemini Embeddings       │ │  - Local Vector RAG     │
│  - Multi-level Chunking    │ │  - Standard Playbooks   │
│  - Graph Precedents        │ │  - Benchmark Clauses    │
└────────────────────────────┘ └─────────────────────────┘
```

---

## 2. The 4 MCP Tools Deep-Dive

| Tool | Purpose | What Knowledge It Retrieves | Why It Was Designed This Way |
|---|---|---|---|
| `search_clause_library` | Benchmark Comparison | Standard/approved clauses matching the candidate clause | Semantic vector search finds relevant clauses even when phrasing differs; metadata filtering (`clause_type`) narrows the search space to prevent noisy cross-clause comparisons. |
| `get_playbook_rule` | Authoritative Governance | Specific policy rule from the legal playbook (e.g. survival minimums, liability caps) | Exact lookup (not fuzzy search), because legal governance must be strictly grounded in actual company policy rather than model hallucination. |
| `search_prior_approved_clauses` | Precedent Lookup | Historically approved clauses negotiated in past contracts | Grounded in precedent: if a similar provision was approved before by Legal, risk score is reduced, preventing re-escalation of accepted patterns. |
| `fetch_metadata` | Contextual Filtering | Contract type, jurisdiction rules, enforceability nuances, and review triggers | Jurisdiction changes legality. Metadata filtering occurs **before** vector ranking so a California-specific rule cannot rank highly on a New York contract. |

---

## 3. Key Design Decisions

### A. Four Narrow Tools vs. One General `search`
- **Problem with 1 general tool**: Collapses distinct retrieval intents into a single prompt. If the agent returns an erroneous evaluation, it is impossible to diagnose whether the playbook rule was missing, the precedent search was noisy, or the benchmark comparison was misaligned.
- **Our 4-tool design**:
  - `get_playbook_rule` returning empty = **knowledge-base gap** (policy is missing).
  - `search_prior_approved_clauses` returning noise = **retrieval quality issue**.
  - Keeping them distinct makes execution traces legible, debuggable, and independently evaluable.

### B. Metadata Filtering Before Semantic Search
A pure embedding similarity search will happily return a well-matching California clause for a New York contract. However, legal enforceability is strictly jurisdictional (e.g., non-competes in California under Cal. Bus. & Prof. Code § 16600 vs. Delaware). `fetch_metadata` ensures constraints are applied before similarity ranking.

### C. Dual-Mode Resilience (Neo4j GraphRAG + Embedded Vector Store)
- **Connected Mode**: When running with live infrastructure, tools interface directly with Neo4j Aura, Gemini embeddings, and the platform's `EnhancedSearchService` and `PolicyRepository`.
- **Standalone Mode**: When evaluated offline, during classroom presentations, or in environments without live Neo4j credentials, tools seamlessly fall back to an embedded vector store (`knowledge_store`) pre-seeded with CUAD and commercial contract standards. The system will **never crash during an evaluation or demo**.

### D. Dual Interface: MCP Server & LangChain Agent Tools
- **External Orchestrators**: Exposes an MCP standard stdio server (`server.py`) for Claude Desktop, external supervisor agents, or CLI runners.
- **Python / LangGraph Agents**: Exposes `@tool` wrappers in `mcp/mcp_tools.py` (`MCP_TOOLS = [...]`) so teammates' agents can import and run them directly in Python.

---

## 4. Quick Verification & Demo Guide

### 1. Run the End-to-End Orchestrator Demo
Runs an end-to-end evaluation of a candidate clause through all 4 MCP tools:
```bash
python3 backend/mcp_layer/orchestrator_integration.py
```
**Expected Output:**
- Evaluates a 2-year confidentiality survival clause.
- Fetches metadata (California NDA).
- Fetches playbook rule `pb_001` (minimum 3 years required).
- Fetches standard 5-year NDA clause and precedent approvals.
- Automatically flags the clause as high risk: `"Survival period is less than the 3-year minimum required by playbook (pb_001)."`.

### 2. Run the Automated Test Suite
Runs the 19 unit and integration tests covering the store, tools, MCP server, and pipeline:
```bash
python3 -m unittest tests/test_mcp_knowledge.py -v
```
**Expected Output:**
```
Ran 19 tests in 0.033s
OK
```

### 3. Run the MCP Stdio Server
Starts the Model Context Protocol server over stdio for external MCP clients:
```bash
python3 -m backend.mcp_layer.server
```

---

## 5. Deliverable Artifact Directory

```
contract_agent_capstone/
├── knowledge/
│   ├── __init__.py               ← Knowledge package init
│   ├── vector_store.py           ← Dual-mode vector store (ChromaDB + Local RAG)
│   └── seed_knowledge.py         ← Seeder for clauses, playbooks, precedents
├── mcp/
│   ├── __init__.py               ← MCP package init
│   └── mcp_tools.py              ← 4 LangChain @tool definitions (MCP_TOOLS)
├── backend/
│   ├── knowledge/                ← Backend knowledge package re-export
│   ├── mcp_layer/
│   │   ├── __init__.py           ← MCP layer exports
│   │   ├── server.py             ← MCP stdio server (tools/list, tools/call)
│   │   ├── tools.py              ← Re-export of MCP tools
│   │   ├── orchestrator_integration.py ← Pipeline integration demo
│   │   └── README.md             ← Architecture & technical documentation
│   └── tests/
│       └── test_mcp_layer.py     ← Backend test discovery integration
├── tests/
│   └── test_mcp_knowledge.py     ← Complete 19-test automated test suite
└── CAPSTONE_DELIVERABLE.md       ← Complete presentation & deliverable pack
```
