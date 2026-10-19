# Capstone — Completion Plan (supersedes the April guide)
**Written 2026-09-03.** The original `contract_agent_capstone_guide.md` is untouched and still
useful for the Git workflow. **Its build plan is stale** and following it will waste your time.

---

## What I found when I opened the actual repo

Repo: `~/AI Files/contract_agent_capstone` · remotes: `origin` = your GitHub,
`upstream` = karthikkv1981 · you are on branch `brittany_branch`.

| Check | Result |
|---|---|
| Commits by you | **Zero.** All 5 commits are Karthik Venkatesan's, dated 2026-03-23 |
| `brittany_branch` vs `upstream/main` | **Identical.** No diff, no unmerged work |
| `vector_store.py`, `mcp_tools.py`, `seed_knowledge.py` | **Do not exist**, here or anywhere on this machine |
| `search_clause_library` anywhere in code | **No.** It appears only in planning documents |
| Any MCP layer in the repo | **None** |

**So the capstone was never built.** The "~550 lines of production code" in the May 22 work
summary describes the *annotated Python inside the guide document*, not shipped code. That
distinction matters and it has already been corrected on the resumes.

**The good news:** the gap is real and the fix is small. Read on.

---

## Why the April guide cannot be followed

The guide told you to build a ChromaDB vector store from scratch. **The actual project does not
use ChromaDB.** It runs on:

- **Neo4j Aura** with vector indexing
- **Gemini** 1536-dimensional embeddings (`gemini-embedding-001`)
- LangChain + LangGraph, FastAPI backend, React/Vite frontend
- 11+ agents, a supervisor pattern, multi-level chunking, an advanced RAG agent with precedent lookup

Building a parallel ChromaDB store would **fragment the knowledge**, not extend it. It would
also be the wrong answer in your presentation.

---

## The revised deliverable

**The knowledge layer already exists. What is missing is that none of it is reachable by an
external agent.** That gap is exactly MCP-shaped, and it is your spec'd deliverable anyway:
four MCP tools.

So: **wrap, do not rebuild.** Your four tools map cleanly onto functions already in the repo.

| Your MCP tool | Wraps | File |
|---|---|---|
| `search_clause_library` | `EnhancedSearchService.search()` | `application/services/enhanced_search_service.py` |
| `get_playbook_rule` | `PolicyRepository.get_applicable_policies()` / `.get_policy_by_id()` | `infrastructure/policy_repository.py` |
| `search_prior_approved_clauses` | `PolicyRepository.search_policies_semantic()` | `infrastructure/policy_repository.py` |
| `fetch_metadata` | `get_contracts()` | `shared/utils/contract_search_tool.py` |

**The detail that makes the presentation:** `get_contracts()` already accepts `contract_type`,
`parties`, and `governing_law` — which is precisely the **type / vendor / jurisdiction** triple
your metadata tool was specified to return. The architecture was waiting for this layer.

---

## What I already wrote for you

Three files, in your repo, **local and uncommitted**:

```
backend/mcp_layer/__init__.py
backend/mcp_layer/server.py     ← the four tools, ~250 lines, compiles clean
backend/mcp_layer/README.md     ← the design rationale, in your words
```

Named `mcp_layer` and not `mcp` deliberately, so it does not shadow the `mcp` package import.

Two design decisions are implemented and commented in the code, because they are what you will
be asked about:

1. **Four narrow tools, not one `search`.** A failed `get_playbook_rule` is a knowledge-base
   gap; a noisy `search_prior_approved_clauses` is a retrieval-quality problem. Different
   diagnoses, different fixes. One broad tool destroys that signal.
2. **Empty is not the same as broken.** Every tool returns an explicit `status: empty` with a
   reason, distinct from `status: error`. An exact playbook miss never silently degrades into a
   similarity match presented as the rule.

---

## Your steps, in order

### 1. Sync your branch (it is 5 months stale)

```bash
cd ~/"AI Files"/contract_agent_capstone
git fetch upstream
git checkout brittany_branch
git merge upstream/main
```

### 2. Install the MCP SDK

```bash
cd ~/"AI Files"/contract_agent_capstone/backend
uv add mcp
```

### 3. Check your environment has Neo4j credentials

