"""Developer agent: generates FastAPI source code from the architect's design."""

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


def run_developer(state: dict) -> dict:
    retry = state.get("retry_count", 0)
    label = f"[3/5] DEVELOPER — Generating code (attempt {retry + 1})"
    print("\n" + "=" * 60)
    print(label)
    print("=" * 60)

    llm = ChatAnthropic(
        model=os.getenv("MODEL_NAME", "claude-3-5-haiku-20241022"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=4096,
    )

    feedback_section = ""
    if retry > 0 and state.get("qa_feedback"):
        feedback_section = f"""
Previous attempt failed QA. Feedback to address:
{state['qa_feedback']}

Fix the issues above before generating code.
"""
        print(f"QA feedback to address:\n{state['qa_feedback']}")

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

    # Strip markdown code fences if the model included them
    if code.startswith("```"):
        lines = code.splitlines()
        code = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    print(f"\nOutput — {len(code.splitlines())} lines of code generated")

    return {"code": code, "retry_count": retry + 1}
