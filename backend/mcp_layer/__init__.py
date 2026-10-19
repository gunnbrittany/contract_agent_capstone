"""Knowledge + MCP Layer package initialization."""
from .server import server
from .tools import (
    search_clause_library,
    get_playbook_rule,
    search_prior_approved_clauses,
    fetch_metadata,
    MCP_TOOLS,
)

__all__ = [
    "server",
    "search_clause_library",
    "get_playbook_rule",
    "search_prior_approved_clauses",
    "fetch_metadata",
    "MCP_TOOLS",
]