```bash
cd ~/"AI Files"/contract_agent_capstone/backend
grep -c NEO4J .env
```

If that prints `0`, the tools will return `status: error` and you need credentials from the
team before the demo will work.

### 4. Start the server

```bash
cd ~/"AI Files"/contract_agent_capstone/backend
uv run python -m mcp_layer.server
```

It speaks MCP over stdio and will sit there waiting for a client. That is correct behavior, not
a hang. Press `Ctrl+C` to stop it.

### 5. Commit and push

```bash
cd ~/"AI Files"/contract_agent_capstone
git add backend/mcp_layer/
git commit -m "Add MCP layer: four knowledge-retrieval tools over the existing Neo4j surface"
git push origin brittany_branch
```

### 6. Open the pull request

Go to `https://github.com/gunnbrittany/contract_agent_capstone`, click **Compare & pull
request**, title it `Add MCP + Knowledge Layer (Brittany)`, and paste the README's design
rationale into the description.

### 7. Email the instructor

You have been carrying this since April. Send it before the PR is even reviewed:

> I am completing the Knowledge and MCP layer for the contract review agent. Rather than
> building a separate vector store, I implemented four MCP tools over the platform's existing
> Neo4j retrieval surface, since the architectural gap was reachability rather than storage.
> PR is open and I can present whenever it suits you.

---

## The presentation, in four beats

1. **The gap.** The platform had a mature knowledge layer and no way for an external agent to
   reach it. Storage was never the problem.
2. **The decision.** Four narrow single-responsibility tools instead of one `search`, so a
   failure is diagnosable from the trace alone.
3. **The second decision.** Metadata filtering before similarity. Legal answers are
   jurisdiction-dependent, and pure embedding search will hand you a California clause for a
   New York contract.
4. **What I would do next.** Per-tool evaluation: precision and recall against a labeled clause
   set for the two search tools, exact-match for the playbook lookup, since a playbook lookup
   is either right or it is a bug.

---

## What this does NOT let you say

- Not "I built a ChromaDB vector store." You did not, and you should not.
- Not "550 lines of production code" as prior work. The count that matters is what lands in
  the PR.
- Not completed-and-presented until the PR is merged and you have actually presented it.

Once the PR is open, Story 2 in the Signature Story Bank becomes true in past tense, and the
honest account of an 18-day overrun that ended in a plan and a hard conversation becomes the
strongest "tell me about a missed deadline" answer you have.

---

## Added 2026-10-18: what was verified today, and three findings this plan did not have

**Verified by running it (repo: `~/AI Files/contract_agent_capstone`, branch `brittany_branch`, everything still uncommitted):**
- **Tests:** all 19 pass (`tests/test_mcp_knowledge.py` and `backend/tests/test_mcp_layer.py`, run with the repo's own `.venv`).
- **Server:** the local dev server starts without Neo4j (it falls back to the embedded store). Five endpoints answered 200: `/api/mcp/info`, `/api/mcp/tools`, `/api/mcp/tools/search_clause_library`, `/api/mcp/tools/get_playbook_rule`, `/api/mcp/validate-clause`.

**Three findings to fix before the demo:**
1. **The clause search ignores its result limit.** `backend/api/mcp_router.py` (about line 137) calls `search_clause_library(req.query, req.clause_type)` without the limit, and the tool in `backend/mcp_layer/tools.py` (about line 116) hardcodes `n_results=3`. Asking for 2 results returned 3. Fix: give the tool an optional `limit` and pass it through.
2. **The dev server listens on every network connection.** `backend/dev_server.py` ends with `uvicorn.run(app, host="0.0.0.0", port=8000)`. For a local demo use `127.0.0.1`.
3. **The playbook lookup returned nothing** for rule "survival" under clause type "Confidentiality". Check the names in `backend/knowledge/seed_knowledge.py` against what the demo uses (the validator call with clause type "Survival" worked), and pick a demo example that returns a rule.

**Still to do:** view the React demo page; commit, push, and open the pull request (steps 5 and 6 above); email the instructor (step 7); record a short walkthrough for the presentation. Her ruling 2026-10-18: the explanation of her contribution lives as the slide deck (`Big Tech Career Strategy/Capstone_Deck/`), not as a tab on the website.
