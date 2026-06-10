"""Analyst agent: breaks down a natural-language requirement into atomic tasks."""

import json
import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


def run_analyst(state: dict) -> dict:
    print("\n" + "=" * 60)
    print("[1/5] ANALYST — Analyzing requirements")
    print("=" * 60)
    print(f"Input: {state['requirement']}")

    llm = ChatAnthropic(
        model=os.getenv("MODEL_NAME", "claude-3-5-haiku-20241022"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=1024,
    )

    messages = [
        SystemMessage(
            content=(
                "You are a software requirements analyst. "
                "Your job is to break down a user requirement into clear, atomic development tasks."
            )
        ),
        HumanMessage(
            content=f"""Analyze the following requirement and decompose it into a list of development tasks.

Requirement: {state['requirement']}

Rules:
- Each task must be specific and actionable.
- Focus on API/backend tasks (data model, endpoints, validation, error handling).
- Return ONLY a JSON array of task strings, no additional text.

Example output:
["Task 1: Define data model with fields X, Y, Z", "Task 2: Implement GET /items endpoint", "Task 3: Implement POST /items endpoint"]
"""
        ),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    try:
        tasks = json.loads(raw)
        if not isinstance(tasks, list):
            raise ValueError("Expected a list")
    except (json.JSONDecodeError, ValueError):
        # Graceful fallback: treat each non-empty line as a task
        tasks = [line.strip().strip('"').strip(",") for line in raw.splitlines() if line.strip()]

    print(f"\nOutput — {len(tasks)} tasks identified:")
    for task in tasks:
        print(f"  • {task}")

    return {"tasks": tasks}
