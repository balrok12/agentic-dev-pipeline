"""Retrospector agent: summarises the pipeline cycle and extracts one improvement point."""

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage


def run_retrospector(state: dict) -> dict:
    print("\n" + "=" * 60)
    print("[5/5] RETROSPECTOR — Summarising cycle")
    print("=" * 60)

    llm = ChatAnthropic(
        model=os.getenv("MODEL_NAME", "claude-3-5-haiku-20241022"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=512,
    )

    qa_status = "PASSED" if state.get("qa_passed") else f"FAILED after {state.get('retry_count', 0)} attempt(s)"

    messages = [
        SystemMessage(
            content=(
                "You are a technical lead conducting a development sprint retrospective. "
                "Summarise what happened and identify one concrete improvement for the next cycle."
            )
        ),
        HumanMessage(
            content=f"""Sprint retrospective for this pipeline run:

Original requirement: {state['requirement']}

Tasks identified: {len(state.get('tasks', []))}
QA result: {qa_status}
QA feedback (if any): {state.get('qa_feedback') or 'None'}

Provide:
1. One-sentence summary of what was accomplished.
2. One concrete improvement for the next cycle (start with "Next cycle:").

Keep it brief and actionable.
"""
        ),
    ]

    response = llm.invoke(messages)
    retrospection = response.content.strip()

    print(f"\nRetrospection:\n{retrospection}")

    return {"retrospection": retrospection}
