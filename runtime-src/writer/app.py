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

RUNTIME_ROLE = os.getenv("RUNTIME_ROLE", "writer")
MODEL_ID = os.getenv("WRITER_MODEL_ID", "eu.anthropic.claude-haiku-4-5-20251001-v1:0")
SHARED_MEMORY_ID = os.getenv("SHARED_MEMORY_ID", "")


def run_model(user_prompt: str) -> str:
    try:
        import boto3  # lazy load to avoid startup crash when dependency is unavailable

        bedrock_runtime = boto3.client("bedrock-runtime")
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.1},
        )
        output = response.get("output", {}).get("message", {}).get("content", [])
        texts = [item.get("text", "") for item in output if isinstance(item, dict)]
        result = "\n".join([t for t in texts if t]).strip()
        return result if result else "model_empty_response"
    except Exception as exc:
        return f"model_unavailable: {exc}"


def save_event_to_memory(actor_id: str, session_id: str, text: str) -> tuple[bool, str]:
    if not SHARED_MEMORY_ID:
        return False, "missing_shared_memory_id"
    if not actor_id or not session_id:
        return False, "missing_actor_or_session"
    try:
        import boto3

        agentcore = boto3.client("bedrock-agentcore")
        agentcore.create_event(
            memoryId=SHARED_MEMORY_ID,
            actorId=actor_id,
            sessionId=session_id,
            eventTimestamp=datetime.now(timezone.utc),
            payload=[
                {
                    "conversational": {
                        "role": "USER",
                        "content": {"text": text},
                    }
                }
            ],
        )
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


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

        messages = payload.get("messages", [])
        if isinstance(messages, list) and messages:
            prompt = "\n".join(str(x) for x in messages)
        else:
            prompt = str(payload.get("prompt", ""))
        actor_id = str(payload.get("actor_id", "operator-001"))
        session_id = str(payload.get("session_id", ""))

        model_prompt = (
            "Extract canonical facts and objectives from the context below in concise bullet form.\n"
            "Output language must be English only.\n"
            f"Context:\n{prompt}"
        )
        model_answer = run_model(model_prompt)
        memory_ok, memory_status = save_event_to_memory(actor_id, session_id, model_answer)

        response = {
            "role": RUNTIME_ROLE,
            "message": "Writer runtime active.",
            "received_prompt": prompt,
            "model_id": MODEL_ID,
            "writer_summary": model_answer,
            "memory_write_ok": memory_ok,
            "memory_write_status": memory_status,
            "memory_id": SHARED_MEMORY_ID,
            "actor_id": actor_id,
            "session_id": session_id,
        }
        self._send_json(200, response)


def main():
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
