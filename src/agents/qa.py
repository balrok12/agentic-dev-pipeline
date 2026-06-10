"""QA agent: validates generated code via syntax check and structural assertions."""

import ast
import re


_REQUIRED_KEYWORDS = [
    "FastAPI",
    "BaseModel",
]

_REQUIRED_PATTERNS = [
    r"@app\.(get|post|put|delete|patch)\(",
]


def run_qa(state: dict) -> dict:
    print("\n" + "=" * 60)
    print("[4/5] QA — Validating generated code")
    print("=" * 60)

    code = state.get("code", "")
    issues = []

    # 1. Syntax check
    try:
        ast.parse(code)
        print("  [PASS] Syntax check")
    except SyntaxError as exc:
        issues.append(f"SyntaxError: {exc}")
        print(f"  [FAIL] Syntax check — {exc}")

    # 2. Required imports / class usage
    for keyword in _REQUIRED_KEYWORDS:
        if keyword in code:
            print(f"  [PASS] Contains '{keyword}'")
        else:
            issues.append(f"Missing required element: '{keyword}'")
            print(f"  [FAIL] Missing '{keyword}'")

    # 3. At least one route decorator
    has_route = any(re.search(p, code) for p in _REQUIRED_PATTERNS)
    if has_route:
        print("  [PASS] At least one route decorator found")
    else:
        issues.append("No route decorators found (@app.get / @app.post / etc.)")
        print("  [FAIL] No route decorators found")

    # 4. Health check endpoint
    if "/health" in code:
        print("  [PASS] Health check endpoint present")
    else:
        issues.append("Missing /health endpoint")
        print("  [FAIL] Missing /health endpoint")

    qa_passed = len(issues) == 0
    feedback = "\n".join(issues) if issues else ""

    if qa_passed:
        print("\nResult: PASSED")
    else:
        print(f"\nResult: FAILED ({len(issues)} issue(s))")
        print("Feedback:")
        for issue in issues:
            print(f"  • {issue}")

    return {"qa_passed": qa_passed, "qa_feedback": feedback}
