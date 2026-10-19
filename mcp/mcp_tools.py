"""
=====================================================================
MCP LAYER: Contract Review Tools
=====================================================================
PURPOSE:
  Defines the 4 MCP tools the agent orchestrator uses to retrieve
  legal knowledge during contract analysis. Each tool is a focused,
  single-responsibility function that agents call via MCP or directly
  as LangChain/LangGraph tools.

WHY MCP FOR THIS:
  MCP standardizes how agents access external data and tools.
  Instead of hardcoding retrieval logic inside each agent, MCP lets
  any agent call these tools without knowing HOW they work internally.
  This is the separation of concerns that makes the system maintainable.

TOOL DESIGN PRINCIPLE:
  4 sharp tools beats 20 general ones. Each tool does one thing well:
    1. search_clause_library: Compare candidate clause against standard benchmark
    2. get_playbook_rule: Exact policy rule lookup (governance grounding)
    3. search_prior_approved_clauses: Precedent search to assess historical risk
    4. fetch_metadata: Jurisdiction, contract type, and vendor contextual filters
=====================================================================
"""

import os
import sys
from typing import Optional, List, Dict, Any, Callable

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from knowledge.vector_store import knowledge_store

# ── Resilient tool decorator (supports both LangChain invoke and direct Python call) ──
def callable_tool(func: Callable) -> Callable:
    try:
        from langchain_core.tools import tool as lc_tool
        t = lc_tool(func)
        class CallableTool:
            def __init__(self, tool_obj, py_func):
                self._tool = tool_obj
                self._func = py_func
                self.name = getattr(tool_obj, "name", py_func.__name__)
                self.description = getattr(tool_obj, "description", py_func.__doc__ or "")
                self.__name__ = py_func.__name__
                self.__doc__ = py_func.__doc__

            def __call__(self, *args, **kwargs):
                return self._func(*args, **kwargs)

            def __getattr__(self, name):
                return getattr(self._tool, name)

            def __repr__(self):
                return f"<Tool: {self.name}>"

        return CallableTool(t, func)
    except Exception:
        func.name = func.__name__
        func.description = func.__doc__ or ""
        return func


@callable_tool
def search_clause_library(query: str, clause_type: Optional[str] = None, limit: int = 3) -> str:
    """
    Search the clause library for standard and approved clauses similar
    to the clause being reviewed.

    Use this tool when you need to compare a contract clause against
    known-good standard language to identify deviations.

    Args:
        query: The clause text or description to search for
        clause_type: Optional filter (e.g., 'Confidentiality', 'Termination',
                     'Limitation of Liability', 'Indemnification')
        limit: Maximum number of clauses to return (default 3)

    Returns:
        Top matching standard clauses with risk metadata
    """
    # 1. Try Platform Search (Neo4j EnhancedSearchService) if available
    try:
        from backend.domain.search.search_entities import SearchParams, SearchLevel
        from backend.application.services.enhanced_search_service import EnhancedSearchService

        params = SearchParams(
            search_level=SearchLevel.CLAUSE,
            query=query,
            clause_types=[clause_type] if clause_type else None
        )
        service = EnhancedSearchService()
        result = service.search(params)
        items = getattr(result, "items", getattr(result, "results", []))
        if items:
            output = f"Found {len(items[:limit])} matching clauses in Graph Knowledge Store:\n\n"
            for i, r in enumerate(items[:limit], 1):
                text = r.get("content") or r.get("text") or str(r)
                output += f"[{i}] {text}\n"
                output += f"    Type: {r.get('clause_type', clause_type or 'General')}\n"
                output += f"    Risk: {r.get('risk_level', 'Medium')}\n\n"
            return output
    except Exception:
        pass  # Fall back seamlessly to local knowledge store

    # 2. Local Knowledge Store (ChromaDB / Vector RAG)
    results = knowledge_store.search_clauses(
        query=query,
        clause_type=clause_type,
        n_results=limit
    )

    if not results:
        return "No matching clauses found in the library."

    output = f"Found {len(results)} relevant standard clauses:\n\n"
    for i, r in enumerate(results, 1):
        output += f"[{i}] {r['text']}\n"
        output += f"    Type: {r['metadata'].get('clause_type', 'Unknown')}\n"
        output += f"    Risk: {r['metadata'].get('risk_level', 'Unknown')}\n"
        output += f"    Source: {r['metadata'].get('source', 'Unknown')}\n"
        if r.get('distance') is not None:
            similarity = round(max(0.0, 1.0 - r['distance']) * 100, 1)
            output += f"    Similarity: {similarity}%\n"
        output += "\n"
    return output


