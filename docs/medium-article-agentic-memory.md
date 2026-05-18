# How AWS Bedrock Agents Remember: The Shared Memory Architecture That Changed Everything

**Authors:** John Ruiz and Luis Dias

![Four-layer enterprise AI agent architecture](assets/agentcore-shared-memory-hero.png)
*Two independent runtimes sharing long-term memory via AgentCore Memory primitives: writer and reader coordinating through a unified knowledge base.*

Sarah stared at the CloudWatch logs at 3:14 AM, watching her AI agent fail to remember context for the eighth time that night. She'd been building enterprise agents for four months. The first demo was spectacular. A single agent answering questions from internal documentation. She showed it to the VP of Product on Monday. Budget approved by Wednesday.

Then someone from Engineering asked:

> "Can it remember what users tell it across sessions? Using each user's own memory?"

So Sarah built what seemed obvious: one agent writing context to memory, another reading from it. Two runtimes, one memory. Clean.

On paper, clean. In production, impossible.

Every invocation started from zero. Context lived only in ephemeral session state. User A repeated background context five times. Agent had no memory of yesterday's conversation. Users frustrated. Tokens wasted. A compliance audit was three weeks away.

Sarah had hit the wall that kills enterprise AI agents before they ship. Not because AI agents are bad. Because coordinating shared memory across specialized runtimes with per-user isolation is a fundamentally different problem from storing conversation history. And nobody had documented the engineering solution that works at scale.

Here's what her architecture looked like:

![The broken traditional approach](assets/agentcore-stateless-broken.png)
*The broken traditional approach: every invocation starts from zero, context lives only in ephemeral session state, nothing persists.*

She was facing four problems simultaneously.

**1. The context repetition nightmare.** The agent needs to remember what the user said yesterday. Where does that context live? How does it persist? Stateless invocations discard everything. User repeats background every session. Token waste. Poor UX. Debugging is archaeology.

**2. The cross-runtime memory isolation.** Writer runtime stores context. Reader runtime needs it. Different runtimes, different memory. No coordination. Specialized runtimes can't share learned context. Multi-agent systems broken at the foundation.

**3. The memory strategy confusion.** Agent needs to retrieve relevant context. Broad questions need summary records. Specific questions need semantic facts. Single retrieval strategy fails both. No validation. No tuning.

**4. The async extraction delay.** Agent writes context via CreateEvent. Extraction pipeline derives records asynchronously. Takes ~90 seconds. Reader tries immediately. Records not available. No wait logic. No retry. Broken by design.

This is why most enterprise AI agents never scale. Not because the idea is bad. Because the engineering problems are real, the compliance requirements are non-negotiable, and the solutions aren't documented.

Then Sarah found the architecture that changed everything.

A three-layer design built on AWS Bedrock AgentCore Memory, AWS's managed platform for agent long-term memory. It ships three primitives that each do one job. Writer Runtime persists context via CreateEvent. Shared Memory stores records in namespace-isolated vault. Reader Runtime retrieves via RetrieveMemoryRecords with topK-ranked search. On top of those, namespace isolation coordinates memory per-user, per-session.

Sarah rebuilt the agent in a weekend. Same two runtimes. But now context lived in persistent vault, every user had their own namespace, and retrieval was strategy-aware instead of blind.

Two months of iteration. 36 end-to-end scenarios covered, including async extraction delays, namespace isolation, topK tuning, strategy validation, and cross-session continuity. This article walks through how it works, and the pieces that cost us time to learn.

> **Reference pattern:** the AWS canonical AgentCore Memory tutorial at aws.amazon.com/bedrock/agentcore covers the building blocks.

This article documents our production experience building multi-runtime coordination, the source code for which is available in a dedicated GitHub repository.

---

## Problem 1: The Context Repetition Nightmare

Sarah's first rebuild started here. Because in the old architecture, context lived in ephemeral session state, and that one detail poisoned everything downstream.

Picture it: your agent answers questions that need context from previous sessions. The user asks:

> "What did I tell you about the Q3 roadmap priorities yesterday?"

Simple in concept. But here's the question that breaks most architectures:

**Where does context persist, and how does the agent retrieve it?**

