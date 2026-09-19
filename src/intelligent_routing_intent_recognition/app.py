"""HTTP entrypoint: POST /router/call."""

from flask import Flask, request, jsonify

from .config import load_config
from .llm_client import LlmClient
from .router_service import RouterService

app = Flask(__name__)
app.json.ensure_ascii = False
_config = load_config()
_service = RouterService(LlmClient(_config))


@app.post("/router/call")
def router_call():
    body = request.get_json(force=True, silent=True) or {}
    question = body.get("question", "")
    return jsonify(_service.route(question))


def main():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
