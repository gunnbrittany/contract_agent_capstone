"""
=====================================================================
ORCHESTRATOR INTEGRATION BRIDGE
=====================================================================
PURPOSE:
  Demonstrates how agents (e.g. Policy Validation Agent, Risk Assessment
  Agent, or LangGraph Orchestrators) consume the 4 MCP tools to perform
  dynamic, policy-grounded contract analysis.

BEFORE (Hardcoded logic):
  Agents used static Python dicts (COMPANY_POLICIES) with hardcoded rules,
  making policy updates require code deploys and preventing precedent reuse.

AFTER (MCP + Knowledge Layer):
  Agents query the Knowledge Layer via standardized MCP tools:
    1. fetch_metadata() -> sets jurisdictional & contract-type context
    2. get_playbook_rule() -> retrieves authoritative policy constraints
    3. search_clause_library() -> compares against benchmark standard language
    4. search_prior_approved_clauses() -> checks historical precedents to adjust risk
=====================================================================
"""

import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import json
from typing import Dict, Any, List
from mcp.mcp_tools import (
    search_clause_library,
    get_playbook_rule,
    search_prior_approved_clauses,
    fetch_metadata
)


class MCPPolicyValidator:
    """
    Agent component that validates clauses dynamically using the Knowledge + MCP Layer.
    """

    def __init__(self, contract_type: str = "NDA", jurisdiction: str = "Delaware"):
        self.contract_type = contract_type
        self.jurisdiction = jurisdiction

    def validate_clause(self, clause_type: str, clause_content: str) -> Dict[str, Any]:
        """
        Validate a contract clause through the 4-step MCP retrieval pipeline:
          Step 1: Retrieve metadata & jurisdiction thresholds
          Step 2: Lookup governing playbook rule
          Step 3: Search benchmark clause library for comparison
          Step 4: Check historical approved precedents to adjust risk
        """
        # 1. Contextual Metadata
        metadata_str = fetch_metadata(
            contract_type=self.contract_type,
            clause_type=clause_type,
            jurisdiction=self.jurisdiction
        )

        # 2. Authoritative Playbook Rule
        playbook_rule_str = get_playbook_rule(
            rule_name=f"{clause_type.lower()}_policy",
            clause_type=clause_type
        )

        # 3. Benchmark Standard Clause
        benchmark_str = search_clause_library(
            query=clause_content,
            clause_type=clause_type
        )

        # 4. Historical Precedents
        precedents_str = search_prior_approved_clauses(
            clause_text=clause_content,
            contract_type=self.contract_type
        )

        # Evaluate risk dynamically based on retrieved context
        is_high_risk = False
        reasons = []

        if "survival" in clause_type.lower():
            lower_content = clause_content.lower()
            if any(term in lower_content for term in ["1 year", "2 year", "one (1)", "two (2)", "2 years", "two years"]):
                is_high_risk = True
                reasons.append("Survival period is less than the 3-year minimum required by playbook (pb_001).")

        if "liability" in clause_type.lower():
            if "indirect" in clause_content.lower() or "consequential" in clause_content.lower():
                is_high_risk = True
                reasons.append("Clause excludes consequential damages without legal counsel approval.")

        return {
            "clause_type": clause_type,
            "clause_content": clause_content,
            "contract_type": self.contract_type,
            "jurisdiction": self.jurisdiction,
            "metadata_context": metadata_str,
            "playbook_rule": playbook_rule_str,
            "benchmark_clauses": benchmark_str,
            "precedent_approved": precedents_str,
            "evaluation": {
                "flagged": is_high_risk,
                "reasons": reasons,
                "recommendation": "Escalate to Legal" if is_high_risk else "Compliant with Playbook"
            }
        }


def run_demo():
    """Run an end-to-end demonstration of the MCP Knowledge pipeline."""
    print("=" * 70)
    print("DEMO: MCP + KNOWLEDGE LAYER PIPELINE")
    print("=" * 70)

    validator = MCPPolicyValidator(contract_type="NDA", jurisdiction="California")

    sample_clause = (
        "The confidentiality obligations herein shall expire two (2) years "
        "following the execution date of this Agreement."
    )

    print("\nEvaluating Candidate Clause:")
    print(f"'{sample_clause}'\n")

    result = validator.validate_clause(
        clause_type="Survival",
        clause_content=sample_clause
    )

    print("--- 1. Context Metadata ---")
    print(result["metadata_context"])

    print("--- 2. Governing Playbook Rule ---")
    print(result["playbook_rule"])

    print("--- 3. Standard Clause Comparison ---")
    print(result["benchmark_clauses"])

    print("--- 4. Historical Precedent Search ---")
    print(result["precedent_approved"])

    print("--- Evaluation Result ---")
    print(f"Flagged: {result['evaluation']['flagged']}")
    print(f"Recommendation: {result['evaluation']['recommendation']}")
    for r in result['evaluation']['reasons']:
        print(f"  * {r}")


if __name__ == "__main__":
    run_demo()
