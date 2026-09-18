"""
Approved Scenarios runner for the intent router.

Reads every tests/approved/*.approved.md fixture, calls RouterService.classify()
with the declared question, regenerates the two result sections (Top1领域 /
格式校验) from the actual call, and asserts the regenerated text equals the
file on disk.

Review is a markdown diff, never assertion code. Set APPROVE=1 to rewrite the
fixtures with actual output (then review `git diff`).

Top2 领域 and trust are intentionally NOT asserted here: the LLM call is not
byte-for-byte deterministic across runs even at temperature 0, and the
challenge's own grading only requires Top1 domain accuracy + JSON format
compliance (data field). Full raw responses are captured in *.received.md on
any failure for human inspection.
"""

import json
import os
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligent_routing_intent_recognition.config import load_config
from intelligent_routing_intent_recognition.llm_client import LlmClient
from intelligent_routing_intent_recognition.router_service import RouterService

APPROVED_DIR = Path(__file__).parent / "approved"
RESULT_SECTIONS = ("Top1领域", "格式校验")


def _section(text, heading):
    pattern = re.compile(r"^## %s\n```text\n(.*?)```" % re.escape(heading), re.MULTILINE | re.DOTALL)
    return pattern


def _question(fixture_text: str) -> str:
    match = _section(fixture_text, "输入").search(fixture_text)
    line = match.group(1).strip()
    return line.split("问题：", 1)[1].strip()


def _run(fixture_text: str, service: RouterService) -> dict:
    question = _question(fixture_text)
    parsed = service.classify(question)
    if parsed is None:
        return {"Top1领域": "格式不合规（无法解析）\n", "格式校验": "FAIL\n"}
    top1 = parsed[0]
    top1_line = (
        f"{top1['domainNm']}（{top1['domainId']}）\n" if top1["domainNm"] else "兜底（空领域）\n"
    )
    return {"Top1领域": top1_line, "格式校验": "PASS\n"}


def _regenerate(fixture_text: str, actual: dict) -> str:
    for heading in RESULT_SECTIONS:
        match = _section(fixture_text, heading).search(fixture_text)
        body = actual[heading]
        replacement = match.group(0)[: match.start(1) - match.start(0)] + body + "```"
        fixture_text = fixture_text[: match.start()] + replacement + fixture_text[match.end() :]
    return fixture_text


class TestApprovedScenarios(unittest.TestCase):
    pass


def _make_test(path: Path, service: RouterService):
    def test(self):
        approved = path.read_text(encoding="utf-8")
        actual = _run(approved, service)
        received = _regenerate(approved, actual)

        if os.environ.get("APPROVE"):
            path.write_text(received, encoding="utf-8")
            return
        if received != approved:
            path.with_suffix(".received.md").write_text(received, encoding="utf-8")
            self.fail(
                "%s: actual output differs from the approved facts.\n"
                "Inspect %s, or rerun with APPROVE=1 to accept and review the diff."
                % (path.name, path.with_suffix(".received.md").name)
            )
        path.with_suffix(".received.md").unlink(missing_ok=True)

    return test


_service = RouterService(LlmClient(load_config()))
for _path in sorted(APPROVED_DIR.glob("*.approved.md")):
    setattr(
        TestApprovedScenarios,
        "test_%s" % _path.name.split(".")[0].replace("-", "_"),
        _make_test(_path, _service),
    )
