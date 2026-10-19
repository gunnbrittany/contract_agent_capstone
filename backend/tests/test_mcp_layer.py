"""
=====================================================================
TEST SUITE: backend/mcp_layer
=====================================================================
OWNER: Brittany Gunn (Capstone Deliverable)
Re-exports and runs tests from tests/test_mcp_knowledge.py.
=====================================================================
"""

import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from tests.test_mcp_knowledge import (
    TestKnowledgeStore,
    TestLangChainMCPTools,
    TestMCPServer,
    TestOrchestratorIntegration,
)
import unittest

if __name__ == "__main__":
    unittest.main(verbosity=2)
