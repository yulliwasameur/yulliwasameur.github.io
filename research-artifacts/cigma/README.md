> Archived snapshot, 19 August 2026. Validation on 18 September 2026: 33/34 existing tests passed; one paper-macro export-consistency check failed. Read [PUBLICATION_VALIDATION.md](PUBLICATION_VALIDATION.md) before using the archived results.

# CIGMA reproducibility artifact

This directory contains the offline experimental artifact for the CIGMA paper
revision. It provides a deterministic, evidence-grounded benchmark rather than
an enterprise deployment or a user study. The executable path is:

1. generate heterogeneous observations from TLS, PKI, code/SBOM, CI/CD, CMDB,
   and OT sources;
2. keep the evaluator oracle physically and programmatically separate;
3. normalize records, resolve entities, enforce a closed typed ontology, and
   attach evidence identifiers to every accepted edge;
4. compare two single-source inventories, a flat source union, exact direct
   rules, CIGMA fusion, and four CIGMA ablations;
5. evaluate inventory, entity resolution, typed edges, ranking, calibration,
   critical misses, source dropout, and observation dropout;
6. export machine-readable tables, bootstrap intervals, paired randomization
   tests, a figure, and LaTeX macros.

The default test and campaign paths make no network request, embed no
credential, and call no LLM API. Its runtime dependencies are Python plus
NumPy, pandas, scikit-learn, SciPy, Matplotlib, and PyYAML.
The locked dependencies require Python 3.11 or newer. The checked commands and
outputs were revalidated on Ubuntu 24.04.3 LTS (x86-64) with CPython 3.12.13.

## Quick start

From this directory:

```bash
python3 -m pip install -r requirements-lock.txt
make test
make campaign
```

Equivalent direct command:

```bash
PYTHONPATH=src MPLCONFIGDIR=.mplconfig \
  python3 -m cigma.cli campaign \
  --config configs/default.yaml \
  --output results/default
```

The CLI refuses configuration and output paths outside this artifact and
requires campaign outputs to be named directories below `results/`.
`requirements-lock.txt` pins the environment used for the checked results;
`manifest.json` records the versions observed at execution time.

## Benchmark and oracle boundary

`CIGMA-Lab` models an internet TLS edge, patient/authentication services, a
TLS-enabled PostgreSQL database, enterprise PKI, source and SBOM observations,
CI/CD pipelines, CMDB ownership/context, and an OT gateway with a PLC. Assets
appear under source-specific local names so that cross-source resolution is
measured rather than assumed.

The default fixture contains 46 entity observations and 34 claim observations
from six source families. Evaluator truth contains 23 canonical nodes and 34
typed edges. The split is explicit:

```text
results/default/data/
├── public/observations.json   # only method input
└── oracle/oracle.json         # evaluator only
```

Public records include source, local identifier, collection time, quality,
evidence locator/excerpt, and a SHA-256 digest of that excerpt (not of a raw
source file). They contain no truth
ID, priority, migration label, or observation-to-truth map. Construction and
scoring functions receive only the public payload; the oracle is passed to the
evaluator after predictions exist.

## Evidence-grounded graph

`src/cigma/ontology.py` defines the closed node and relation vocabulary. The
pipeline validates relation signatures, rejects unknown or quarantined
endpoints, and rejects observations below the configured quality gate. Every
accepted direct or derived edge carries non-empty `evidence_ids`. The only
derived `service USES algorithm` paths are declared in the ontology:

```text
service --HOSTS--> endpoint --PRESENTS--> certificate --USES--> algorithm
service --USES--> software_component --USES--> algorithm
```

Optional LLM output is never trusted as a graph update. The bounded contract in
`prompts/bounded_llm_system.txt` permits only existing node IDs, closed-ontology
predicates, and non-empty supplied evidence IDs. `validate_candidate_batch` in
`src/cigma/openai_adapter.py` rejects missing, unknown, unrelated, mistyped, or
out-of-ontology evidence/claims. Accepted candidates remain in a separate file
and never mutate the measured graph.

The optional Responses API adapter has two independent opt-ins: set
`openai_adapter.enabled: true` in a deliberate configuration and invoke the
`llm-generate` CLI command with `--enable-openai`. It reads a key only from the
process environment, sets remote storage off, and never logs or serializes the
credential. `llm-replay` validates a previously saved response offline. Neither
command is invoked by `make test` or `make campaign`; no LLM result is included
in the deterministic default tables.

### Separate optional live trace

`results/llm/` archives three separately authorized Responses API calls made
with `gpt-5.6-luna`, plus deterministic replay decisions and an oracle-side
post-hoc evaluation. Each request manifest records the requested and returned
model, schema/prompt/input hashes, token usage, and `store: false`; it contains
no credential. These network traces are deliberately excluded from
`results/default/manifest.json` and from every default campaign metric.

The bounded request omitted the evaluator oracle, existing graph edges,
computed scores, and the structured `attributes` field. It did retain verbatim
public evidence excerpts; those synthetic excerpts explicitly contain observed
business context such as criticality, exposure, data lifetime, migration time,
and agility. This declared boundary is enforced by a structural-key test and
must not be summarized as “the model saw no attributes.”

