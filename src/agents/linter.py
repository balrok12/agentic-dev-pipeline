"""Linter agent: runs ruff on generated code, auto-fixes what it can, flags the rest."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_linter(state: dict) -> dict:
    print("\n" + "=" * 60)
    print("[4/6] LINTER — Running ruff on generated code")
    print("=" * 60)

    code = state.get("code", "")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)

    try:
        # Auto-fix safe issues (import order, unused imports, etc.)
        subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--fix", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        # Read back auto-fixed code
        fixed_code = tmp_path.read_text(encoding="utf-8")

        # Check for remaining issues
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--output-format=json", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        issues = []
        if result.stdout.strip():
            try:
                raw = json.loads(result.stdout)
                issues = [
                    f"Line {item['location']['row']}: [{item['code']}] {item['message']}"
                    for item in raw
                ]
            except (json.JSONDecodeError, KeyError):
                if result.stdout.strip():
                    issues = [result.stdout.strip()]

        if issues:
            print(f"  [FAIL] {len(issues)} issue(s) remain after auto-fix:")
            for issue in issues:
                print(f"    • {issue}")
            lint_passed = False
            lint_feedback = "\n".join(issues)
        else:
            print("  [PASS] No lint issues")
            lint_passed = True
            lint_feedback = ""

        return {
            "code": fixed_code,
            "lint_passed": lint_passed,
            "lint_feedback": lint_feedback,
        }

    finally:
        tmp_path.unlink(missing_ok=True)