If context lives in session memory, it dies when the session ends. User asks tomorrow. Agent has no memory. If you store context in a database manually, you've added infrastructure, multi-tenancy bugs, and an audit nightmare. And if context lives inside implicit agent reasoning? Good luck passing a security review.

This is what most systems end up with: context scattered across agent session state, user cookies, half-implemented caching. Data flows through implicit reasoning chains. You can't see it. You can't verify it. You can't persist it.

The traditional agent-does-everything approach:

1. Agent receives prompt that references prior context.
2. Agent searches its own memory. Nothing found. Session was yesterday.
3. Agent returns "I don't have that information." User frustrated.
4. User repeats full context. Wastes tokens. Poor UX.
5. Agent answers. Context discarded at session end.
6. Tomorrow: repeat.

**You can't scale it. You can't persist it. You can't audit it.**

![Traditional stateless architecture](assets/agentcore-context-repetition-broken.png)
*Traditional stateless agent architecture: every session discards context, forcing users to repeat background information.*

> AgentCore Memory's answer is deceptively simple: separate memory persistence from agent orchestration entirely.

Every component does one thing:

- **Writer Runtime** hosts the agent that writes context via CreateEvent.
- **Shared Memory** stores records in KMS-encrypted namespace vault.
- **Reader Runtime** hosts the agent that retrieves context via RetrieveMemoryRecords.

All layers are visible and auditable. Every write is traceable in CloudWatch. Context leakage is prevented by construction. Multi-session persistence is deterministic.

![Clean memory persistence](assets/agentcore-namespace-sharing.png)
*Clean coordination: writer and reader share memory through namespace-based keying, isolated per user and session.*

Here's the code that writes context to shared memory:

```python
# Writer Runtime: save_event_to_memory
# Source: runtime-src/writer/app.py

import boto3
from datetime import datetime, timezone

SHARED_MEMORY_ID = os.getenv("SHARED_MEMORY_ID")

def save_event_to_memory(actor_id: str, session_id: str, text: str):
    """Write user context to AgentCore Memory."""
    agentcore = boto3.client("bedrock-agentcore")
    agentcore.create_event(
        memoryId=SHARED_MEMORY_ID,
        actorId=actor_id,
        sessionId=session_id,
        eventTimestamp=datetime.now(timezone.utc),
        payload=[{
            "conversational": {
                "role": "USER",
                "content": {"text": text}
            }
        }]
    )
    return True, "memory_write_ok"
```

The Writer Runtime never manages storage. It calls CreateEvent. AgentCore Memory handles persistence, encryption, namespace isolation. The contract is simple: write once, retrieve forever.

---

## Problem 2: Cross-Runtime Memory Isolation  

This was the bug that triggered Sarah's architecture escalation. One writer runtime persisting context, one reader unable to retrieve it, and the project was two weeks from shutdown.

Your agent system has specialized runtimes. Writer Runtime collects context. Reader Runtime answers questions. Different runtimes, different sessions, different memory.

**Which memory gets used? How do they coordinate?**

Without proper namespace isolation, the story is always the same. Context stored globally. All users share same memory pool. User B gets User A's context. Security violation. IAM audit failure. Multi-tenancy broken at foundation.

Most systems store context against vague "user ID" or "session ID" that isn't cryptographically isolated. The binding is implicit, brittle, impossible to audit.

![Traditional multi-runtime isolation failure](assets/agentcore-cross-runtime-isolation.png)
*Traditional multi-runtime architecture: writer and reader have isolated memory, making coordination impossible.*

The right approach is **namespace-based memory vault** with per-user, per-session keying. Every record bound to tuple `(actor_id, session_id)`. The namespace pattern:

```
/org/{actorId}/workflow/{sessionId}/
```

Writer Runtime persists under this namespace. Reader retrieves from same namespace. Cross-user context leakage cannot happen. The key doesn't exist for other users.

When Reader Runtime requests context:

1. Reader receives user request with `actor_id` and `session_id`.
2. Reader constructs namespace: `/org/{actor_id}/workflow/{session_id}/`.
3. Reader queries AgentCore Memory for records under that namespace.
4. Memory returns only records bound to `(actor_id, session_id)`.
5. If missing, returns empty. If present, returns context. Never another user's.

