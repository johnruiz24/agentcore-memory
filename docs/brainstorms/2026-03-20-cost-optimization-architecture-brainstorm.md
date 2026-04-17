# Brainstorm: AWS Cost Optimization with BedrockAgentCore + Claude Code Interpreter

**Date:** 2026-03-20
**Participants:** John Ruiz, Luis Dias, Claude (AI)
**Status:** Final

---

## What We're Building

A complete redesign of the existing AWS Cost Optimization multi-agent system (SO9593). Instead of the current supervisor + 2 Nova Micro sub-agents pattern, we're building a **monolithic intelligent system** where:

- **BedrockAgentCore** is the runtime container
- **Claude Code Interpreter** runs INSIDE BedrockAgentCore as the central AI engine
- The system operates in **3 layers**: Analysis, Decision, Implementation
- Claude Code Interpreter has access to **plugins and skills** (swarm mode, ralph loop, visual-explainer, etc.)
- All changes require **human approval** via Teams before execution
- Resources can be **edited but NEVER deleted** - full rollback mechanism
- **Memory persists** between cycles: resource state, learning from past decisions, and project context
- Runs on a **weekly schedule** via EventBridge
- Supports **multi-account** (AWS Organizations) from day one

### Core Concept: Claude Code Interpreter

The key innovation is that Claude Code is not a standalone tool - it runs as an **interpreter** inside BedrockAgentCore. This means:

1. It can access BedrockAgentCore's native capabilities (action groups, memory, guardrails)
2. It can use installed plugins/skills for iterative development (swarm, ralph)
3. It **dynamically generates boto3 code** to modify any AWS resource (no pre-defined Lambdas per service)
4. It maintains context through BedrockAgentCore's SESSION_SUMMARY + custom DynamoDB memory

---

## Why This Approach

### Chosen: Monolithic Intelligent (Option A)

**Over Pipeline Event-Driven (Option B):** Step Functions adds infrastructure complexity without proportional benefit for v1. The 3 layers don't need independent scaling yet.

**Over Hybrid Pragmatic (Option C):** Having Camada 1 as a separate Lambda breaks the "single intelligent system" concept. Claude Code Interpreter should orchestrate everything including data collection.

**Rationale:**
- Single deploy unit = faster iteration
- All 3 layers share the same Claude Code Interpreter context
- Swarm/Ralph modes work naturally within a single agent session
- Memory is centralized, not split across systems
- Easier to test end-to-end locally before deploying

---

## Architecture

### System Overview

```
BedrockAgentCore (Runtime)
  |
  +-- Claude Code Interpreter (Engine)
  |     |-- Swarm Mode (parallel strategy evaluation)
  |     |-- Ralph Loop (iterative refinement)
  |     |-- Dynamic Code Generation (boto3)
  |     +-- Skills & Plugins
  |
  +-- Action Groups (Lambdas):
  |     |-- CostExplorerAction     (GetCostAndUsage, GetCostForecast)
  |     |-- TrustedAdvisorAction   (ListRecommendations, ListResources)
  |     |-- CodeExecutorAction     (Executes Claude-generated boto3 code in sandbox)
  |     |-- SnapshotManagerAction  (Capture before/after state via AWS APIs)
  |     |-- AuditLoggerAction      (Record all actions + reasoning)
  |     +-- AccountDiscoveryAction (AWS Organizations: list accounts, assume roles)
  |
  +-- Memory Layer:
  |     |-- SESSION_SUMMARY (Bedrock native, conversation context, up to 365 days)
  |     +-- DynamoDB (custom: resource state, learning, project context)
  |
  +-- Output:
        +-- Teams Channel (approval cards + notifications + results)
```

### 3 Layers

**Layer 1 - Analysis & Reports:**
- Claude Code Interpreter invokes CostExplorerAction + TrustedAdvisorAction
- Iterates across all accounts via AccountDiscoveryAction
- Generates structured reports (JSON) with current costs, usage patterns, recommendations
- Stores reports in DynamoDB memory for historical comparison

**Layer 2 - Decision & Planning:**
- Claude Code Interpreter analyzes reports using swarm mode (3+ parallel strategies)
- Ralph loop refines the best strategy iteratively
- Produces an optimization plan per resource (generic - any AWS service)
- Plan includes: what to change, expected savings, risk assessment, rollback strategy
- **Claude Code Interpreter dynamically generates the boto3 code** that will be executed

