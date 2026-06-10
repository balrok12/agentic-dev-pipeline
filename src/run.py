"""Entry point: run the agentic pipeline from the command line."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _check_env() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.")
        print("Copy .env.example to .env and add your key.")
        sys.exit(1)


def _save_output(code: str, requirement: str) -> str:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"todo_api_{timestamp}.py"
    filename.write_text(code, encoding="utf-8")
    return str(filename)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agentic development pipeline — generates a FastAPI app from a requirement."
    )
    parser.add_argument(
        "--requirement",
        type=str,
        default="Create a REST API for todo management with full CRUD operations.",
        help="Natural-language requirement to implement",
    )
    args = parser.parse_args()

    _check_env()

    # Import here so dotenv is loaded before langchain initialises
    from src.pipeline import PipelineState, build_pipeline

    pipeline = build_pipeline()

    initial_state: PipelineState = {
        "requirement": args.requirement,
        "tasks": [],
        "design": "",
        "code": "",
        "qa_passed": False,
        "qa_feedback": "",
        "retry_count": 0,
        "retrospection": "",
        "output_path": "",
    }

    print("\n" + "=" * 60)
    print("  AGENTIC DEVELOPMENT PIPELINE")
    print("=" * 60)
    print(f"Requirement: {args.requirement}")

    final_state = pipeline.invoke(initial_state)

    # Save generated code
    if final_state.get("code"):
        output_path = _save_output(final_state["code"], args.requirement)
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"QA result  : {'PASSED' if final_state.get('qa_passed') else 'FAILED'}")
        print(f"Output file: {output_path}")
        print(f"\nRetrospection:\n{final_state.get('retrospection', '')}")
    else:
        print("\nPipeline completed but no code was generated.")


if __name__ == "__main__":
    main()
