#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CURRENT_DIR = os.path.dirname(__file__)
VENDOR_DIR = os.path.join(CURRENT_DIR, "vendor")
if os.path.isdir(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

RUNTIME_ROLE = os.getenv("RUNTIME_ROLE", "reader")
MODEL_ID = os.getenv("READER_MODEL_ID", "eu.anthropic.claude-haiku-4-5-20251001-v1:0")
SHARED_MEMORY_ID = os.getenv("SHARED_MEMORY_ID", "")


def maybe_run_tools(question: str) -> dict:
    tools = {}
    lower_q = question.lower()
    if "hora" in lower_q or "time" in lower_q or "timestamp" in lower_q:
        tools["current_utc_time"] = datetime.now(timezone.utc).isoformat()
    return tools


def retrieve_memory(question: str, actor_id: str, session_id: str, top_k: int) -> tuple[list[str], dict]:
    if not SHARED_MEMORY_ID:
        return [], {"error": "missing_shared_memory_id"}
    namespace = f"/org/{actor_id}/workflow/{session_id}/"
    try:
        import boto3

        agentcore = boto3.client("bedrock-agentcore")
        resp = agentcore.retrieve_memory_records(
            memoryId=SHARED_MEMORY_ID,
            namespace=namespace,
            searchCriteria={"searchQuery": question, "topK": top_k},
        )
        records = resp.get("memoryRecordSummaries", [])
        texts = []
        for record in records:
            text = record.get("content", {}).get("text")
            if isinstance(text, str) and text.strip():
                texts.append(text)
        meta = {"namespace": namespace, "retrieved_count": len(records)}
        return texts, meta
    except Exception as exc:
        return [], {"error": str(exc), "namespace": namespace}


def run_model(question: str, memory_records: list[str]) -> str:
    context = "\n".join(memory_records).strip()
    model_prompt = (
        "Answer ONLY using the provided memory.\n"
        "If information is missing, explicitly return 'insufficient_memory'.\n"
        "Output language must be English only.\n\n"
        f"Question:\n{question}\n\n"
        f"Memory:\n{context}"
    )
    try:
        import boto3  # lazy load to avoid startup crash when dependency is unavailable

        bedrock_runtime = boto3.client("bedrock-runtime")
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": model_prompt}]}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.0},
        )
        output = response.get("output", {}).get("message", {}).get("content", [])
        texts = [item.get("text", "") for item in output if isinstance(item, dict)]
        result = "\n".join([t for t in texts if t]).strip()
        return result if result else "model_empty_response"
    except Exception as exc:
        return f"model_unavailable: {exc}"


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/ping":
            self._send_json(200, {"status": "ok", "role": RUNTIME_ROLE})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/invocations":
            self._send_json(404, {"error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_payload = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(raw_payload.decode("utf-8"))
        except Exception:
            payload = {}

        question = str(payload.get("prompt", ""))
        actor_id = str(payload.get("actor_id", "operator-001"))
        session_id = str(payload.get("session_id", ""))
        top_k = int(payload.get("top_k", 5))

        memory_records, memory_meta = retrieve_memory(question, actor_id, session_id, top_k)
        tool_outputs = maybe_run_tools(question)

        augmented_question = question
        if tool_outputs:
            augmented_question = f"{question}\n\nTool outputs:\n{json.dumps(tool_outputs, ensure_ascii=False)}"

        reader_answer = run_model(augmented_question, memory_records)

        response = {
            "role": RUNTIME_ROLE,
            "message": "Reader runtime active.",
            "received_prompt": question,
            "memory_records_count": len(memory_records),
            "model_id": MODEL_ID,
            "reader_answer": reader_answer,
            "memory_id": SHARED_MEMORY_ID,
            "actor_id": actor_id,
            "session_id": session_id,
            "memory_meta": memory_meta,
            "tool_outputs": tool_outputs,
            "memory_preview": memory_records[:3],
        }
        self._send_json(200, response)


def main():
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