**Layer 3 - Implementation (Human-in-the-Loop):**
- Plan + generated code is sent to Teams as adaptive card for approval
- On approval: SnapshotManager captures BEFORE state
- CodeExecutor runs the Claude-generated boto3 code in a sandboxed Lambda
- SnapshotManager captures AFTER state
- AuditLogger records everything (who, what, why, impact, code executed)
- If issue detected: Claude Code Interpreter generates rollback code from BEFORE snapshot

### Code Interpreter Flow (Layer 3 Detail)

```
1. Trusted Advisor says: "Lambda X has 3008MB but uses max 256MB"
2. Claude Code Interpreter generates:
   ```python
   import boto3
   client = boto3.client('lambda')
   client.update_function_configuration(
       FunctionName='my-func',
       MemorySize=512  # Conservative: 2x actual usage
   )
   ```
3. Code is validated (syntax, safety checks, no delete operations)
4. Sent to Teams: "Reduce Lambda X memory: 3008MB -> 512MB. Save ~$45/mo. Approve?"
5. Human approves in Teams
6. CodeExecutor Lambda runs the code
7. Snapshot AFTER captured, diff computed
8. Result sent to Teams: "Done. Lambda X now 512MB. Monitoring for 5 min..."
```

### Memory Architecture

**Discovery:** There are TWO distinct memory systems in AWS:

1. **Bedrock Agents Memory** (original) - Only `SESSION_SUMMARY` type
2. **Bedrock AgentCore Memory** (newer, standalone service) - 3 extraction strategies

We use **AgentCore Memory** (the newer service) as the primary memory layer, augmented with **DynamoDB** only for resource state snapshots and audit trail.

#### AgentCore Memory (Native - Primary)

| Strategy | Namespace | Purpose |
|---|---|---|
| `summaryMemoryStrategy` | `/summaries/{actorId}/{sessionId}` | Session summaries across weekly cycles |
| `userPreferenceMemoryStrategy` | `/preferences/{actorId}` | Team preferences, constraints, approval patterns |
| `semanticMemoryStrategy` | `/facts/{actorId}` | Learning: past decisions, outcomes, what worked/didn't |

**Configuration:**
```python
control_client = boto3.client('bedrock-agentcore-control')
memory = control_client.create_memory(
    name="CostOptimizationMemory",
    description="Memory for cost optimization agent cycles",
    eventExpiryDuration=365,
    memoryStrategies=[
        {'summaryMemoryStrategy': {'name': 'CycleSummarizer', 'namespaces': ['/summaries/{actorId}/{sessionId}']}},
        {'userPreferenceMemoryStrategy': {'name': 'TeamPreferences', 'namespaces': ['/preferences/{actorId}']}},
        {'semanticMemoryStrategy': {'name': 'OptimizationLearnings', 'namespaces': ['/facts/{actorId}']}}
    ]
)
```

**Integration with Strands Agent SDK:**
```python
from bedrock_agentcore.memory.client import MemoryClient
from bedrock_agentcore.memory.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.session import AgentCoreMemorySessionManager

config = AgentCoreMemoryConfig(memory_id=MEM_ID, session_id=SESSION_ID, actor_id="cost-optimizer")
session_manager = AgentCoreMemorySessionManager(agentcore_memory_config=config)
```

#### DynamoDB (Custom - Supplementary)

Only for data that AgentCore Memory doesn't handle natively:

| Data Type | Storage | Purpose | TTL |
|---|---|---|---|
| Resource State Snapshots | DynamoDB | Before/after config per resource per account | 90 days |
| Audit Trail | DynamoDB + S3 | Complete action log: code, approval, result | 365 days |

**DynamoDB Table Design (preliminary):**

- **PK:** `ACCOUNT#<account-id>` | **SK:** `RESOURCE#<resource-arn>#<timestamp>`
- **GSI1:** `TYPE#state|audit` | `TIMESTAMP#<iso-date>` (for querying by type)
- **TTL:** Configurable per type (state: 90 days, audit: 365 days)

### Safety Mechanisms

**Principle: Edit, Never Delete**

1. **Code Generation** - Claude Code Interpreter writes boto3 code
2. **Safety Validation** - Code is parsed: no `delete_*`, `terminate_*`, `destroy_*` calls allowed
3. **Snapshot BEFORE** - Capture current resource state via AWS APIs
4. **Human Approval** - Teams adaptive card with code preview + expected impact
5. **Sandboxed Execution** - CodeExecutor Lambda runs with scoped IAM (no delete permissions)
6. **Snapshot AFTER** - Capture new state, compute diff
7. **Monitor** - CloudWatch checks for degradation (configurable window: default 5 min)
8. **Rollback** - If issue: Claude Code Interpreter generates restore code from BEFORE state
9. **Audit** - Full trail: agent reasoning, generated code, human approval, execution result

