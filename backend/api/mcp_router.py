"""
=====================================================================
MCP LAYER REST API ROUTER
=====================================================================
OWNER: Brittany Gunn (Capstone Deliverable)

PURPOSE:
  Exposes the 4 Model Context Protocol (MCP) tools and knowledge store
  as REST endpoints for the React frontend, orchestrators, and testing UI.
=====================================================================
"""

import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Ensure root and backend are on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (root_dir, backend_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from mcp.mcp_tools import (
    search_clause_library,
    get_playbook_rule,
    search_prior_approved_clauses,
    fetch_metadata,
    MCP_TOOLS
)
from backend.mcp_layer.orchestrator_integration import MCPPolicyValidator
from knowledge.vector_store import knowledge_store
from knowledge.seed_knowledge import SAMPLE_CLAUSES, SAMPLE_PLAYBOOK, SAMPLE_APPROVED

router = APIRouter(prefix="/api/mcp", tags=["Knowledge + MCP Layer"])


# ── Request Models ───────────────────────────────────────────────────

class SearchClauseRequest(BaseModel):
    query: str
    clause_type: Optional[str] = None
    limit: int = 3


class PlaybookRuleRequest(BaseModel):
    rule_name: str
    clause_type: str = ""


class PrecedentRequest(BaseModel):
    clause_text: str
    contract_type: str = "NDA"
    limit: int = 3


class MetadataRequest(BaseModel):
    contract_type: str = "NDA"
    clause_type: str = "Confidentiality"
    jurisdiction: Optional[str] = None


class ValidateClauseRequest(BaseModel):
    clause_type: str = "Survival"
    clause_content: str
    contract_type: str = "NDA"
    jurisdiction: str = "California"


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/info")
def get_info():
    """Information about the Knowledge + MCP Layer capstone deliverable."""
    return {
        "layer": "Knowledge + MCP Layer (Phase 2)",
        "owner": "Brittany Gunn",
        "description": "Authoritative memory and governance layer connecting Agent Orchestrator to Legal Playbooks, Clause Library, Precedents, and Contextual Metadata.",
        "status": "operational",
        "tools_count": len(MCP_TOOLS),
        "tools": [
            {
                "name": "search_clause_library",
                "purpose": "Benchmark Comparison",
                "description": "Compare candidate clauses against standard/approved clauses using semantic search and clause_type filtering."
            },
            {
                "name": "get_playbook_rule",
                "purpose": "Authoritative Governance",
                "description": "Retrieve exact policy rules from the company legal playbook (targeted lookup, not fuzzy)."
            },
            {
                "name": "search_prior_approved_clauses",
                "purpose": "Precedent Search",
                "description": "Find historically approved precedent clauses to adjust and lower contract risk scores."
            },
            {
                "name": "fetch_metadata",
                "purpose": "Contextual Constraints",
                "description": "Retrieve jurisdiction-specific enforceability rules and contract metadata before ranking."
            }
        ]
    }


@router.get("/tools")
def list_mcp_tools():
    """List the 4 MCP tools with specifications."""
    return [
        {
            "name": "search_clause_library",
            "description": search_clause_library.description if hasattr(search_clause_library, "description") else "",
            "arguments": ["query", "clause_type"]
        },
        {
            "name": "get_playbook_rule",
            "description": get_playbook_rule.description if hasattr(get_playbook_rule, "description") else "",
            "arguments": ["rule_name", "clause_type"]
        },
        {
            "name": "search_prior_approved_clauses",
            "description": search_prior_approved_clauses.description if hasattr(search_prior_approved_clauses, "description") else "",
            "arguments": ["clause_text", "contract_type"]
        },
        {
            "name": "fetch_metadata",
            "description": fetch_metadata.description if hasattr(fetch_metadata, "description") else "",
            "arguments": ["contract_type", "clause_type", "jurisdiction"]
        }
    ]


@router.post("/tools/search_clause_library")
def api_search_clause(req: SearchClauseRequest):
    """Execute search_clause_library tool."""
    raw_output = search_clause_library(req.query, req.clause_type, limit=req.limit)
    structured = knowledge_store.search_clauses(req.query, req.clause_type, n_results=req.limit)
    return {
        "tool": "search_clause_library",
        "formatted_text": raw_output,
        "structured_results": structured
    }


@router.post("/tools/get_playbook_rule")
def api_get_playbook_rule(req: PlaybookRuleRequest):
    """Execute get_playbook_rule tool."""
    raw_output = get_playbook_rule(req.rule_name, req.clause_type)
    structured = knowledge_store.get_playbook_rule(req.rule_name, req.clause_type)
    return {
        "tool": "get_playbook_rule",
        "formatted_text": raw_output,
        "structured_rule": structured
    }


@router.post("/tools/search_prior_approved_clauses")
def api_search_precedents(req: PrecedentRequest):
    """Execute search_prior_approved_clauses tool."""
    raw_output = search_prior_approved_clauses(req.clause_text, req.contract_type)
    structured = knowledge_store.search_approved_clauses(req.clause_text, req.contract_type, n_results=req.limit)
    return {
        "tool": "search_prior_approved_clauses",
        "formatted_text": raw_output,
        "structured_precedents": structured
    }


@router.post("/tools/fetch_metadata")
def api_fetch_metadata(req: MetadataRequest):
    """Execute fetch_metadata tool."""
    raw_output = fetch_metadata(req.contract_type, req.clause_type, req.jurisdiction)
    return {
        "tool": "fetch_metadata",
        "formatted_text": raw_output
    }


@router.post("/validate-clause")
def api_validate_clause(req: ValidateClauseRequest):
    """Run full 4-step MCP pipeline to validate a candidate clause."""
    validator = MCPPolicyValidator(contract_type=req.contract_type, jurisdiction=req.jurisdiction)
    result = validator.validate_clause(
        clause_type=req.clause_type,
        clause_content=req.clause_content
    )
    return result


@router.get("/knowledge-base")
def api_get_knowledge_base():
    """Retrieve sample knowledge base contents."""
    return {
        "clauses": SAMPLE_CLAUSES,
        "playbook_rules": SAMPLE_PLAYBOOK,
        "approved_precedents": SAMPLE_APPROVED
    }
