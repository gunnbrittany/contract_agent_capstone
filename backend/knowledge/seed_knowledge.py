"""
=====================================================================
KNOWLEDGE SEEDER
=====================================================================
PURPOSE:
  Loads curated legal knowledge into the vector store.
  Includes standard clause libraries, legal playbook rules, and
  historically approved precedent clauses based on CUAD and commercial
  contract standards (NDA, MSA, SOW).

USAGE:
  cd backend && python -m knowledge.seed_knowledge
=====================================================================
"""

from typing import Any

# ── Sample Clause Library (Standard / Benchmark Clauses) ───────────
SAMPLE_CLAUSES = [
    {
        "id": "cl_001",
        "text": "Each party agrees to maintain the confidentiality of the other party's Confidential Information and not to disclose it to any third party without prior written consent, exercising at least reasonable care.",
        "metadata": {
            "clause_type": "Confidentiality",
            "contract_type": "NDA",
            "risk_level": "Low",
            "source": "standard_nda_template"
        }
    },
    {
        "id": "cl_002",
        "text": "The obligations of confidentiality shall survive termination of this Agreement for a period of five (5) years.",
        "metadata": {
            "clause_type": "Survival",
            "contract_type": "NDA",
            "risk_level": "Low",
            "source": "standard_nda_template"
        }
    },
    {
        "id": "cl_003",
        "text": "Either party may terminate this Agreement upon thirty (30) days written notice to the other party for any reason or no reason.",
        "metadata": {
            "clause_type": "Termination",
            "contract_type": "NDA",
            "risk_level": "Medium",
            "source": "standard_nda_template"
        }
    },
    {
        "id": "cl_004",
        "text": "In no event shall either party be liable for any indirect, incidental, special, exemplary, or consequential damages arising out of or related to this Agreement.",
        "metadata": {
            "clause_type": "Limitation of Liability",
            "contract_type": "NDA",
            "risk_level": "High",
            "source": "flagged_clause_library"
        }
    },
    {
        "id": "cl_005",
        "text": "Each party shall indemnify, defend, and hold harmless the other party and its officers from third-party claims arising out of gross negligence or willful misconduct.",
        "metadata": {
            "clause_type": "Indemnification",
            "contract_type": "MSA",
            "risk_level": "Medium",
            "source": "standard_msa_template"
        }
    },
    {
        "id": "cl_006",
        "text": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles.",
        "metadata": {
            "clause_type": "Governing Law",
            "contract_type": "MSA",
            "risk_level": "Low",
            "source": "standard_commercial_template"
        }
    },
    {
        "id": "cl_007",
        "text": "Invoices are payable within thirty (30) days of receipt by Customer. Undisputed past due amounts shall accrue interest at 1.0% per month.",
        "metadata": {
            "clause_type": "Payment Terms",
            "contract_type": "SOW",
            "risk_level": "Low",
            "source": "standard_sow_template"
        }
    },
    {
        "id": "cl_008",
        "text": "Client owns all deliverables created specifically for Client under this Statement of Work. Company retains all rights, title, and interest in and to its pre-existing IP, tools, and methodologies.",
        "metadata": {
            "clause_type": "IP Ownership",
            "contract_type": "SOW",
            "risk_level": "Low",
            "source": "standard_ip_carveout"
        }
    }
]