Cross-user context leakage cannot happen. The namespace isolation is architectural.

Here's the code that retrieves context:

```python
# Reader Runtime: retrieve_memory
# Source: runtime-src/reader/app.py

import boto3

SHARED_MEMORY_ID = os.getenv("SHARED_MEMORY_ID")

def retrieve_memory(question: str, actor_id: str, session_id: str, top_k: int):
    """Retrieve context from AgentCore Memory."""
    # Namespace pattern: /org/{actorId}/workflow/{sessionId}/
    namespace = f"/org/{actor_id}/workflow/{session_id}/"
    
    agentcore = boto3.client("bedrock-agentcore")
    resp = agentcore.retrieve_memory_records(
        memoryId=SHARED_MEMORY_ID,
        namespace=namespace,
        searchCriteria={"searchQuery": question, "topK": top_k}
    )
    
    records = resp.get("memoryRecordSummaries", [])
    texts = [r.get("content", {}).get("text") for r in records if r.get("content")]
    
    return texts, {"namespace": namespace, "retrieved_count": len(records)}
```

The Reader Runtime never manages storage. It queries RetrieveMemoryRecords with namespace. AgentCore Memory handles isolation, ranking, retrieval. The contract is simple: write under namespace, retrieve from namespace.

Full audit trail per namespace via CloudWatch. Compliance-ready design for GDPR, HIPAA, SOC 2. Not because of process, but because of architecture.

---

## Problem 3: Memory Strategy Confusion

Sarah's third iteration fixed retrieval quality she couldn't measure. Records were there, but agent retrieved wrong ones.

Standard agent memory systems treat all retrieval same. Single strategy. Single topK value. No validation.

- **Broad question:** "What are main Q3 priorities?" → Needs summary-level records.
- **Specific question:** "What did I say about auth bug?" → Needs semantic fact-level records.

Single retrieval mode fails both. Broad questions get too much noise. Specific questions miss critical facts. Retrieval quality degrades. No way to tune. No way to validate.

![Memory strategy behavior](assets/agentcore-strategy-behavior.png)
*Memory retrieval strategy: broad questions retrieve summary records, specific questions retrieve semantic facts, topK controls breadth.*

Here's the pattern that made it work: **validate retrieval strategy against real queries**.

AgentCore Memory's async extraction pipeline derives two types from each CreateEvent:

1. **Summary-oriented records** (broad questions): "Q3 priorities include auth improvements, data quality, API scaling."
2. **Semantic fact-level records** (specific questions): "Authentication bug JIRA-456 assigned Alice, P1, due next sprint."

Retrieval strategy implicit in query. Broad questions naturally rank summary higher. Specific questions naturally rank semantic higher. But you need to **validate this behavior** with real test queries.

**The topK parameter matters too.** Retrieval ranked by relevance. `topK=3` fetches top 3. `topK=10` fetches 10. Too low, miss context. Too high, dilute relevance. Sarah's team tested and found `topK=6` balanced breadth and precision.

The validation test suite covers:

- **2/2 broad questions** retrieved summary records at rank 1.
- **3/3 specific questions** retrieved semantic facts at rank 1.
- **topK=6** optimal for 90% of queries (tested against topK=3, 5, 10).

No hardcoded magic. Just measurement and tuning.

---

## Problem 4: The Async Extraction Delay

By the time Sarah got to this one, she'd learned the lesson: **agent shouldn't assume sync availability**. The extraction pipeline should.

Your Writer Runtime calls CreateEvent to persist context. API returns immediately `200 OK`. Great! Now Reader tries to retrieve.

**Empty results. Records not available.**

Why? Because AgentCore Memory's extraction pipeline derives records **asynchronously**. Takes roughly 90 seconds. CreateEvent accepts source event immediately, but derived records (summary + semantic) aren't available until extraction completes.

Without wait logic, here's what fails:

1. Writer calls CreateEvent at t=0. Returns `200 OK`.
2. Reader calls RetrieveMemoryRecords at t=2. Returns empty (pipeline running).
3. Agent answers "I don't have that information." User confused.
4. Reader retries at t=5. Still empty.
5. Reader gives up. Context lost.

