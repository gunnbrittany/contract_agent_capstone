"""MCP package initialization."""
from .mcp_tools import (
    search_clause_library,
    get_playbook_rule,
    search_prior_approved_clauses,
    fetch_metadata,
    MCP_TOOLS,
)

__all__ = [
    "search_clause_library",
    "get_playbook_rule",
    "search_prior_approved_clauses",
    "fetch_metadata",
    "MCP_TOOLS",
]