@callable_tool
def get_playbook_rule(rule_name: str, clause_type: str = "") -> str:
    """
    Retrieve a specific legal playbook rule that governs how a clause
    type should be handled.

    Use this tool when you need to check whether a clause violates
    a specific company policy or legal standard.

    Args:
        rule_name: The name of the policy rule (e.g., 'confidentiality_survival_minimum',
                   'liability_cap_review', 'termination_notice_minimum')
        clause_type: The type of clause being checked

    Returns:
        The policy rule text and enforcement metadata
    """
    # 1. Try Platform Policy Repository if available
    try:
        from backend.infrastructure.policy_repository import PolicyRepository
        repo = PolicyRepository()
        doc = repo.get_policy_by_id(rule_name)
        if doc and hasattr(doc, "rules") and doc.rules:
            r = doc.rules[0]
            return (
                f"POLICY RULE: {r.rule_text}\n"
                f"Rule Name: {rule_name}\n"
                f"Severity: {getattr(r, 'severity', 'HIGH')}\n"
                f"Applies To: {clause_type or 'General'}"
            )
    except Exception:
        pass

    # 2. Local Knowledge Store
    result = knowledge_store.get_playbook_rule(rule_name, clause_type)

    if not result.get("rule"):
        return f"No playbook rule found for '{rule_name}' in '{clause_type}' clauses."

    meta = result.get("metadata", {})
    return (
        f"POLICY RULE: {result['rule']}\n"
        f"Rule Name: {meta.get('rule_name', rule_name)}\n"
        f"Policy Owner: {meta.get('policy_owner', 'Legal')}\n"
        f"Severity: {meta.get('severity', 'HIGH')}\n"
        f"Applies To: {meta.get('clause_type', clause_type or 'General')}"
    )


@callable_tool
def search_prior_approved_clauses(clause_text: str, contract_type: str = "NDA") -> str:
    """
    Search historically approved clauses for precedents similar to
    the clause currently under review.

    Use this tool to determine if similar clause language has been
    approved before. High similarity to approved clauses reduces risk score.

    Args:
        clause_text: The full text of the clause being reviewed
        contract_type: The type of contract (e.g., 'NDA', 'MSA', 'SOW')

    Returns:
        Previously approved clauses with similar language and approval metadata
    """
    # 1. Try Platform Policy Semantic Search if available
    try:
        from backend.infrastructure.policy_repository import PolicyRepository
        repo = PolicyRepository()
        hits = repo.search_policies_semantic(query_text=clause_text, tenant_id="default", limit=3)
        if hits:
            output = f"Found {len(hits)} precedent approved policies:\n\n"
            for i, r in enumerate(hits, 1):
                output += f"[{i}] {r.get('rule_text')}\n"
                output += f"    Policy: {r.get('policy_name', 'Corporate Standard')}\n"
                output += f"    Severity: {r.get('severity', 'MEDIUM')}\n\n"
            return output
    except Exception:
        pass

    # 2. Local Knowledge Store
    results = knowledge_store.search_approved_clauses(
        clause_text=clause_text,
        contract_type=contract_type,
        n_results=3
    )

    if not results:
        return f"No prior approved clauses found for contract type: {contract_type}."

    output = f"Found {len(results)} precedent approved clauses:\n\n"
    for i, r in enumerate(results, 1):
        output += f"[{i}] {r['text']}\n"
        output += f"    Approved By: {r['metadata'].get('approved_by', 'Legal')}\n"
        output += f"    Date: {r['metadata'].get('approved_date', 'Unknown')}\n"
        output += f"    Status: {r['metadata'].get('precedent_status', 'Approved')}\n"
        if r.get('distance') is not None:
            similarity = round(max(0.0, 1.0 - r['distance']) * 100, 1)
            output += f"    Similarity: {similarity}%\n"
        output += "\n"
    return output


