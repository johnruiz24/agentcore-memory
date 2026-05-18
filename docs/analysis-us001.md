# US-001 Analysis: Reference Article Structure + Agentic Memory Codebase

## Reference Article Structure (AgentCore Identity)

### Narrative Flow
1. **Hero Introduction** (Marcus character)
   - 3:14 AM CloudWatch logs, OAuth failing 8th time
   - Demo success → Production ask → Impossible reality
   - Core problem: coordinating delegated OAuth across providers

2. **Four Problem Sections**
   - Problem 1: OAuth Multi-Provider Nightmare
   - Problem 2: Token Binding and Multi-Tenancy
   - Problem 3: Zero-Trust Token Isolation
   - Problem 4: Cross-Provider Orchestration
   
   Each follows pattern:
   - Problem statement with story
   - Broken traditional approach shown
   - Diagram (broken state)
   - Solution explained
   - Architecture diagram (clean state)
   - Code snippet

3. **Architecture Deep Dive**
   - Four-layer architecture in one picture
   - Each layer explained (Runtime, Gateway, Identity, Supervisor)
   - Responsibilities + guarantees

4. **Costs/Tradeoffs Section**
   - Real numbers: latency (210ms Gateway, 55ms Identity cached)
   - Operational complexity (4 services)
   - Token refresh races
   - Consent denial rates (4-7%)
   - Honest about when NOT to use

5. **Five Things We Got Wrong**
   - Numbered mistakes with fixes
   - Production-learned, specific
   - Optional infographic (mistakes → fixes)

6. **Production Proof**
   - Real trace with actual request IDs
   - Variance acknowledged
   - Behind-the-scenes flow explained

7. **Conclusion**
   - Marcus ships
   - Security team approves
   - Architecture scales to new providers
   - Call to action

### Tone/Style
- Story-driven but technically deep
- Honest about problems (not marketing)
- Production evidence > theory
- "You can't debug it" repetition for emphasis
- Code snippets are real, not pseudocode
- Numbers are specific (210ms, 4-7%, 36 scenarios)

### Image Pattern (16 total)
1. Hero image (4-layer architecture overview)
2. Problem diagrams (broken traditional approaches)
3. Architecture diagrams (3-layer, 4-layer, flows)
4. Flow diagrams (OAuth consent, token isolation, JWT validation)
5. Tradeoffs infographic
6. Mistakes/fixes infographic
7. Production trace diagram

**Placement:** Hero at top, 1 diagram per problem section, architecture in deep dive, tradeoffs before lessons, production proof near end

**Style:** White/light backgrounds, enterprise professional, clean typography, high contrast

## Agentic Memory Implementation Analysis

### Core Components

**1. Writer Runtime** (`runtime-src/writer/app.py`)
- Receives: `prompt` or `messages`, `actor_id`, `session_id`
- Process: Calls Bedrock model to extract canonical facts
- Persist: `CreateEvent(memoryId, actorId, sessionId, payload)`
- Returns: `memory_write_ok`, `memory_write_status`, `writer_summary`, `memory_id`

**2. Reader Runtime** (`runtime-src/reader/app.py`)
- Receives: `prompt`, `actor_id`, `session_id`, `top_k`
- Retrieve: `RetrieveMemoryRecords(memoryId, namespace, searchQuery, topK)`
- Enrich: Optional tool outputs (e.g., current_utc_time)
- Generate: Calls Bedrock model with retrieved context
- Returns: `reader_answer`, `memory_records_count`, `memory_meta`, `memory_preview`

**3. Namespace Pattern**
```
/org/{actorId}/workflow/{sessionId}/
```
- Same actor+session → shared context
- Different actor/session → isolated

**4. Memory Lifecycle**
1. Writer calls `CreateEvent` → source event stored
2. AgentCore async pipeline (~90s) derives records:
   - Summary-oriented records (broad questions)
   - Semantic fact-level records (specific questions)
3. Derived records indexed in namespace
4. Reader queries with `RetrieveMemoryRecords(searchQuery, topK)`
5. Returns ranked results (mixed summary + semantic)

**5. CDK Stack** (`lib/agentcore-shared-memory-poc-stack.ts`)
- 1 shared `AWS::BedrockAgentCore::Memory`
- 2 runtimes: `poc_memory_writer_runtime`, `poc_memory_reader_runtime`
- 2 endpoints (1 per runtime)
- Model: `eu.anthropic.claude-haiku-4-5-20251001-v1:0`
- Language: `PYTHON_3_12`

