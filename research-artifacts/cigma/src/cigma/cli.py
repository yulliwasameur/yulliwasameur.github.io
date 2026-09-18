"""Command-line interface for deterministic generation and evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import generate_benchmark
from .experiment import ARTIFACT_ROOT, load_config, materialize_dataset, run_campaign
from .io import read_json, safe_clean_output
from .model import graph_result_from_dict
from .openai_adapter import generate_candidates, replay_candidates


def _artifact_path(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()
    root = ARTIFACT_ROOT.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"refusing path outside artifact root: {candidate}")
    return candidate


def _results_path(value: str) -> Path:
    candidate = _artifact_path(value)
    results_root = (ARTIFACT_ROOT / "results").resolve()
    if candidate == results_root or results_root not in candidate.parents:
        raise ValueError(f"output must be a named directory below {results_root}")
    return candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CIGMA reproducibility artifact")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ["generate", "campaign"]:
        child = subparsers.add_parser(command)
        child.add_argument("--config", required=True)
        child.add_argument("--output", required=True)
    clean = subparsers.add_parser("clean")
    clean.add_argument("--output", required=True)
    llm_generate = subparsers.add_parser(
        "llm-generate", help="explicitly call the optional bounded Responses API adapter"
    )
    llm_generate.add_argument("--config", required=True)
    llm_generate.add_argument("--public", required=True)
    llm_generate.add_argument("--graph", required=True)
    llm_generate.add_argument("--output", required=True)
    llm_generate.add_argument("--enable-openai", action="store_true", required=True)
    llm_replay = subparsers.add_parser(
        "llm-replay", help="replay deterministic validation of a saved raw response"
    )
    llm_replay.add_argument("--public", required=True)
    llm_replay.add_argument("--graph", required=True)
    llm_replay.add_argument("--raw-response", required=True)
    llm_replay.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = _results_path(args.output)
    if args.command == "clean":
        safe_clean_output(output)
        return 0

    if args.command in {"llm-generate", "llm-replay"}:
        public = read_json(_artifact_path(args.public))
        graph = graph_result_from_dict(read_json(_artifact_path(args.graph)))
        if args.command == "llm-generate":
            config = load_config(_artifact_path(args.config))
            result = generate_candidates(
                public,
                graph,
                config,
                output,
                explicitly_enabled=bool(args.enable_openai),
            )
        else:
            result = replay_candidates(
                public,
                graph,
                _artifact_path(args.raw_response),
                output,
            )
        print(
            json.dumps(
                {
                    "output": str(output),
                    "accepted": len(result["accepted"]),
                    "rejected": len(result["rejected"]),
                    "graph_mutated": False,
                },
                sort_keys=True,
            )
        )
        return 0

    config_path = _artifact_path(args.config)
    config = load_config(config_path)
    if args.command == "generate":
        public, oracle = generate_benchmark(config)
        materialize_dataset(public, oracle, output)
        print(json.dumps({"output": str(output), "entities": len(public["entities"])}, sort_keys=True))
        return 0
    if args.command == "campaign":
        summary = run_campaign(config, output)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
