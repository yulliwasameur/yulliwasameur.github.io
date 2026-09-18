"""Compatibility wrapper around the single measured graph pipeline.

New experiments should import :func:`cigma.pipeline.run_pipeline` directly.
This module preserves the initial prototype method names without maintaining a
second implementation.
"""

from __future__ import annotations

from typing import Any

from .model import GraphResult
from .pipeline import MethodSpec, run_pipeline


def build_graph(
    public: dict[str, Any],
    config: dict[str, Any],
    method: str,
    source: str | None = None,
) -> GraphResult:
    aliases: dict[str, str] = {
        "flat_union": "source_union",
        "deterministic_rules": "exact_direct",
        "cigma": "cigma",
    }
    if method == "single_source":
        if source is None:
            raise ValueError("single_source requires source")
        spec = MethodSpec(
            name=f"single_{source}",
            sources=(source,),
            resolution="strong",
            min_entity_quality=0.0,
            min_claim_quality=0.0,
            derive_paths=False,
        )
        return run_pipeline(public, config, spec)
    if method not in aliases:
        raise ValueError(f"unknown compatibility method: {method}")
    graph = run_pipeline(public, config, aliases[method])
    graph.metadata["compatibility_alias"] = method
    if method != "cigma":
        graph.method = method
    return graph
