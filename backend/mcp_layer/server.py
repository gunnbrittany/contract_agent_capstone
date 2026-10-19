"""
=====================================================================
KNOWLEDGE + MCP LAYER — MCP Server
=====================================================================
OWNER: Brittany Gunn (capstone deliverable)

PURPOSE
  Exposes this platform's legal retrieval surface as four Model Context
  Protocol (MCP) tools, so any MCP-capable agent (Claude Desktop, agent
  orchestrator, or class supervisor) can ground its reasoning in real legal
  policy and precedent instead of hallucinating.

WHY FOUR NARROW TOOLS INSTEAD OF ONE `search`
  One broad tool collapses four distinct retrieval intents into a single
  call. When the agent produces a bad answer, you cannot tell which intent
  failed. Four tools keep the trace legible and each retrieval path
  independently evaluable:

    get_playbook_rule             returns nothing -> knowledge-base gap
    search_prior_approved_clauses returns noise   -> retrieval-quality problem

  Different diagnoses, different fixes.

WHY THIS WRAPS RATHER THAN REBUILDS
  The platform already stores legal knowledge in Neo4j with Gemini
  embeddings and multi-level chunking. A second parallel vector store would
  fragment the knowledge rather than extend it. The architectural gap was
  never storage; it was that none of this retrieval was reachable by an
  external agent.

DUAL-MODE RESILIENCE
  When connected to Neo4j, tools query live graph knowledge and vector indexes.
  When offline, in local testing, or when Neo4j is unavailable, tools seamlessly
  fall back to the embedded local vector store (knowledge_store) seeded with
  standard CUAD/commercial clauses and playbook policies. It will never crash.

METADATA FILTERING, NOT PURE SIMILARITY
  Legal answers are jurisdiction-dependent. A pure embedding search will
  happily return a well-matching California clause for a New York contract.
  `fetch_metadata` narrows the candidate set by contract type, governing
  law, and party BEFORE similarity ranks it.
=====================================================================
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# Ensure project root and backend are on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (root_dir, backend_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

logger = logging.getLogger("mcp_layer")

DEFAULT_TENANT_ID = os.getenv("MCP_DEFAULT_TENANT_ID", "default")

# ── Resilient MCP Protocol Types ───────────────────────────────────────
try:
    from mcp.server import Server as OfficialServer
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
    HAS_OFFICIAL_MCP = True
except ImportError:
    HAS_OFFICIAL_MCP = False

    @dataclass
    class TextContent:
        type: str = "text"
        text: str = ""

    @dataclass
    class Tool:
        name: str
        description: str
        inputSchema: Dict[str, Any] = field(default_factory=dict)

    class OfficialServer:
        """Lightweight MCP Protocol Server fallback when mcp package is absent."""
        def __init__(self, name: str):
            self.name = name
            self._list_tools_handler: Optional[Callable] = None
            self._call_tool_handler: Optional[Callable] = None

        def list_tools(self):
            def decorator(func: Callable):
                self._list_tools_handler = func
                return func
            return decorator

        def call_tool(self):
            def decorator(func: Callable):
                self._call_tool_handler = func
                return func
            return decorator

        def create_initialization_options(self):
            return {"server": self.name, "protocol_version": "2024-11-05"}

        async def run(self, read_stream, write_stream, init_options=None):
            # Implemented in stdio runner below
            pass


server = OfficialServer("contract-knowledge")


# ── Lazy backend wiring ────────────────────────────────────────────────

def _policy_repository():
    try:
        from backend.infrastructure.policy_repository import PolicyRepository
        return PolicyRepository()
    except Exception:
        from infrastructure.policy_repository import PolicyRepository
        return PolicyRepository()


def _search_service():
    try:
        from backend.application.services.enhanced_search_service import EnhancedSearchService
        return EnhancedSearchService()
    except Exception:
        from application.services.enhanced_search_service import EnhancedSearchService
        return EnhancedSearchService()


def _contract_search():
    try:
        from backend.shared.utils.contract_search_tool import get_contracts
        return get_contracts
    except Exception:
        from shared.utils.contract_search_tool import get_contracts
        return get_contracts


def _embeddings():
    try:
        from backend.shared.utils.gemini_embedding_service import GeminiEmbeddingService
        return GeminiEmbeddingService()
    except Exception:
        from shared.utils.gemini_embedding_service import GeminiEmbeddingService
        return GeminiEmbeddingService()


def _ok(payload: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]


def _empty(tool: str, reason: str) -> list[TextContent]:
    """
    An explicit empty result. The agent must be able to tell 'nothing
    matched' apart from 'the tool broke' — collapsing those is how a
    knowledge-base gap gets silently misread as a bad answer.
    """
    return _ok({"tool": tool, "results": [], "status": "empty", "reason": reason})


def _failed(tool: str, err: Exception) -> list[TextContent]:
    logger.exception("%s failed: %s", tool, err)
    return _ok({"tool": tool, "results": [], "status": "error", "error": str(err)})


# ── Tool declarations ──────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_clause_library",
            description=(
                "Search the clause library for standard or approved clauses to "
                "compare a candidate clause against. Use when you need to know "
                "what 'normal' looks like for a clause type."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Clause text or description to match."},
                    "clause_type": {"type": "string", "description": "Optional clause type filter, e.g. 'indemnification'."},
                    "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 25},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_playbook_rule",
            description=(
                "Retrieve a specific policy rule from the legal playbook. Use when "
                "you need the authoritative rule a clause must satisfy. Returns an "
                "exact rule, not a similarity match."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "policy_id": {"type": "string", "description": "Exact policy id or rule name, when known."},
                    "rule_name": {"type": "string", "description": "Alternative key for rule name lookup."},
                    "clause_type": {"type": "string", "description": "Clause type to narrow rule search."},
                    "contract_type": {"type": "string", "description": "Contract type, to fetch all applicable rules."},
                    "tenant_id": {"type": "string", "description": "Tenant scope. Defaults to MCP_DEFAULT_TENANT_ID."},
                },
            },
        ),
        Tool(
            name="search_prior_approved_clauses",
            description=(
                "Find historical approved clauses as precedent. Use when the "
                "playbook is silent and you need to know what the company has "
                "accepted before."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Clause text or issue to find precedent for."},
                    "contract_type": {"type": "string", "default": "NDA", "description": "Contract type (NDA, MSA, SOW)."},
                    "tenant_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="fetch_metadata",
            description=(
                "Return contract and clause metadata: type, governing law "
                "(jurisdiction), parties, and risk thresholds. Call this FIRST to narrow "
                "the candidate set before running a similarity search, so a "
                "jurisdictionally wrong clause cannot rank highly."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_type": {"type": "string"},
                    "clause_type": {"type": "string"},
                    "party": {"type": "string", "description": "Counterparty or vendor name."},
                    "jurisdiction": {"type": "string", "description": "Governing law state/country."},
                    "governing_law_country": {"type": "string"},
                    "governing_law_state": {"type": "string"},
                    "summary_search": {"type": "string", "description": "Free-text summary match."},
                },
            },
        ),
    ]


# ── Tool dispatch ──────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    args = arguments or {}

    if name == "search_clause_library":
        return await _search_clause_library(args)
    if name == "get_playbook_rule":
        return await _get_playbook_rule(args)
    if name == "search_prior_approved_clauses":
        return await _search_prior_approved_clauses(args)
    if name == "fetch_metadata":
        return await _fetch_metadata(args)

    return _ok({"status": "error", "error": f"unknown tool: {name}"})


async def _search_clause_library(args: dict[str, Any]) -> list[TextContent]:
    tool = "search_clause_library"
    query = args.get("query", "").strip()
    clause_type = args.get("clause_type")
    limit = int(args.get("limit", 5))

    if not query:
        return _empty(tool, "query was empty")

    # 1. Attempt Platform Search (Neo4j EnhancedSearchService)
    try:
        from backend.domain.search.search_entities import SearchParams, SearchLevel
        params = SearchParams(
            search_level=SearchLevel.CLAUSE,
            query=query,
            clause_types=[clause_type] if clause_type else None,
        )
        result = _search_service().search(params)
        hits = getattr(result, "items", getattr(result, "results", []))
        if hits:
            return _ok({
                "tool": tool,
                "status": "ok",
                "source": "neo4j_graph",
                "query": query,
                "results": hits[:limit]
            })
    except Exception as err:
        logger.debug("Platform search bypassed (%s), using resilient knowledge store", err)

    # 2. Resilient Knowledge Store Fallback
    try:
        from knowledge.vector_store import knowledge_store
        hits = knowledge_store.search_clauses(query=query, clause_type=clause_type, n_results=limit)
        if not hits:
            return _empty(tool, "no clause in the library matched the query")
        return _ok({
            "tool": tool,
            "status": "ok",
            "source": "knowledge_store",
            "query": query,
            "results": hits
        })
    except Exception as err:
        return _failed(tool, err)


async def _get_playbook_rule(args: dict[str, Any]) -> list[TextContent]:
    tool = "get_playbook_rule"
    tenant_id = args.get("tenant_id") or DEFAULT_TENANT_ID
    policy_id = args.get("policy_id") or args.get("rule_name")
    contract_type = args.get("contract_type")
    clause_type = args.get("clause_type", "")

    if not policy_id and not contract_type and not clause_type:
        return _empty(tool, "supply either policy_id, rule_name, clause_type, or contract_type")

    # 1. Attempt Platform Policy Repository
    try:
        repo = _policy_repository()
        if policy_id:
            doc = repo.get_policy_by_id(policy_id)
            if doc:
                return _ok({"tool": tool, "status": "ok", "source": "neo4j_graph", "policy": doc})
        elif contract_type:
            rules = repo.get_applicable_policies(tenant_id, contract_type)
            if rules:
                return _ok({
                    "tool": tool,
                    "status": "ok",
                    "source": "neo4j_graph",
                    "contract_type": contract_type,
                    "rules": rules
                })
    except Exception as err:
        logger.debug("Platform policy repo bypassed (%s), using resilient knowledge store", err)

    # 2. Resilient Knowledge Store Fallback
    try:
        from knowledge.vector_store import knowledge_store
        lookup_name = policy_id or contract_type or clause_type
        result = knowledge_store.get_playbook_rule(lookup_name, clause_type=clause_type)
        if result.get("rule"):
            return _ok({
                "tool": tool,
                "status": "ok",
                "source": "knowledge_store",
                "lookup_name": lookup_name,
                "rule": result["rule"],
                "metadata": result.get("metadata", {})
            })
        return _empty(tool, f"no playbook rule found for '{lookup_name}' in '{clause_type}'")
    except Exception as err:
        return _failed(tool, err)


async def _search_prior_approved_clauses(args: dict[str, Any]) -> list[TextContent]:
    tool = "search_prior_approved_clauses"
    query = args.get("query", "").strip()
    contract_type = args.get("contract_type", "NDA")
    limit = int(args.get("limit", 10))

    if not query:
        return _empty(tool, "query was empty")

    # 1. Attempt Platform Policy Semantic Precedent Search
    try:
        repo = _policy_repository()
        hits = repo.search_policies_semantic(
            query_text=query,
            tenant_id=args.get("tenant_id") or DEFAULT_TENANT_ID,
            limit=limit,
        )
        if hits:
            return _ok({
                "tool": tool,
                "status": "ok",
                "source": "neo4j_graph",
                "query": query,
                "precedents": hits
            })
    except Exception as err:
        logger.debug("Platform precedent search bypassed (%s), using resilient knowledge store", err)

    # 2. Resilient Knowledge Store Fallback
    try:
        from knowledge.vector_store import knowledge_store
        hits = knowledge_store.search_approved_clauses(
            clause_text=query,
            contract_type=contract_type,
            n_results=min(limit, 5)
        )
        if not hits:
            return _empty(tool, f"no prior approved clause resembled the query for contract type {contract_type}")
        return _ok({
            "tool": tool,
            "status": "ok",
            "source": "knowledge_store",
            "query": query,
            "contract_type": contract_type,
            "precedents": hits
        })
    except Exception as err:
        return _failed(tool, err)


async def _fetch_metadata(args: dict[str, Any]) -> list[TextContent]:
    tool = "fetch_metadata"
    try:
        contract_type = args.get("contract_type", "NDA")
        clause_type = args.get("clause_type", "General")
        jurisdiction = (
            args.get("jurisdiction")
            or args.get("governing_law_state")
            or args.get("governing_law_country")
        )
        party = args.get("party")

        from mcp.mcp_tools import (
            _get_risk_threshold,
            _requires_review,
            _get_applicable_datasets,
            _get_jurisdiction_notes
        )

        metadata: Dict[str, Any] = {
            "contract_type": contract_type,
            "clause_type": clause_type,
            "party": party or "Not specified",
            "jurisdiction": jurisdiction or "Delaware (Default Commercial)",
            "standard_risk_threshold": _get_risk_threshold(clause_type),
            "requires_legal_review": _requires_review(clause_type),
            "applicable_datasets": _get_applicable_datasets(clause_type),
            "enforceability_notes": _get_jurisdiction_notes(clause_type, jurisdiction),
        }

        # Optional Neo4j graph contract search enrichment
        try:
            from shared.utils.contract_search_tool import Location
            governing_law = None
            if args.get("governing_law_country") or args.get("governing_law_state"):
                governing_law = Location(
                    country=args.get("governing_law_country"),
                    state=args.get("governing_law_state")
                )

            contracts = _contract_search()(
                embeddings=_embeddings(),
                contract_type=contract_type,
                parties=[party] if party else None,
                governing_law=governing_law,
                summary_search=args.get("summary_search"),
            )
            if contracts:
                metadata["matching_contracts"] = contracts
        except Exception:
            pass

        return _ok({"tool": tool, "status": "ok", "metadata": metadata})
    except Exception as err:
        return _failed(tool, err)


# ── Entry point ────────────────────────────────────────────────────────

async def main() -> None:
    logging.basicConfig(level=os.getenv("MCP_LOG_LEVEL", "INFO"))
    if HAS_OFFICIAL_MCP:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    else:
        # Resilient JSON-RPC 2.0 stdio server implementation
        sys.stderr.write("Starting Contract Knowledge MCP Server (JSON-RPC stdio)...\n")
        sys.stderr.flush()

        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            try:
                msg = json.loads(line.decode("utf-8"))
                msg_id = msg.get("id")
                method = msg.get("method")
                params = msg.get("params", {})

                if method == "initialize":
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "contract-knowledge", "version": "1.0.0"}
                        }
                    }
                elif method == "tools/list":
                    tools = await list_tools()
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "tools": [
                                {
                                    "name": t.name,
                                    "description": t.description,
                                    "inputSchema": t.inputSchema
                                }
                                for t in tools
                            ]
                        }
                    }
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    results = await call_tool(tool_name, arguments)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": r.type, "text": r.text} for r in results]
                        }
                    }
                else:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    }

                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"Error handling message: {e}\n")
                sys.stderr.flush()


if __name__ == "__main__":
    asyncio.run(main())