### Key APIs
- Writer: `bedrock-runtime:Converse`, `bedrock-agentcore:CreateEvent`
- Reader: `bedrock-agentcore:RetrieveMemoryRecords`, `bedrock-runtime:Converse`

### Evidence Files
- E2E flows: `evidence/e2e/e2e-flow-*.log/json`
- Strategy validation: `evidence/e2e/e2e-flow-4-strategy-validation-complex.json`
  - 2/2 broad questions retrieved summary records
  - 3/3 specific questions retrieved semantic records
- Live AWS proof: `evidence/e2e/e2e-flow-5-live-aws-proof.json`

## Article Structure Plan (Agentic Memory)

### Hero Section
- Character: Developer frustrated with context repetition
- Problem: Agent forgets everything between sessions
- User repeats context every time → poor UX + wasted tokens
- Solution teaser: 2 runtimes sharing 1 long-term memory

### Problem Sections (3 main)

**Problem 1: Context Repetition Nightmare**
- Stateless invocations, no persistence
- User repeats background every session
- Traditional: ephemeral agent memory
- Solution: AgentCore Memory with writer/reader pattern
- Code: CreateEvent API

**Problem 2: Cross-Runtime Memory Isolation**
- Specialized runtimes (writer vs reader) can't share
- Multi-agent systems need coordination
- Traditional: isolated runtime state
- Solution: Shared memory with namespace pattern
- Code: RetrieveMemoryRecords with `/org/{actorId}/workflow/{sessionId}/`

**Problem 3: Memory Strategy Confusion**
- Summary vs semantic retrieval
- Broad questions need summary, specific need semantic
- Traditional: single retrieval mode
- Solution: Strategy-aware retrieval with topK tuning
- Code: Strategy classification logic

### Architecture Section
- 3 components: Writer Runtime, Shared Memory, Reader Runtime
- Memory lifecycle: CreateEvent → async extraction → RetrieveMemoryRecords
- CDK stack showing infrastructure
- Sequence diagram: writer → memory → reader (with timing)

### Costs/Tradeoffs
- Async extraction delay (~90s)
- Storage costs per event
- RetrieveMemoryRecords latency (~150ms)
- When NOT to use: single-runtime, ephemeral context, real-time needs
- When to use: multi-session workflows, specialized runtime coordination

### Five Mistakes
1. Assumed sync extraction → needed 90s wait
2. Single namespace for all → needed actor+session keying
3. No topK tuning → tested topK=6 optimal
4. No strategy validation → built test harness
5. Missing wait logic → added retry with backoff

### Production Proof
- Real trace from evidence/e2e/ files
- Actual request IDs, latency numbers
- Writer output: memory_write_ok: true
- Reader output: memory_records_count: 4, answer grounded in context

## Image Generation Plan (10-12 images)

1. **Hero**: 2 runtimes + shared memory architecture (1792x1024)
2. **Problem 1**: Isolated sessions (broken) vs shared memory
3. **Problem 2**: Namespace pattern visualization
4. **Problem 3**: Strategy behavior flowchart (broad→summary, specific→semantic)
5. **Architecture**: 3-layer with CDK resources (Writer, Memory, Reader)
6. **Sequence**: Full flow writer→memory→reader with timing annotations
7. **Lifecycle**: CreateEvent → async extraction → derived records → retrieval
8. **Production**: Real trace with request IDs and latencies
9. **Tradeoffs**: Infographic showing delays, costs, when to use
10. **Mistakes/Fixes**: Optional red X → green check pattern
11-12. **Additional**: Memory namespace tree, strategy validation results

**Style**: White backgrounds, enterprise professional, minimal modern design, high contrast, clean typography

## Acceptance Criteria Verification (US-001)

✅ Reference article structure documented: hero, 4 problems, architecture, costs, lessons, production proof
✅ Agentic-memory components mapped: writer/reader runtimes, CDK stack, memory APIs
✅ Tone/style captured: story-driven, technically deep, honest, production-real
✅ Image placement identified: hero, problem diagrams, architecture, flows, tradeoffs, production

**US-001 COMPLETE**