Revalidate a saved response without a key or network access:

```bash
PYTHONPATH=src python3 -m cigma.cli llm-replay \
  --public results/default/data/public/observations.json \
  --graph results/default/graphs/cigma_no_paths.json \
  --raw-response results/llm/run01/raw_response.json \
  --output results/llm/replay-run01
```

Recompute the separate oracle-side evaluation after all replays are frozen:

```bash
PYTHONPATH=src python3 scripts/evaluate_llm_runs.py \
  --public results/default/data/public/observations.json \
  --oracle results/default/data/oracle/oracle.json \
  --base-graph results/default/graphs/cigma_no_paths.json \
  --validation-graph results/default/graphs/cigma_no_paths.json \
  --runs-root results/llm \
  --output results/llm/evaluation
```

The three calls are repetitions on one synthetic fixture, not independent
organizations or a model comparison. Per-call wall-clock latency is retained
only as request provenance and is not used as performance evidence.
They are the first complete triplicate used for the manuscript analysis. Their
live payload preceded a fixture consistency correction: the synthetic root
certificate stated `key_bits=3072` while its linked identifier was `RSA-2048`;
the current fixture states `2048`. Reconstructing that single pre-correction
field and its evidence digest reproduces the archived public-input, no-path
graph, and bounded-input hashes. Relation observations and canonical node IDs
did not change, and the current stricter validator reproduces the archived
accepted/rejected partitions exactly. The evaluator contains a versioned hash
registry for the raw responses and request manifests so a later call cannot
silently replace this triplicate.
The reported union combines the no-path CIGMA graph and validated candidates on
their shared canonical node IDs. It is executable after CIGMA entity resolution
and isolates candidate path composition, but it is not an independent end-to-end
LLM pipeline.

The frozen post-hoc evaluation reports macro means over unique canonical
triples. Raw candidates have precision/recall/F1
`0.9285 / 0.8725 / 0.8978`; validated candidates have
`1.0000 / 0.8725 / 0.9305`; and the no-path CIGMA union
has `1.0000 / 0.9020 / 0.9471`. The validator rejects 6.5% of raw candidate
objects. Against the evaluator oracle, the mean false-triple rate is 7.2%
before and 0.0% after validation. Mean incremental recall is 0.3333 over the
five relations absent from the no-path graph (per-run recall: 0/5, 0/5, 5/5),
and mean pairwise Jaccard agreement after validation is 0.8990.
These values are conditional on CIGMA entity resolution already being supplied
to the model; they do not measure end-to-end graph construction.

## Compared methods

| Method | Behavior |
|---|---|
| `tls_inventory` | TLS-only inventory, no cross-source resolution |
| `cbom_inventory` | code/SBOM-only inventory, no cross-source resolution |
| `source_union` | all sources concatenated without entity resolution |
| `exact_direct` | stable-identifier resolution and direct typed claims |
| `cigma` | stable identifiers, configured type-compatible non-conflicting aliases, quality gates, and allowed path composition |

The campaign also evaluates `cigma_no_alias`, `cigma_no_paths`,
`cigma_no_quality_gate`, and `cigma_uniform_reliability`. Six
leave-one-source-out CIGMA runs quantify dependence on TLS, PKI, code, CI/CD,
CMDB, and OT evidence.

## Urgency, ranking, and confidence

The primary ranking is deliberately weight-free. It orders the conservative
policy-tier upper bound, then the observed lower bound, a Pareto front computed
only among assets with that same `(upper bound, lower bound)` tier interval,
and a deterministic lexicographic ordering of declared impact factors. An
asset in another tier interval therefore cannot change an intra-tier front.
The exported weighted score is a sensitivity baseline, not the primary policy.

For an asset and its service context, the implementation computes:

- quantum vulnerability from the versioned deterministic
  `ALGORITHM_QUANTUM_VULNERABILITY_V1` policy keyed by normalized algorithm ID
  (`rsa-2048=1.0`, `ecdsa-p256=1.0`, `aes-256-gcm=0.15`); source-provided risk
  attributes do not affect scoring, and an unlisted ID remains unknown;
- HNDL urgency as `QV × clip((data lifetime + migration time) / horizon)`;
- blast radius as the fraction of services transitively depending on its
  service context;
- criticality and exposure from evidence-grounded attributes.

Agility is exported separately as migration feasibility. It is absent from the
policy tier, Pareto fronts, and every primary tie-break; changing agility cannot
change primary urgency or rank. It appears only in the legacy weighted
sensitivity baseline.

Three concepts remain separate:

- `primary_rank_score` is an ordering surrogate derived from the policy rank;
- `calibrated_urgency_probability` is Platt scaling of the weighted policy
  baseline on the versioned synthetic panel in `fixtures/`;
- `epistemic_confidence` is the minimum supporting node/algorithm-edge
confidence and controls `verification_required`.

