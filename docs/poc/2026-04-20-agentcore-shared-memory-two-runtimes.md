# AgentCore Shared Memory POC: Technical Notes

## Objective
Demonstrate memory sharing between two different AgentCore runtimes using one shared long-term memory.

## Runtime Pair
- Writer: `poc_memory_writer_runtime`
- Reader: `poc_memory_reader_runtime`

## Model
- `eu.anthropic.claude-haiku-4-5-20251001-v1:0`

## APIs used
Writer:
- `bedrock-runtime:Converse`
- `bedrock-agentcore:CreateEvent`

Reader:
- `bedrock-agentcore:RetrieveMemoryRecords`
- `bedrock-runtime:Converse`

## Test payloads

Writer payload:
```json
{
  "prompt": "<writer message>",
  "messages": ["<writer message>"],
  "actor_id": "<actor_id>",
  "session_id": "<session_id>"
}
```

Reader payload:
```json
{
  "prompt": "<reader question>",
  "actor_id": "<actor_id>",
  "session_id": "<session_id>",
  "top_k": 6
}
```

## Shared namespace pattern
- `/org/{actorId}/workflow/{sessionId}/...`

## Memory lifecycle clarification

`CreateEvent` does not require pre-existing memory records.

It writes a new **source event**. Then AgentCore asynchronously derives strategy records from that source event:
- summary records (high-level synthesized context)
- semantic records (fact-level context)

Reader retrieval (`RetrieveMemoryRecords`) operates on these derived records, not on raw source events.

Practical consequence:
- Before first writer event: derived record set can be empty.
- After writer event: derived records appear after async processing delay.
- Retrieval results are relevance-ranked and can include both strategies in the same response.

## Validated outcomes
- Flow 1: immediate handoff writer -> memory -> reader works
- Flow 2: separate invocation writer, then later reader, works
- Reader answers from retrieved records and returns retrieval counts

## Evidence files
- `evidence/e2e/e2e-flow-1-writer-memory-reader-fixed.log`
- `evidence/e2e/e2e-flow-2-separate-invocations.log`
- `evidence/e2e/e2e-flow-3-complex-english.log`
- `evidence/e2e/e2e-flow-4-strategy-validation-complex.json`
- `evidence/e2e/e2e-flow-5-live-aws-proof.json`
- `evidence/e2e/e2e-flow-6-live-aws-proof-english-output.json`
- `evidence/gates/*.log`

## Strategy behavior validation (complex)

Additional strict validator:
- Script: `scripts/poc/strategy_retrieval_validation.py`
- Typed questions: `evidence/e2e/reader_questions_strategy_complex.jsonl`
- Result: `evidence/e2e/e2e-flow-4-strategy-validation-complex.json`

Pass criteria:
- All writer writes succeed
- Every broad question retrieves at least one summary record
- Every specific question retrieves at least one semantic record
- Every reader response is non-empty

Observed strict result:
- `passed = true`
- `broadQuestionsWithSummary = 2/2`
- `specificQuestionsWithSemantic = 3/3`
- `readerAnswersNonEmpty = 5/5`

## Endpoint display note

Seeing two endpoints in console for each runtime is expected:
- `DEFAULT` endpoint (service-managed)
- custom endpoint created by stack

This does not mean duplicate runtimes. The POC still uses exactly:
- 1 writer runtime
- 1 reader runtime
