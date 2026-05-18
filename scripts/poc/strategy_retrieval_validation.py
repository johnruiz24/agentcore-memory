#!/usr/bin/env python3
"""Validate summary vs semantic retrieval behavior with complex prompts.

This script:
1) Sends complex context to writer runtime
2) Waits for long-term extraction
3) Executes broad/specific reader questions
4) Audits retrieved strategy mix (summary vs semantic)
5) Produces a strict pass/fail report
"""

from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any

import boto3


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Strategy retrieval validation for AgentCore memory")
    p.add_argument("--region", required=True)
    p.add_argument("--memory-id", required=True)
    p.add_argument("--writer-runtime-arn", required=True)
    p.add_argument("--reader-runtime-arn", required=True)
    p.add_argument("--actor-id", default="operator-strategy-en-001")
    p.add_argument("--session-id")
    p.add_argument("--wait-seconds", type=int, default=90)
    p.add_argument("--top-k", type=int, default=6)
    p.add_argument("--writer-messages-file", required=True)
    p.add_argument("--questions-file", required=True)
    p.add_argument("--output-file", required=True)
    return p.parse_args()


def ensure_session_id(raw: str | None) -> str:
    sid = raw or f"strategy-session-{uuid.uuid4().hex}"
    if len(sid) < 33:
        sid = f"{sid}-{uuid.uuid4().hex}"
    return sid


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if not t:
            continue
        rows.append(json.loads(t))
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def invoke_runtime(client: Any, runtime_arn: str, payload_obj: dict[str, Any], session_id: str) -> dict[str, Any]:
    raw = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(payload_obj).encode("utf-8"),
    )
    stream = raw.get("response")
    parsed = None
    if stream is not None:
        parsed = json.loads(stream.read().decode("utf-8"))
    out = dict(raw)
    out["parsedResponse"] = parsed
    out.pop("response", None)
    return out


def classify_strategy(strategy_id: str) -> str:
    sid = strategy_id.lower()
    if "summary" in sid:
        return "summary"
    if "semantic" in sid:
        return "semantic"
    return "other"


def main() -> int:
    args = parse_args()
    session_id = ensure_session_id(args.session_id)

    data_client = boto3.client("bedrock-agentcore", region_name=args.region)
    writer_messages = load_jsonl(args.writer_messages_file)
    questions = load_jsonl(args.questions_file)

    report: dict[str, Any] = {
        "region": args.region,
        "memoryId": args.memory_id,
        "actorId": args.actor_id,
        "sessionId": session_id,
        "writerCount": len(writer_messages),
        "questionCount": len(questions),
        "writerResults": [],
        "questionResults": [],
        "validation": {
            "allWriterWritesOk": True,
            "broadQuestionsWithSummary": 0,
            "specificQuestionsWithSemantic": 0,
            "readerAnswersNonEmpty": 0,
        },
    }

    for i, msg_obj in enumerate(writer_messages, start=1):
        text = str(msg_obj.get("text") or msg_obj.get("prompt") or msg_obj)
        r = invoke_runtime(
            data_client,
            args.writer_runtime_arn,
            {
                "prompt": text,
                "messages": [text],
                "actor_id": args.actor_id,
                "session_id": session_id,
            },
            session_id,
        )
        pr = r.get("parsedResponse") or {}
        write_ok = bool(pr.get("memory_write_ok"))
        if not write_ok:
            report["validation"]["allWriterWritesOk"] = False
        report["writerResults"].append(
            {
                "index": i,
                "textPreview": text[:180],
                "modelId": pr.get("model_id"),
                "memoryWriteOk": write_ok,
                "memoryWriteStatus": pr.get("memory_write_status"),
            }
        )

    time.sleep(args.wait_seconds)

    namespace = f"/org/{args.actor_id}/workflow/{session_id}/"

    for q in questions:
        question = str(q["question"])
        q_type = str(q["type"]).lower()

        retrieve = data_client.retrieve_memory_records(
            memoryId=args.memory_id,
            namespace=namespace,
            searchCriteria={"searchQuery": question, "topK": args.top_k},
        )
        records = retrieve.get("memoryRecordSummaries", [])
        by_strategy = {"summary": 0, "semantic": 0, "other": 0}
        for rec in records:
            cls = classify_strategy(str(rec.get("memoryStrategyId", "")))
            by_strategy[cls] += 1

        rr = invoke_runtime(
            data_client,
            args.reader_runtime_arn,
            {
                "prompt": question,
                "actor_id": args.actor_id,
                "session_id": session_id,
                "top_k": args.top_k,
            },
            session_id,
        )
        pr = rr.get("parsedResponse") or {}
        answer = str(pr.get("reader_answer") or "")

        if answer.strip():
            report["validation"]["readerAnswersNonEmpty"] += 1

        if q_type == "broad" and by_strategy["summary"] > 0:
            report["validation"]["broadQuestionsWithSummary"] += 1
        if q_type == "specific" and by_strategy["semantic"] > 0:
            report["validation"]["specificQuestionsWithSemantic"] += 1

        report["questionResults"].append(
            {
                "type": q_type,
                "question": question,
                "retrievedCount": len(records),
                "strategyMix": by_strategy,
                "readerModelId": pr.get("model_id"),
                "answerPreview": answer[:500],
            }
        )

    broad_total = sum(1 for x in questions if str(x.get("type", "")).lower() == "broad")
    specific_total = sum(1 for x in questions if str(x.get("type", "")).lower() == "specific")
    answers_total = len(questions)

    validation = report["validation"]
    report["validation"]["broadTotal"] = broad_total
    report["validation"]["specificTotal"] = specific_total
    report["validation"]["answersTotal"] = answers_total

    passed = (
        validation["allWriterWritesOk"]
        and validation["broadQuestionsWithSummary"] == broad_total
        and validation["specificQuestionsWithSemantic"] == specific_total
        and validation["readerAnswersNonEmpty"] == answers_total
    )
    report["validation"]["passed"] = passed

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report["validation"], indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