Every unknown impact factor has explicit `impact_lower_*=0` and
`impact_upper_*=1` bounds. Diagnostic factor fields may retain an imputed value
(for example HNDL computed with a missing lifetime), but those values never
enter the lower policy tier. The scorer also exports missing-factor names and a
completeness flag. A potentially high-impact incomplete item is ranked using
its conservative bound and sent to the verification queue. When no supporting
algorithm edge exists, epistemic confidence is the node confidence multiplied
by the fixed `0.5` missing-support penalty; a unit test fixes this rule.

The calibration panel is independent from the benchmark oracle but is
synthetic. It is not expert correctness data, and the artifact makes no claim
of expert-calibrated confidence. Changing epistemic confidence does not alter
policy tier or rank; a unit test enforces that invariant.

## Metrics and robustness design

The oracle-side evaluator reports:

- asset precision/recall/F1 and pairwise entity-resolution precision/recall/F1;
- B³ precision/recall/F1 over observable mentions;
- typed-edge precision/recall/F1 and unsupported-edge rate;
- critical-miss count/rate;
- NDCG@5, NDCG@10, Spearman, Kendall tau-b, and urgent recall@5 for primary,
  weighted, rank-aggregation, and calibrated rankings;
- edge-confidence and urgency-probability Brier score and ECE;
- verification-queue size and the provenance invariant.

Robustness uses 32 deterministic missing-observation masks at dropout levels
0%, 10%, 25%, and 50% for `source_union`, `exact_direct`, and `cigma`: 128
scenarios and 384 method runs. The campaign exports seeded bootstrap 95%
intervals and paired sign-randomization tests at nonzero dropout. It does not
compute a p-value from the 32 identical zero-dropout observation sets; their
replicate metadata seeds differ. These masks are repeated
perturbations of one synthetic scenario, not 32 independent organizations.

## Default measured run

The checked `results/default` directory is generated by `make campaign` under
the default configuration. Current CIGMA measurements are:

| Quantity | Value |
|---|---:|
| Asset F1 | 1.0000 |
| Entity pairwise F1 / B³ F1 | 1.0000 / 1.0000 |
| Typed-edge F1 / unsupported-edge rate | 1.0000 / 0.0000 |
| Critical misses | 0 / 16 |
| NDCG@5 / NDCG@10 | 0.8948 / 0.8984 |
| Kendall tau-b | 0.2737 |
| Edge Brier / urgency Brier | 0.0228 / 0.0985 |

Perfect graph recovery is specific to this small deterministic fixture. Under
50% observation dropout, mean CIGMA asset F1 is 0.8075 and mean edge F1 is
0.2101 across the 32 masks. These results do not establish external validity,
analyst-effort reduction, or superiority on production infrastructure.

## Outputs

```text
results/default/
├── config.snapshot.yaml
├── manifest.json
├── summary.json
├── paper_macros.tex
├── data/{public,oracle}/
├── graphs/                  # typed predictions and rejections
├── rankings/               # per-method ranks and factors
├── evaluation/             # evaluator details
├── metrics/
│   ├── method_metrics.csv
│   ├── robustness_runs.csv
│   ├── robustness_aggregate.csv
│   ├── statistics.csv
│   ├── leave_one_source_out.csv
│   ├── calibrator.json
│   └── robustness_summary.json
└── figures/campaign_metrics.png
```

`manifest.json` records SHA-256 hashes of all result files, package versions,
the seed, the oracle-isolation statement, and that no network is required.
The separately authorized network trace has its own per-run request manifests
and replay hashes under `results/llm/`; its post-hoc evaluator writes a separate
`results/llm/evaluation/manifest.json`. None is covered by the deterministic
campaign manifest.

The manuscript's result macros are composed deterministically from the frozen
default and LLM JSON/CSV outputs; no measured number is embedded in the export
script. Regenerate them after both result sets are stable, or verify the
checked-in file without changing it:

```bash
make paper-macros
make paper-macros-check
```

`tests/test_paper_macros.py` performs the same export into a temporary file and
requires a byte-for-byte match with `../paper/results_macros.tex`.

## Explicitly out of scope

The checked default campaign does not measure a live model, unsupported-claim
rates before/after validation, token/cost behavior, or model comparisons. The
three-call optional trace reports validation effects and token counts only as a
separate, bounded experiment; it does not estimate cost or generalize beyond
the fixture. This release also does not implement n8n export, temporal
`valid_from`/`valid_to` semantics, contradiction objects, expert or analyst user
studies, production-scale throughput, or enterprise external validation.
Host-dependent wall-clock measurements are excluded from deterministic outputs.
Paper claims in any of these areas require separate evidence.

## Tests

The `unittest` suite covers deterministic generation, six-source coverage,
oracle isolation, evidence-digest integrity, graph fusion, fail-closed claim
validation, urgency/confidence independence, and a complete campaign smoke run
including robustness aggregates, leave-one-source-out output, macros, and the
summary bounds. It also replays and evaluates the three archived LLM responses
offline, verifies their hashes/partitions, and checks that unmapped baseline
edges remain false positives; this test makes no network request.