**IAM Safety Layer:**
- CodeExecutor Lambda role has explicit `Deny` on all `Delete*`, `Terminate*`, `Destroy*` actions
- Cross-account access via `sts:AssumeRole` with the same deny policy
- Even if Claude Code Interpreter generates delete code, IAM blocks it

### Plugins & Skills (Claude Code Interpreter)

| Plugin | Purpose | When Used |
|---|---|---|
| Swarm Mode | Parallel evaluation of multiple optimization strategies | Layer 2 |
| Ralph Loop | Iterative refinement of chosen strategy + code | Layer 2 + Layer 3 |
| Visual Explainer | Generate HTML diagrams of changes and results | All layers |
| Code Generator | Dynamic boto3 code generation for any AWS service | Layer 3 |
| Snapshot Manager | Capture before/after state via describe_* APIs | Layer 3 |
| Audit Logger | Record all actions with reasoning and code | All layers |
| Teams Notifier | Adaptive cards for approval + result notifications | Layer 3 |
| Account Discovery | Iterate across AWS Organizations accounts | Layer 1 |

---

## Key Decisions

1. **Redesign from scratch** - Not extending the existing supervisor/sub-agent pattern
2. **Claude Code Interpreter inside BedrockAgentCore** - Not standalone Claude Code
3. **Dynamic code generation** - Claude Code Interpreter generates boto3 code on-the-fly instead of pre-built Lambda modifiers per service
4. **Generic resource support** - Any service Trusted Advisor recommends
5. **Human-in-the-loop always** - Every change requires human approval via Teams adaptive card
6. **Teams-first for v1** - Approval and notifications via Teams; dashboard for historical view only
7. **Dual memory** - SESSION_SUMMARY (native) + DynamoDB (custom state/learning/context)
8. **Monolithic architecture** - Single BedrockAgentCore, not distributed pipeline
9. **Edit never delete** - IAM enforced: Deny on all Delete/Terminate/Destroy actions
10. **Weekly schedule** - EventBridge triggers optimization cycle every week
11. **Multi-account from day one** - AWS Organizations support via cross-account role assumption

---

## Resolved Questions

1. **ResourceModifier genericity** -> Claude Code Interpreter generates boto3 code dynamically. No pre-defined Lambdas per service. A single CodeExecutor Lambda runs the generated code in a sandbox.

2. **Human approval UX** -> Teams adaptive cards for v1. Dashboard only for historical viewing.

3. **Scheduling** -> Weekly via EventBridge. Can be triggered on-demand too.

4. **Multi-account support** -> Yes, from day one. AWS Organizations with cross-account role assumption.

## Resolved Questions

1. **ResourceModifier genericity** -> Claude Code Interpreter generates boto3 code dynamically. No pre-defined Lambdas per service. A single CodeExecutor Lambda runs the generated code in a sandbox.

2. **Human approval UX** -> Teams adaptive cards via Power Automate for v1. Dashboard only for historical viewing.

3. **Scheduling** -> Weekly via EventBridge. Can be triggered on-demand too.

4. **Multi-account support** -> Yes, from day one. AWS Organizations with cross-account role assumption.

5. **Rollback scope for stateful services** -> Excluded from v1. Only stateless services (Lambda, EC2 compute, S3 policies, etc.) in v1. Stateful services (RDS, ElastiCache, DynamoDB) added in v2 with maintenance window support.

6. **Cost of the system itself** -> Minimum savings threshold per resource (e.g., >$50/month). Only propose changes where expected savings justify the cost of analysis + execution.

7. **Teams integration** -> Power Automate flow: SNS notification -> Power Automate -> Adaptive card with approve/reject buttons -> Response via SQS back to the agent.

## Open Questions (Deferred)

1. **Code sandbox security**: How to secure the CodeExecutor Lambda (IAM Deny, VPC isolation, code parsing, allowlist). Deferred to implementation phase.

---

## Next Steps

- Create implementation plan (`/ce:plan`)
- Architecture dashboard updated: `~/.agent/diagrams/aws-cost-optimization-architecture.html`
