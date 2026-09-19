"""Contract test for deterministic Approved Scenarios fixture generation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
APPROVED_DIR = PROJECT_ROOT / "tests" / "approved"


def test_generator_recreates_every_approved_fixture_byte_for_byte(tmp_path: Path) -> None:
    """Catch omitted scenarios or changed approved business facts."""
    # Arrange
    output_dir = tmp_path / "approved"
    expected = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(APPROVED_DIR.glob("*.approved.md"))
    }

    # Act
    result = subprocess.run(
        [sys.executable, "gen_fixtures.py", "--output-dir", str(output_dir)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    # Assert
    assert result.returncode == 0, result.stderr
    actual = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(output_dir.glob("*.approved.md"))
    }
    assert actual == expected
