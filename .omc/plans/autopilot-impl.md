# Autopilot: Reorganize agentcore-memory Repository

## Scope
**Worktree**: /Users/john.ruiz/.claude/worktrees/cost-optimization-bedrock-agents/clean-agentcore-memory  
**No other branches. No work outside this worktree.**

---

## Task Group 1: README Restructure (Haiku Executor)

**Task 1.1**: Read current README.md and agentcore-identity example
**Task 1.2**: Rewrite README.md with structure:
- Problem & Solution (top)
- ✨ Core Features (3-5 bullets)
- Quick Start (prerequisites, install, first use)
- System Architecture (with diagram reference)
- Documentation table
- Memory Lifecycle diagram
- Configuration reference
- Usage Examples (3-5 concrete examples)
- Testing
- Deployment
- Security
- Troubleshooting
- Contributing
- License
- Next Steps

---

## Task Group 2: Hero Banner Image Generation (Sonnet Executor)

**Task 2.1**: Generate 1200x600px hero banner with text "Agent Core Runtime with Persistent Memory"
**Task 2.2**: Create docs/images/ directory
**Task 2.3**: Save banner as docs/images/hero-banner.png
**Task 2.4**: Update README.md to include hero banner reference at top

---

## Task Group 3: File Organization (Haiku Executor)

**Task 3.1**: Create .config/ directory
**Task 3.2**: Move .eslintrc.js, jest.config.js, cdk.json → .config/
**Task 3.3**: Move CODE_OF_CONDUCT.md, CONTRIBUTING.md, SETUP.md, EXAMPLES.md, reference.md → docs/
**Task 3.4**: Delete cdk.out, dist, build artifacts
**Task 3.5**: Verify package.json references updated (if needed)

---

## Task Group 4: Final Verification (Haiku Executor)

**Task 4.1**: List root directory — should only contain:
  - README.md
  - package.json
  - LICENSE
  - .github/
  - src/
  - tests/
  - docs/
  - .config/
  - .omc/
  - .git/

**Task 4.2**: Verify no scattered files remain

---

## Task Group 5: Git Commit (Haiku Executor)

**Task 5.1**: Stage all changes
**Task 5.2**: Single commit: "chore: reorganize repository structure and add hero banner"
**Task 5.3**: Verify commit was created

---

## Execution Order
1. Task Groups 2 + 3 (parallel) — Hero banner generation + File reorganization
2. Task Group 1 — README restructure (uses hero banner path)
3. Task Group 4 — Verify final state
4. Task Group 5 — Commit

---

## Critical Constraints
- ✅ ONLY work in: /Users/john.ruiz/.claude/worktrees/cost-optimization-bedrock-agents/clean-agentcore-memory
- ✅ NO other branches
- ✅ NO work outside this worktree
- ✅ Single commit only