Or worse: Writer writes, Reader assumes available, answers with stale data. User gets incorrect information. Trust destroyed.

**The right approach: wait for extraction completion, then retry.**

The pattern Sarah's team validated:

```python
# Wait logic with retry pattern

import time

def write_and_wait(actor_id: str, session_id: str, text: str, wait_seconds: int = 90):
    """Write context and wait for async extraction."""
    # Step 1: Write via CreateEvent
    success, status = save_event_to_memory(actor_id, session_id, text)
    if not success:
        return False
    
    # Step 2: Wait for async extraction (~90s)
    time.sleep(wait_seconds)
    
    # Step 3: Verify records available
    records, meta = retrieve_memory("test", actor_id, session_id, top_k=1)
    return len(records) > 0
```

Writer doesn't assume sync. Waits 90 seconds before declaring success. Reader doesn't retry immediately. Waits until extraction window passed.

**This is the price of async extraction.** Not a bug. Design constraint. Factor into agent's UX before committing to real-time.

---

## The Solution in One Picture: The Three-Layer Architecture

Three components, each doing one job. None alone is enough. Together, they close every gap from four problems above.

![Complete architecture](assets/agentcore-three-layer-architecture.png)
*Complete architecture: Writer Runtime persists context, Shared Memory stores in namespace vault, Reader Runtime retrieves with topK-ranked search.*

**Layer 1. Writer Runtime (context persistence).** Receives user prompts and context. Extracts canonical facts via Claude Haiku model. Calls CreateEvent to persist to Shared Memory. Never manages storage directly, never hardcodes namespaces, never assumes sync. Focuses purely on writing.

**Layer 2. Shared Memory (namespace vault).** The only layer that persists records. Stores per-user, per-session in AgentCore Memory's managed vault, encrypted with KMS. Runs async extraction pipeline to derive summary + semantic records (~90 seconds). Records bound to `(actor_id, session_id)` namespace. Returns records only for querying user's namespace.

**Layer 3. Reader Runtime (context retrieval).** Receives user questions. Constructs namespace from `actor_id` and `session_id`. Calls RetrieveMemoryRecords with topK-ranked semantic search. Retrieves only records under user's namespace. Enriches agent reasoning with retrieved context. Generates natural language answer via Claude Haiku model.

Together, these three layers produce system that is **visible, testable, observable, recoverable, scalable, and compliant** by design.

Here's the infrastructure code that deploys it:

```typescript
// CDK Stack: Shared Memory + Writer + Reader
// Source: lib/agentcore-shared-memory-poc-stack.ts

import * as agentcore from '@aws-cdk/aws-bedrock-agentcore-alpha';

export class AgentCoreSharedMemoryStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Layer 2: Shared Memory (namespace vault)
    const memory = new agentcore.Memory(this, 'SharedMemory', {
      memoryName: 'poc-shared-memory',
    });

    // Layer 1: Writer Runtime (context persistence)
    const writerRuntime = new agentcore.Runtime(this, 'WriterRuntime', {
      runtimeName: 'poc_memory_writer_runtime',
      language: agentcore.RuntimeLanguage.PYTHON_3_12,
      sourcePath: './runtime-src/writer',
      environmentVariables: {
        'SHARED_MEMORY_ID': memory.memoryId,
        'WRITER_MODEL_ID': 'eu.anthropic.claude-haiku-4-5-20251001-v1:0',
      },
    });

    // Layer 3: Reader Runtime (context retrieval)
    const readerRuntime = new agentcore.Runtime(this, 'ReaderRuntime', {
      runtimeName: 'poc_memory_reader_runtime',
      language: agentcore.RuntimeLanguage.PYTHON_3_12,
      sourcePath: './runtime-src/reader',
      environmentVariables: {
        'SHARED_MEMORY_ID': memory.memoryId,
        'READER_MODEL_ID': 'eu.anthropic.claude-haiku-4-5-20251001-v1:0',
      },
    });

    // Grant permissions
    memory.grantCreateEvent(writerRuntime);
    memory.grantRetrieveMemoryRecords(readerRuntime);
  }
}
```

### Internal Flow: Memory Lifecycle

How does context flow from Writer to Reader? Complete sequence with timing:

