# MCP Layer — Knowledge Retrieval Tools

**Owner:** Brittany Gunn · Capstone deliverable: Knowledge + MCP Layer (Phase 2)

## What this is

Four Model Context Protocol (MCP) tools that connect agent orchestrators to authoritative legal playbooks, benchmark clause libraries, precedent approvals, and contract metadata:

1. `search_clause_library` — Semantic comparison against standard/approved clauses.
2. `get_playbook_rule` — Targeted retrieval of authoritative legal rules from company playbooks.
3. `search_prior_approved_clauses` — Historical precedent search to evaluate and reduce risk.
4. `fetch_metadata` — Contract classification and jurisdictional compliance constraints.

## Key Design Decisions

### 1. Four narrow single-responsibility tools, not one general `search`

One broad tool collapses four different retrieval intents into a single call. When the agent returns an ungrounded answer, you cannot tell which intent failed. With four distinct tools, the execution trace is legible:

- `get_playbook_rule` returning nothing = **knowledge-base gap** (policy needs to be added).
- `search_prior_approved_clauses` returning noise = **retrieval-quality problem**.

Those have different fixes. Separating them also lets each retrieval path be evaluated independently.

### 2. Metadata filtering before vector similarity

Legal enforceability is jurisdiction-dependent. A pure embedding search will cheerfully return a well-matching California clause for a New York contract. `fetch_metadata` exists so contract type, governing law, and parties constrain the candidate set *before* similarity ranks it.

### 3. Dual-Mode Architecture: GraphRAG + Resilient Fallback

- **Connected Mode**: When Neo4j Aura is active, tools query `EnhancedSearchService`, `PolicyRepository`, and contract search graphs with Gemini embeddings.
- **Embedded Fallback Mode**: If Neo4j is offline or credentials are not supplied (e.g. during offline grading or class presentation), tools seamlessly fall back to an embedded vector store pre-seeded with CUAD and commercial contract provisions. **The system will never crash during a demo or evaluation.**

## Tool Mapping

| MCP tool | Primary Source (Graph) | Fallback Source (RAG) |
|---|---|---|
| `search_clause_library` | `EnhancedSearchService.search()` | `knowledge_store.search_clauses()` |
| `get_playbook_rule` | `PolicyRepository.get_policy_by_id()` | `knowledge_store.get_playbook_rule()` |
| `search_prior_approved_clauses` | `PolicyRepository.search_policies_semantic()` | `knowledge_store.search_approved_clauses()` |
| `fetch_metadata` | `get_contracts()` | `mcp_tools.fetch_metadata()` |

## Running the Server and Tools

### 1. Run MCP Server (Stdio JSON-RPC)
```bash
python3 -m backend.mcp_layer.server
```
The server communicates over standard stdio JSON-RPC, compatible with Claude Desktop, Cursor, and any MCP orchestrator.

### 2. Run Direct Agent Tools in Python
```python
from backend.mcp_layer import MCP_TOOLS, search_clause_library, get_playbook_rule

# Use directly in LangGraph or LangChain workflows
playbook_rule = get_playbook_rule.invoke({"rule_name": "confidentiality_survival_minimum", "clause_type": "Survival"})
```

### 3. Run the Orchestrator Pipeline Demo
```bash
python3 backend/mcp_layer/orchestrator_integration.py
```

### 4. Run the Verification Tests
```bash
python3 -m unittest tests/test_mcp_knowledge.py -v
```
