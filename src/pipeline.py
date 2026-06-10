"""LangGraph pipeline orchestration for the agentic development workflow."""

from typing import TypedDict

from langgraph.graph import END, StateGraph

from src.agents.analyst import run_analyst
from src.agents.architect import run_architect
from src.agents.developer import run_developer
from src.agents.qa import run_qa
from src.agents.retrospector import run_retrospector


class PipelineState(TypedDict):
    requirement: str
    tasks: list[str]
    design: str
    code: str
    qa_passed: bool
    qa_feedback: str
    retry_count: int
    retrospection: str
    output_path: str


def _route_after_qa(state: PipelineState) -> str:
    """Conditional edge: retry developer up to MAX_RETRY times, then retrospect."""
    max_retry = int(__import__("os").getenv("MAX_RETRY", "2"))
    if state.get("qa_passed"):
        return "retrospector"
    if state.get("retry_count", 0) < max_retry:
        return "developer"
    return "retrospector"


def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("analyst", run_analyst)
    graph.add_node("architect", run_architect)
    graph.add_node("developer", run_developer)
    graph.add_node("qa", run_qa)
    graph.add_node("retrospector", run_retrospector)

    graph.set_entry_point("analyst")
    graph.add_edge("analyst", "architect")
    graph.add_edge("architect", "developer")
    graph.add_edge("developer", "qa")
    graph.add_conditional_edges(
        "qa",
        _route_after_qa,
        {
            "developer": "developer",
            "retrospector": "retrospector",
        },
    )
    graph.add_edge("retrospector", END)

    return graph.compile()
