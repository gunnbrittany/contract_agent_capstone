"""
=====================================================================
TEST SUITE: Knowledge + MCP Layer
=====================================================================
OWNER: Brittany Gunn (Capstone Deliverable Verification)

Tests:
  1. Knowledge Store (RAG layer, semantic search, metadata filters)
  2. The 4 LangChain MCP Tools (Python interface for agent workflows)
  3. The Model Context Protocol (MCP) Server (JSON-RPC stdio interface)
  4. Orchestrator Integration (End-to-end dynamic policy validation)
=====================================================================
"""

import asyncio
import json
import os
import sys
import unittest

# Ensure repo root and backend are on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
for p in (root_dir, backend_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from knowledge.vector_store import KnowledgeStore, knowledge_store
from mcp.mcp_tools import (
    search_clause_library,
    get_playbook_rule,
    search_prior_approved_clauses,
    fetch_metadata,
    MCP_TOOLS,
)
from backend.mcp_layer.server import list_tools, call_tool
from backend.mcp_layer.orchestrator_integration import MCPPolicyValidator


class TestKnowledgeStore(unittest.TestCase):
    """Test the RAG vector store and semantic search capabilities."""

    def setUp(self):
        self.store = knowledge_store

    def test_search_clauses_returns_matches(self):
        results = self.store.search_clauses("confidential information and disclosure", n_results=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        first = results[0]
        self.assertIn("text", first)
        self.assertIn("metadata", first)
        self.assertIn("distance", first)

    def test_search_clauses_metadata_filtering(self):
        results = self.store.search_clauses(
            "termination notice",
            clause_type="Termination",
            n_results=2
        )
        self.assertIsInstance(results, list)
        for r in results:
            self.assertEqual(r["metadata"].get("clause_type"), "Termination")

    def test_get_playbook_rule_exact_lookup(self):
        result = self.store.get_playbook_rule("confidentiality_survival_minimum", "Survival")
        self.assertIsNotNone(result.get("rule"))
        self.assertIn("Confidentiality survival period", result["rule"])
        self.assertEqual(result["metadata"].get("severity"), "HIGH")

    def test_get_playbook_rule_missing(self):
        result = self.store.get_playbook_rule("non_existent_policy_xyz", "Unknown")
        self.assertIsNone(result.get("rule"))

    def test_search_approved_clauses_precedents(self):
        results = self.store.search_approved_clauses(
            "confidentiality five years",
            contract_type="NDA",
            n_results=2
        )
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["metadata"].get("contract_type"), "NDA")


class TestLangChainMCPTools(unittest.TestCase):
    """Test the 4 tools as callable LangChain agent tools."""

    def test_mcp_tools_registry(self):
        self.assertEqual(len(MCP_TOOLS), 4)
        tool_names = [t.name if hasattr(t, "name") else t.__name__ for t in MCP_TOOLS]
        self.assertIn("search_clause_library", tool_names)
        self.assertIn("get_playbook_rule", tool_names)
        self.assertIn("search_prior_approved_clauses", tool_names)
        self.assertIn("fetch_metadata", tool_names)

    def test_search_clause_library_output_format(self):
        output = search_clause_library("consequential damages exclusion", "Limitation of Liability")
        self.assertIsInstance(output, str)
        self.assertIn("standard clauses", output.lower())
        self.assertIn("Type:", output)
        self.assertIn("Risk:", output)

    def test_get_playbook_rule_output_format(self):
        output = get_playbook_rule("liability_cap_review", "Limitation of Liability")
        self.assertIsInstance(output, str)
        self.assertIn("POLICY RULE:", output)
        self.assertIn("CRITICAL", output)

    def test_search_prior_approved_clauses_output_format(self):
        output = search_prior_approved_clauses("aggregate liability capped at fees paid", "MSA")
        self.assertIsInstance(output, str)
        self.assertIn("precedent approved clauses", output.lower())
        self.assertIn("Approved By:", output)

    def test_fetch_metadata_output_format(self):
        output = fetch_metadata("NDA", "Indemnification", "California")
        self.assertIsInstance(output, str)
        self.assertIn("CONTRACT METADATA:", output)
        self.assertIn("California", output)
        self.assertIn("standard_risk_threshold: High", output)
        self.assertIn("requires_legal_review: True", output)


class TestMCPServer(unittest.IsolatedAsyncioTestCase):
    """Test the official MCP Server protocol handlers."""

    async def test_list_tools(self):
        tools = await list_tools()
        self.assertEqual(len(tools), 4)
        names = [t.name for t in tools]
        self.assertIn("search_clause_library", names)
        self.assertIn("get_playbook_rule", names)
        self.assertIn("search_prior_approved_clauses", names)
        self.assertIn("fetch_metadata", names)

    async def test_call_search_clause_library(self):
        resp = await call_tool("search_clause_library", {"query": "payment within 30 days"})
        self.assertEqual(len(resp), 1)
        data = json.loads(resp[0].text)
        self.assertEqual(data.get("tool"), "search_clause_library")
        self.assertEqual(data.get("status"), "ok")
        self.assertIsInstance(data.get("results"), list)

    async def test_call_search_clause_library_empty_query(self):
        resp = await call_tool("search_clause_library", {"query": ""})
        data = json.loads(resp[0].text)
        self.assertEqual(data.get("status"), "empty")
        self.assertIn("reason", data)

    async def test_call_get_playbook_rule(self):
        resp = await call_tool("get_playbook_rule", {"policy_id": "confidentiality_survival_minimum"})
        self.assertEqual(len(resp), 1)
        data = json.loads(resp[0].text)
        self.assertEqual(data.get("tool"), "get_playbook_rule")
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("rule", data)

    async def test_call_search_prior_approved_clauses(self):
        resp = await call_tool("search_prior_approved_clauses", {"query": "confidential information", "contract_type": "NDA"})
        self.assertEqual(len(resp), 1)
        data = json.loads(resp[0].text)
        self.assertEqual(data.get("tool"), "search_prior_approved_clauses")
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("precedents", data)

    async def test_call_fetch_metadata(self):
        resp = await call_tool("fetch_metadata", {
            "contract_type": "MSA",
            "clause_type": "Governing Law",
            "jurisdiction": "Delaware"
        })
        self.assertEqual(len(resp), 1)
        data = json.loads(resp[0].text)
        self.assertEqual(data.get("tool"), "fetch_metadata")
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data["metadata"]["contract_type"], "MSA")
        self.assertEqual(data["metadata"]["jurisdiction"], "Delaware")

    async def test_call_unknown_tool(self):
        resp = await call_tool("unknown_tool_test", {})
        data = json.loads(resp[0].text)
        self.assertEqual(data.get("status"), "error")
        self.assertIn("unknown tool", data.get("error", ""))


class TestOrchestratorIntegration(unittest.TestCase):
    """Test the end-to-end integration between agents and the MCP tools."""

    def test_non_compliant_clause_flagged(self):
        validator = MCPPolicyValidator(contract_type="NDA", jurisdiction="California")
        result = validator.validate_clause(
            clause_type="Survival",
            clause_content="The obligations shall expire two (2) years after execution."
        )
        self.assertTrue(result["evaluation"]["flagged"])
        self.assertEqual(result["evaluation"]["recommendation"], "Escalate to Legal")
        self.assertGreater(len(result["evaluation"]["reasons"]), 0)

    def test_compliant_clause_passes(self):
        validator = MCPPolicyValidator(contract_type="NDA", jurisdiction="Delaware")
        result = validator.validate_clause(
            clause_type="Survival",
            clause_content="The obligations of confidentiality shall survive termination for five (5) years."
        )
        self.assertFalse(result["evaluation"]["flagged"])
        self.assertEqual(result["evaluation"]["recommendation"], "Compliant with Playbook")


if __name__ == "__main__":
    unittest.main(verbosity=2)
