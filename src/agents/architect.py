"""Architect agent: produces a design document (data model + API interface) from task list."""

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


def run_architect(state: dict) -> dict:
    print("\n" + "=" * 60)
    print("[2/5] ARCHITECT — Designing system")
    print("=" * 60)

    tasks_text = "\n".join(f"  - {t}" for t in state["tasks"])
    print(f"Input tasks:\n{tasks_text}")

    llm = ChatAnthropic(
        model=os.getenv("MODEL_NAME", "claude-3-5-haiku-20241022"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2048,
    )

    messages = [
        SystemMessage(
            content=(
                "You are a software architect. "
                "Given a list of development tasks, produce a concise design document "
                "that specifies the data model and API endpoints needed to implement them."
            )
        ),
        HumanMessage(
            content=f"""Create a design document for the following tasks:

{tasks_text}

Include:
1. Data Model: field names, types, and descriptions
2. API Endpoints: method, path, request body, response schema
3. Notes on error handling

Format it as structured plain text (no code blocks needed, just clear sections).
"""
        ),
    ]

    response = llm.invoke(messages)
    design = response.content.strip()

    print(f"\nOutput — Design document ({len(design)} chars):")
    print("-" * 40)
    print(design[:600] + ("..." if len(design) > 600 else ""))
    print("-" * 40)

    return {"design": design}