# ── Sample Legal Playbook Rules (Authoritative Governance) ─────────
SAMPLE_PLAYBOOK = [
    {
        "id": "pb_001",
        "text": "POLICY: Confidentiality survival period must be at least 3 years. Clauses with survival < 3 years are HIGH risk and non-compliant.",
        "metadata": {
            "rule_name": "confidentiality_survival_minimum",
            "clause_type": "Survival",
            "policy_owner": "Legal",
            "severity": "HIGH"
        }
    },
    {
        "id": "pb_002",
        "text": "POLICY: Limitation of Liability clauses that exclude ALL consequential damages or cap damages below 1x annual fees require Senior Legal Counsel review.",
        "metadata": {
            "rule_name": "liability_cap_review",
            "clause_type": "Limitation of Liability",
            "policy_owner": "Legal",
            "severity": "CRITICAL"
        }
    },
    {
        "id": "pb_003",
        "text": "POLICY: Termination notice periods under 15 days are HIGH risk. 30 days is standard. 60+ days is preferred for master agreements.",
        "metadata": {
            "rule_name": "termination_notice_minimum",
            "clause_type": "Termination",
            "policy_owner": "Legal",
            "severity": "HIGH"
        }
    },
    {
        "id": "pb_004",
        "text": "POLICY: Indemnification must be mutual and strictly limited to third-party IP infringement or gross negligence. Unilateral customer indemnification is prohibited.",
        "metadata": {
            "rule_name": "mutual_indemnification_mandate",
            "clause_type": "Indemnification",
            "policy_owner": "General Counsel",
            "severity": "CRITICAL"
        }
    },
    {
        "id": "pb_005",
        "text": "POLICY: Payment terms exceeding 45 days require Delivery Director and Finance approval. Net 30 is preferred company standard.",
        "metadata": {
            "rule_name": "payment_terms_approval",
            "clause_type": "Payment Terms",
            "policy_owner": "Finance",
            "severity": "MEDIUM"
        }
    },
    {
        "id": "pb_006",
        "text": "POLICY: Governing law must be Delaware, New York, or California. Non-US jurisdictions require Executive approval.",
        "metadata": {
            "rule_name": "governing_law_jurisdiction",
            "clause_type": "Governing Law",
            "policy_owner": "Legal",
            "severity": "MEDIUM"
        }
    },
    {
        "id": "pb_007",
        "text": "POLICY: Confidential Information must be kept confidential using at least reasonable care, and survival period must be at least 3 years.",
        "metadata": {
            "rule_name": "confidentiality_standard_policy",
            "clause_type": "Confidentiality",
            "policy_owner": "Legal",
            "severity": "HIGH"
        }
    }
]

# ── Sample Approved Clauses (Historical Precedents) ────────────────
SAMPLE_APPROVED = [
    {
        "id": "ap_001",
        "text": "Confidential Information shall be maintained in strict confidence for a period of five (5) years following the date of disclosure.",
        "metadata": {
            "clause_type": "Confidentiality",
            "contract_type": "NDA",
            "approved_by": "Legal (K. Venkatesan)",
            "approved_date": "2024-01-15",
            "precedent_status": "Approved"
        }
    },
    {
        "id": "ap_002",
        "text": "Except for breaches of confidentiality or gross negligence, each party's aggregate liability under this Agreement shall be limited to the total fees paid in the preceding twelve (12) months.",
        "metadata": {
            "clause_type": "Limitation of Liability",
            "contract_type": "MSA",
            "approved_by": "Senior Legal (B. Gunn)",
            "approved_date": "2024-03-20",
            "precedent_status": "Approved with Carveouts"
        }
    },
    {
        "id": "ap_003",
        "text": "Either party may terminate this Agreement without cause upon giving at least thirty (30) days prior written notice to the other party.",
        "metadata": {
            "clause_type": "Termination",
            "contract_type": "NDA",
            "approved_by": "Legal (Corporate)",
            "approved_date": "2024-02-10",
            "precedent_status": "Approved"
        }
    },
    {
        "id": "ap_004",
        "text": "Customer shall remit payment for undisputed invoice amounts within thirty (30) calendar days of invoice date.",
        "metadata": {
            "clause_type": "Payment Terms",
            "contract_type": "SOW",
            "approved_by": "Finance Ops",
            "approved_date": "2024-04-05",
            "precedent_status": "Approved"
        }
    }
]


def seed_to_store(target_store: Any):
    """Seed sample data into a given KnowledgeStore instance."""
    target_store.clause_library.add(
        ids=[c["id"] for c in SAMPLE_CLAUSES],
        documents=[c["text"] for c in SAMPLE_CLAUSES],
        metadatas=[c["metadata"] for c in SAMPLE_CLAUSES]
    )

    target_store.playbook.add(
        ids=[p["id"] for p in SAMPLE_PLAYBOOK],
        documents=[p["text"] for p in SAMPLE_PLAYBOOK],
        metadatas=[p["metadata"] for p in SAMPLE_PLAYBOOK]
    )

    target_store.approved_clauses.add(
        ids=[a["id"] for a in SAMPLE_APPROVED],
        documents=[a["text"] for a in SAMPLE_APPROVED],
        metadatas=[a["metadata"] for a in SAMPLE_APPROVED]
    )


def seed():
    """Load all sample data into the default knowledge store."""
    from .vector_store import knowledge_store
    print("Seeding clause library...")
    seed_to_store(knowledge_store)
    print("Done. Knowledge base is ready with standard clauses, playbook rules, and precedents.")


if __name__ == "__main__":
    seed()