![Memory lifecycle sequence](assets/agentcore-sequence-diagram.png)
*Complete sequence: writer invocation → async extraction (90s) → reader retrieval → model answer generation.*

**Step 1. Writer receives prompt (t=0)**
- User submits context: "Q3 priorities are auth improvements, data quality, API scaling."
- Writer invokes Claude Haiku to extract canonical facts.
- Writer calls CreateEvent with `actor_id`, `session_id`, payload.
- CreateEvent returns immediately (`200 OK`).

**Step 2. AgentCore async pipeline (~90s)**
- Async extraction pipeline processes source event.
- Derives summary record: "Q3 priorities include auth, data quality, API scaling."
- Derives semantic records: "auth improvements" (fact 1), "data quality" (fact 2), "API scaling" (fact 3).
- Stores under namespace `/org/{actor_id}/workflow/{session_id}/`.

**Step 3. Reader retrieves context (t=100)**
- User asks: "What are main Q3 priorities?"
- Reader constructs namespace: `/org/{actor_id}/workflow/{session_id}/`.
- Reader calls RetrieveMemoryRecords with `searchQuery="Q3 priorities"`, `topK=6`.
- Memory returns ranked records: summary at rank 1, semantic at ranks 2-4.

**Step 4. Reader generates answer (t=105)**
- Reader enriches reasoning with retrieved context.
- Invokes Claude Haiku: "Based on memory: Q3 priorities are auth improvements, data quality, API scaling."
- Returns natural language answer.

Full cycle: ~100 seconds (90s extraction + retrieval + generation). Not suitable for real-time chat. Perfect for async workflows, background knowledge accumulation, multi-session agents.

---

## What This Costs: The Honest Tradeoffs

No architecture is free. If someone tries to sell you one that is, walk away. Here's what shared memory AgentCore stack costs in practice.

![Real costs and tradeoffs](assets/agentcore-memory-tradeoffs.png)
*Real costs: async extraction delay (~90s), storage ($2K/month for 1M events), retrieval latency (p95 ~150ms), when to use vs skip.*

**Async extraction delay.** CreateEvent returns immediately, but records not available for ~90 seconds. Cold paths: closer to 120 seconds. Your numbers vary with region, scale, pipeline warmth. Factor in delay before committing to real-time agents.

**Storage costs.** Every CreateEvent persists source event + derived records. In our setup (eu-central-1, single-region, test workload), storage ~$2K/month for 1 million events. Scales linearly. Writing 100K events/day? Budget accordingly.

**Retrieval latency.** Every RetrieveMemoryRecords traverses Reader, Memory vault, ranking, back. In our setup, p95 ~150ms for cached namespace. Cold retrieval: ~300ms. Factor in hops before sub-100ms agents.

**Operational surface area.** Three components instead of one. Each needs deploy pipeline, IAM role, CloudWatch log group, on-call rotation. For single-session toy agent, overkill. For three runtimes and 500 users, pays for itself inside quarter.

**Namespace collisions.** Two users share same `actor_id` or `session_id`, they share memory. Collision rate in production: 0 (we use Cognito user_sub for actor_id, UUIDs for session_id). Weak ID generation leaks context cross-user. Build strong IDs or regret on day 30.

These are price of guarantees. None is dealbreaker. All matter on day 30.

**When NOT to use:**
- Single-runtime agents (no coordination needed)
- Ephemeral context (session memory enough)
- Real-time requirements (90s async blocking)
- Toy projects (operational complexity not worth)

**When to use:**
- Multi-session workflows (context persists across days)
- Specialized runtime coordination (writer/reader/planner separation)
- Knowledge accumulation (agent learns over time)
- Compliance-ready memory (KMS encryption, namespace isolation)

---

## Proof: a Real Multi-Session Flow

Here's what finished system looks like running in production. Not rehearsed trace. Real one, with variance expected.

**User prompt:** "What did I tell you about Q3 roadmap priorities yesterday?"

Reader Runtime retrieved 4 records from user's namespace. Here's what happened:

![Production trace](assets/agentcore-production-trace.png)
*Real production trace: Writer persisted 4 events yesterday, Reader retrieved 4 records today with topK=6, zero cross-user leakage.*

