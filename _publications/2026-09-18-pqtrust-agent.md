---
title: 'PQTrust-Agent: Policy-Compiled Post-Quantum Trust Contracts for Web-of-Agents Communications'
collection: publications
output_type: conference-record
permalink: /publication/2026-09-18-pqtrust-agent/
date: 2026-09-18
publication_year: 2026
event_month: 2026-12
venue: IEEE/WIC/ACM WI-IAT 2026
authors:
- Yulliwas Ameur
- Insaf Imene Lasledj
- Samia Bouzefrane
halurl: https://hal.science/hal-05743305
status: Accepted conference paper; proceedings forthcoming.
bibtexurl: /files/publications.bib
citation: 'Yulliwas Ameur; Insaf Imene Lasledj; Samia Bouzefrane. "PQTrust-Agent: Policy-Compiled Post-Quantum Trust Contracts for Web-of-Agents Communications." IEEE/WIC/ACM WI-IAT 2026. HAL: hal-05743305.'
pdfurl: /publication/2026-09-18-pqtrust-agent/paper.pdf
codeurl: https://github.com/Insaf19/PQtrust-agent-artifact
excerpt: Autonomous Web agents can agree on a task while enforcing incompatible cryptographic, fallback, resumption, and lease policies. This paper presents PQTrust-Agent, a constraint-first bilateral authorization protocol. Each…
---

**Status:** Accepted conference paper; proceedings forthcoming.

**Conference period:** 2026-12. The page date records this listing; it is not a proceedings publication date.

## Abstract

Autonomous Web agents can agree on a task while enforcing incompatible cryptographic, fallback, resumption, and lease policies. This paper presents PQTrust-Agent, a constraint-first bilateral authorization protocol. Each endpoint compiles private capability and hard-policy constraints into a local safe set; commit–reveal locks the disclosed negotiation inputs; and selection is restricted to the common measured-cost Pareto frontier. The outcome is an RFC-8785-canonical task contract signed by both endpoints with ML-DSA and enforced before real TLS 1.3 and task execution; endpoint TLS authentication remains classical X.509. Infeasibility yields a verifiable subset-minimal conflict certificate and a fail-closed abort, with no weaker retry. In a pre-specified 1,040-observation single-machine campaign, all 480 feasible sessions completed, all 150 infeasible sessions aborted before TLS and task execution, and all 200 author-designed conformance and robustness mutations were rejected with their expected outcomes. Median end-to-end latency was 432.7–537.6 ms; minimax itself took 5.25 ms, with no statistically detected runtime or resource difference from three safe baselines. Three of the four feasible scenarios had singleton frontiers. On the only non-singleton evaluated P0/P3 frontier, minimax coincided with canonical-first-safe and minimum-total-cost in all 1,210 preference conflicts; relative to either endpoint’s unilateral minimum-cost selector, it reduced maximum regret in 605 conflicts and tied in 605. Distinct minimax decisions relative to those two safe heuristics appeared only in an explicitly post-hoc constructed 15-profile frontier, while no profitable unilateral misreport was observed on the tested finite grid. These results support an auditable task-scoped fail-closed mechanism, not complete post-quantum endpoint authentication or Internet-scale performance.

## Open manuscript

The PDF is an author manuscript, with an IEEE copyright and version notice. The version of record will be linked when its DOI is available.
