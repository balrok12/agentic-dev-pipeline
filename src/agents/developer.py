"""Developer agent: generates FastAPI source code from the architect's design."""

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


def run_developer(state: dict) -> dict:
    lint_retry = state.get("lint_retry_count", 0)
    qa_retry = state.get("qa_retry_count", 0)
    attempt = lint_retry + qa_retry + 1
    print("\n" + "=" * 60)
    print(f"[3/6] DEVELOPER — Generating code (attempt {attempt})")
    print("=" * 60)

    llm = ChatAnthropic(
        model=os.getenv("MODEL_NAME", "claude-3-5-haiku-20241022"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=4096,
    )

    feedback_section = ""
    feedback = state.get("lint_feedback") or state.get("qa_feedback") or ""
    source = "Linter" if state.get("lint_feedback") else "QA" if state.get("qa_feedback") else ""
    if feedback:
        feedback_section = f"""
Previous attempt failed {source} checks. Issues to fix:
{feedback}
"""
        print(f"{source} feedback to address:\n{feedback}")

    messages = [
        SystemMessage(
            content=(
                "You are a senior Python developer. "
                "Generate complete, runnable FastAPI source code based on the provided design. "
                "Use only the Python standard library and FastAPI/Pydantic — no external databases."
            )
        ),
        HumanMessage(
            content=f"""Generate a complete FastAPI application based on this design:

{state['design']}
{feedback_section}
Requirements:
- Single Python file, complete and self-contained
- Use in-memory dict for storage (no database)
- Pydantic models for request/response validation
- Proper HTTP status codes and error handling (HTTPException)
- Include a health-check endpoint GET /health
- Return ONLY the Python code, no explanation, no markdown fences
"""
        ),
    ]

    response = llm.invoke(messages)
    code = response.content.strip()

    if code.startswith("```"):
        lines = code.splitlines()
        code = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    print(f"\nOutput — {len(code.splitlines())} lines of code generated")

    # 어느 쪽에서 재시도됐는지에 따라 해당 카운터만 증가
    updates: dict = {"code": code, "lint_feedback": "", "qa_feedback": ""}
    if state.get("lint_feedback"):
        updates["lint_retry_count"] = lint_retry + 1
    else:
        updates["qa_retry_count"] = qa_retry + 1
    return updates