@callable_tool
def fetch_metadata(contract_type: str, clause_type: str, jurisdiction: Optional[str] = None) -> str:
    """
    Fetch contextual metadata for filtering and enriching contract analysis.

    Use this tool to retrieve classification metadata that helps agents
    make more accurate risk assessments based on contract context.

    Args:
        contract_type: Type of contract (e.g., 'NDA', 'MSA', 'SOW')
        clause_type: Type of clause (e.g., 'Indemnification', 'Governing Law', 'Limitation of Liability')
        jurisdiction: Optional legal jurisdiction (e.g., 'California', 'Delaware', 'New York')

    Returns:
        Metadata context including risk thresholds and compliance requirements
    """
    metadata = {
        "contract_type": contract_type,
        "clause_type": clause_type,
        "jurisdiction": jurisdiction or "Delaware (Default Commercial)",
        "standard_risk_threshold": _get_risk_threshold(clause_type),
        "requires_legal_review": _requires_review(clause_type),
        "applicable_datasets": _get_applicable_datasets(clause_type),
        "enforceability_notes": _get_jurisdiction_notes(clause_type, jurisdiction)
    }

    output = "CONTRACT METADATA:\n"
    for key, value in metadata.items():
        output += f"  {key}: {value}\n"
    return output


# ── Helper functions ────────────────────────────────────────────────

def _get_risk_threshold(clause_type: str) -> str:
    """Return the standard risk threshold for a clause type."""
    thresholds = {
        "Indemnification": "High — always flag for review",
        "Limitation of Liability": "High — flag if consequential damages excluded or cap < 1x fees",
        "Termination": "Medium — flag if notice period < 15 days",
        "Confidentiality": "Low — flag if survival period < 3 years",
        "Governing Law": "Low — flag if non-standard jurisdiction",
        "IP Ownership": "High — flag if pre-existing IP is assigned without carveout",
        "Payment Terms": "Medium — flag if net terms exceed 45 days"
    }
    return thresholds.get(clause_type, "Medium — evaluate against playbook")


def _requires_review(clause_type: str) -> bool:
    """Return whether this clause type always requires human legal review."""
    always_review = {"Indemnification", "Limitation of Liability", "IP Ownership"}
    return clause_type in always_review


def _get_applicable_datasets(clause_type: str) -> str:
    """Return the benchmark datasets most relevant to this clause type."""
    dataset_map = {
        "Indemnification": "CUAD (Category 12), LEDGAR",
        "Confidentiality": "CUAD (Category 4), ContractNLI",
        "Termination": "CUAD (Category 28), MAUD",
        "Limitation of Liability": "CUAD (Category 18), LEDGAR, ContractNLI",
        "Governing Law": "CUAD (Category 11), MAUD, ACORD",
        "IP Ownership": "CUAD (Category 15), LEDGAR",
        "Payment Terms": "CUAD (Category 21), SOW Corpus"
    }
    return dataset_map.get(clause_type, "CUAD (general commercial)")


def _get_jurisdiction_notes(clause_type: str, jurisdiction: Optional[str]) -> str:
    """Return legal enforceability nuances based on jurisdiction."""
    if not jurisdiction:
        return "Standard US commercial law applies (UCC / common law)."

    jur = jurisdiction.lower()
    if "california" in jur:
        if clause_type == "Non Compete/Solicit":
            return "Cal. Bus. & Prof. Code § 16600 void: non-competes strictly unenforceable."
        if clause_type == "Indemnification":
            return "California strict construction against indemnitee for sole negligence."
    elif "delaware" in jur:
        return "Delaware Court of Chancery strictly enforces contractual freedom and liability caps."
    elif "new york" in jur:
        return "New York law enforces mutual consequential damages waivers and strict breach notice."

    return f"Standard compliance rules for jurisdiction: {jurisdiction}."


# ── Export: list of tools for the agent to use ─────────────────────
MCP_TOOLS = [
    search_clause_library,
    get_playbook_rule,
    search_prior_approved_clauses,
    fetch_metadata
]
