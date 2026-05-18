#!/usr/bin/env python3
"""Mini demo helper for shared AgentCore Memory across two dedicated POC runtimes.

This script focuses on retrieval validation and runtime invocation orchestration.
It assumes memory setup/strategies already exist and are ACTIVE.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import boto3

PROTECTED_RUNTIME_NAMES = {"claude-code-runtime", "gitlab-runtime"}


def build_runtime_session_id(raw_session_id: str | None) -> str:
    candidate = raw_session_id or f"handoff-session-{uuid.uuid4().hex}"
    if len(candidate) < 33:
        candidate = f"{candidate}-{uuid.uuid4().hex}"
    return candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shared AgentCore Memory mini POC")
    parser.add_argument("--region", required=True)
    parser.add_argument("--memory-id", required=True)
    parser.add_argument("--runtime-a-arn", required=True)
    parser.add_argument("--runtime-b-arn", required=True)
    parser.add_argument("--runtime-a-name", default="poc-memory-writer-runtime")
    parser.add_argument("--runtime-b-name", default="poc-memory-reader-runtime")
    parser.add_argument("--actor-id", default="operator-001")
    parser.add_argument("--session-id")
    parser.add_argument("--wait-seconds", type=int, default=90)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--writer-messages-file", help="Path to .txt or .jsonl with writer context messages")
    parser.add_argument("--reader-questions-file", help="Path to .txt or .jsonl with reader retrieval questions")
    parser.add_argument(
        "--default-writer-message",
        default="Contexto default de teste. Substitua com --writer-messages-file.",
    )
    parser.add_argument(
        "--default-reader-question",
        default="Quais são os principais fatos desta sessão?",
    )
    parser.add_argument("--inter-message-sleep-ms", type=int, default=0)
    parser.add_argument("--max-writer-messages", type=int)
    parser.add_argument("--max-reader-questions", type=int)
    return parser.parse_args()


def invoke_runtime(client: Any, runtime_arn: str, payload_obj: dict[str, Any], session_id: str) -> dict[str, Any]:
    payload = json.dumps(payload_obj).encode("utf-8")
    raw = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=payload,
    )
    parsed_payload = None
    response_stream = raw.get("response")
    if response_stream is not None:
        try:
            body_bytes = response_stream.read()
            parsed_payload = json.loads(body_bytes.decode("utf-8"))
        except Exception as exc:
            parsed_payload = {"parse_error": str(exc)}
    out = dict(raw)
    out["parsedResponse"] = parsed_payload
    out.pop("response", None)
    return out


def retrieve_records(
    client: Any,
    memory_id: str,
    namespace: str,
    query: str,
    top_k: int,
) -> dict[str, Any]:
    return client.retrieve_memory_records(
        memoryId=memory_id,
        namespace=namespace,
        searchCriteria={
            "searchQuery": query,
            "topK": top_k,
        },
    )


def _parse_jsonl_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        doc = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped

    if isinstance(doc, str):
        return doc
    if isinstance(doc, dict):
        for k in ("text", "message", "prompt", "question", "content"):
            value = doc.get(k)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def load_messages(path: str | None, fallback: str) -> list[str]:
    if not path:
        return [fallback]

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    lines = p.read_text(encoding="utf-8").splitlines()
    msgs: list[str] = []
    for line in lines:
        parsed = _parse_jsonl_line(line)
        if parsed:
            msgs.append(parsed)
    if not msgs:
        raise ValueError(f"No valid messages parsed from {path}")
    return msgs


def main() -> int:
    args = parse_args()
    runtime_session_id = build_runtime_session_id(args.session_id)

    if args.runtime_a_name in PROTECTED_RUNTIME_NAMES or args.runtime_b_name in PROTECTED_RUNTIME_NAMES:
        print(
            "Refusing to run against protected stable runtime names. Use dedicated POC runtime names.",
            file=sys.stderr,
        )
        return 3

    data_client = boto3.client("bedrock-agentcore", region_name=args.region)

    namespace_prefix = f"/org/{args.actor_id}/workflow/{runtime_session_id}/"
    writer_messages = load_messages(args.writer_messages_file, args.default_writer_message)
    reader_questions = load_messages(args.reader_questions_file, args.default_reader_question)

    if args.max_writer_messages is not None:
        writer_messages = writer_messages[: max(args.max_writer_messages, 0)]
    if args.max_reader_questions is not None:
        reader_questions = reader_questions[: max(args.max_reader_questions, 0)]

    if not writer_messages:
        print("No writer messages to process.", file=sys.stderr)
        return 4
    if not reader_questions:
        print("No reader questions to process.", file=sys.stderr)
        return 5

    print(f"[1/4] Invoking writer runtime ({args.runtime_a_name}) with {len(writer_messages)} messages...")
    writer_invocations: list[dict[str, Any]] = []
    for idx, message in enumerate(writer_messages, start=1):
        writer_response = invoke_runtime(
            data_client,
            args.runtime_a_arn,
            {
                "prompt": message,
                "messages": [message],
                "actor_id": args.actor_id,
                "session_id": runtime_session_id,
            },
            runtime_session_id,
        )
        writer_invocations.append(
            {
                "messageIndex": idx,
                "messagePreview": message[:180],
                "runtimeResponse": writer_response,
            }
        )
        if args.inter_message_sleep_ms > 0 and idx < len(writer_messages):
            time.sleep(args.inter_message_sleep_ms / 1000.0)

    print(f"[2/4] Waiting {args.wait_seconds}s for async long-term extraction...")
    time.sleep(args.wait_seconds)

    print(f"[3/4] Invoking reader runtime ({args.runtime_b_name}) with {len(reader_questions)} questions...")
    question_results: list[dict[str, Any]] = []
    for question in reader_questions:
        retrieval: dict[str, Any] = {}
        records: list[dict[str, Any]] = []
        for _ in range(3):
            retrieval = retrieve_records(
                data_client,
                memory_id=args.memory_id,
                namespace=namespace_prefix,
                query=question,
                top_k=args.top_k,
            )
            records = retrieval.get("memoryRecordSummaries", [])
            if records:
                break
            time.sleep(10)

        memory_texts = []
        for record in records:
            text = record.get("content", {}).get("text")
            if isinstance(text, str) and text.strip():
                memory_texts.append(text)

        reader_response = invoke_runtime(
            data_client,
            args.runtime_b_arn,
            {
                "prompt": question,
                "actor_id": args.actor_id,
                "session_id": runtime_session_id,
                "top_k": args.top_k,
            },
            runtime_session_id,
        )
        question_results.append(
            {
                "question": question,
                "retrievedCount": len(records),
                "records": records,
                "readerRuntimeResponse": reader_response,
            }
        )

    report = {
        "region": args.region,
        "memoryId": args.memory_id,
        "runtimeAName": args.runtime_a_name,
        "runtimeBName": args.runtime_b_name,
        "actorId": args.actor_id,
        "sessionId": runtime_session_id,
        "namespacePrefix": namespace_prefix,
        "writerMessagesProcessed": len(writer_messages),
        "readerQuestionsProcessed": len(reader_questions),
        "writerInvocations": writer_invocations,
        "questionResults": question_results,
        "totalRetrievedRecords": sum(item["retrievedCount"] for item in question_results),
    }

    print(json.dumps(report, indent=2, default=str))

    if report["totalRetrievedRecords"] == 0:
        print(
            "No memory records retrieved for any reader question. Increase wait time or verify namespace/strategy.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