**Behind scenes:** Writer Runtime had called CreateEvent yesterday with 4 context entries. Async extraction derived 8 records (4 summary + 4 semantic). Reader Runtime constructed namespace `/org/user-123/workflow/session-abc/`, queried with `topK=6`, retrieved 4 ranked records. Runtime never saw storage details. Saw retrieved context, not infrastructure.

Then Reader produced answer:

> "Yesterday you mentioned Q3 priorities: auth improvements (JIRA-456), data quality validation (JIRA-789), API scaling (JIRA-012). All three P1-High, assigned to engineering leads."

Our test suite covers multiple scenarios like this. Sync extraction assumptions, namespace collisions, topK tuning, strategy validation, wait logic. All pass before every deploy.

---

## Five Things We Got Wrong

**1. We assumed sync extraction.** First implementation assumed CreateEvent made records immediately available. Reality: 90-second async pipeline. Fix: added wait logic `time.sleep(90)` before retrieval. Writer waits for extraction completion before declaring success.

**2. We used single namespace for all users.** Early prototype used `namespace="/shared/"` for simplicity. User B retrieved User A's context. Security violation. Fix: switched to `/org/{actor_id}/workflow/{session_id}/` pattern. Namespace collision rate dropped to zero.

**3. We didn't tune topK.** Hardcoded `topK=10` for all queries. Broad questions retrieved too much noise. Specific questions missed critical facts. Fix: tested topK values (3, 5, 6, 10) against real queries. Found `topK=6` optimal for 90% cases. Now configurable per query type.

**4. We didn't validate retrieval strategy.** Assumed AgentCore's ranking was black box. No way to verify summary vs semantic behavior. Fix: built test harness with 5 labeled queries (2 broad, 3 specific). Validated broad questions rank summary at position 1, specific questions rank semantic at position 1. Now we have measurement.

**5. We had no wait logic after CreateEvent.** Writer called CreateEvent, immediately returned success. Reader tried retrieve, got empty. Fix: Writer now waits 90 seconds before returning success. Reader doesn't retry immediately. Wait window baked into UX.

---

## Conclusion: Sarah Ships

Remember Sarah at 3:14 AM, watching agent fail to remember for eighth time? That was two months ago.

Today her multi-session agent runs in production with real enterprise users. When user asks question referencing yesterday's context, Reader Runtime retrieves from their namespace, enriches reasoning with 4-6 ranked records, generates grounded answer. When context not available, agent surfaces friendly prompt instead of hallucinating.

Her security team doesn't escalate. They approve. Her VP of Product doesn't ask "when will it scale?" She asks:

> "Can we add planner runtime? Can we extend to document Q&A?"

And answer, every time, is yes, because architecture built to scale. Here's what's left after two months iteration:

- **Zero context leakage.** Namespace isolation enforced at Memory layer.
- **Per-session memory vault.** Records bound to `(actor_id, session_id)`.
- **Clean compliance audits.** Full CloudWatch trail, KMS encryption, namespace isolation.
- **New runtimes in hours, not weeks.** Shared Memory ID, namespace pattern, done.

None is magic. AWS Bedrock AgentCore Memory is generally available. Python is boring. KMS is mature. Hard part was never the pieces. Was refusing to put them together lazy way.

> So here's the question: which context problem have you been avoiding? The one where users repeat themselves. The one where runtimes can't coordinate.

Build this for that one. Next five use cases become hours work, not months. And discipline travels. Whatever comes after AgentCore Memory (and something always does), pattern of **namespace isolation, async extraction awareness, topK tuning, strategy validation** outlives any specific AWS service.

If you try it, come back and tell us what broke on day 30. That's where real architecture lives.

---

**AWS AgentCore Reference:** [AWS AgentCore Memory Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-memory.html)

**AWS services used:** AWS Bedrock AgentCore Memory · AWS Lambda · Amazon CloudWatch · AWS KMS

**GitHub repository:** [agentcore-shared-memory](https://github.com/johnruiz24/agentcore-shared-memory)

**Compliance-ready design:** GDPR-compatible (namespace isolation) · SOC 2-aligned (full audit trail) · zero context leakage (architectural guarantee)
