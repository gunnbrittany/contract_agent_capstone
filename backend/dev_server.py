"""
=====================================================================
LOCAL FASTAPI DEVELOPMENT SERVER
=====================================================================
OWNER: Brittany Gunn (Capstone Deliverable)

PURPOSE:
  Serves the Knowledge + MCP Layer REST API along with contract search
  and intelligence mock routes so the entire platform can be run and
  tested in localhost with zero external database dependencies.
=====================================================================
"""

import os
import sys
from typing import Optional, List, Dict, Any

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.abspath(os.path.dirname(__file__))
for p in (root_dir, backend_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from backend.api.mcp_router import router as mcp_router
from knowledge.vector_store import knowledge_store

app = FastAPI(
    title="Contract Intelligence — Knowledge + MCP Platform",
    description="Multi-agent contract intelligence with Knowledge + MCP Layer by Brittany Gunn",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the Knowledge + MCP router
app.include_router(mcp_router)


# ── Companion Routes for Frontend Compatibility ──────────────────────

@app.get("/api/workflow/status")
def get_workflow_status():
    return {
        "status": "idle",
        "current_agent": None,
        "completed_agents": ["Knowledge + MCP Layer Active", "Playbook Engine Ready"],
        "total_agents": 4,
        "progress": 100
    }


@app.get("/api/contracts/search/clause-types")
def get_clause_types():
    return {
        "clause_types": [
            "Confidentiality",
            "Survival",
            "Termination",
            "Limitation of Liability",
            "Indemnification",
            "Governing Law",
            "Payment Terms",
            "IP Ownership"
        ]
    }


@app.get("/api/contracts/search/section-types")
def get_section_types():
    return {
        "section_types": [
            {"value": "preamble", "label": "Preamble", "description": "Parties and Effective Date"},
            {"value": "definitions", "label": "Definitions", "description": "Defined Terms"},
            {"value": "covenants", "label": "Covenants", "description": "Core Obligations"},
            {"value": "term_termination", "label": "Term & Termination", "description": "Duration and Exit"},
            {"value": "liability", "label": "Liability & Risk", "description": "Caps and Indemnities"},
            {"value": "boilerplate", "label": "Miscellaneous", "description": "Governing Law, Notices"}
        ]
    }


class EnhancedSearchBody(BaseModel):
    search_level: str
    query: Optional[str] = None
    clause_types: Optional[List[str]] = None
    section_types: Optional[List[str]] = None
    parties: Optional[List[str]] = None
    contract_type: Optional[str] = None
    active: Optional[bool] = None


@app.post("/api/contracts/search/enhanced")
def enhanced_search(body: EnhancedSearchBody):
    # Query KnowledgeStore
    query = body.query or "contract standard clause"
    clause_type = body.clause_types[0] if body.clause_types else None
    results = knowledge_store.search_clauses(query, clause_type=clause_type, n_results=5)
    
    formatted_items = [
        {
            "id": f"res_{i}",
            "content": r["text"],
            "clause_type": r["metadata"].get("clause_type", "General"),
            "contract_type": r["metadata"].get("contract_type", "Commercial"),
            "risk_level": r["metadata"].get("risk_level", "Low"),
            "similarity": round(max(0.0, 1.0 - (r["distance"] or 0.5)) * 100, 1)
        }
        for i, r in enumerate(results, 1)
    ]
    return {
        "success": True,
        "search_level": body.search_level,
        "results": formatted_items
    }


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    return {
        "document_id": f"doc_{file.filename}",
        "filename": file.filename,
        "status": "processed",
        "message": "Document parsed and indexed in Knowledge Store successfully."
    }


@app.get("/")
def root():
    return {
        "message": "Contract Intelligence Knowledge + MCP Server is Running",
        "mcp_layer_owner": "Brittany Gunn",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
