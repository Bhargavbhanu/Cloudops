from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .assistant import answer_question
from .pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CloudScore agent locally.")
    parser.add_argument("--data", required=True, help="Path to cloud usage JSON export")
    parser.add_argument(
        "--question",
        default="What should we focus on?",
        help="Question for the DEX assistant",
    )
    args = parser.parse_args()

    profile = run_pipeline(args.data)
    answer = answer_question(profile, args.question)
    print(json.dumps({"profile": asdict(profile), "answer": answer}, indent=2, default=str))


if __name__ == "__main__":
    main()
