---
title: 'AgentFlowShield: Defending LLM Agents Against Metadata Side Channels'
collection: publications
output_type: conference-record
permalink: /publication/2026-09-18-agentflowshield/
date: 2026-09-18
publication_year: 2026
event_month: 2026-10
venue: AICCSA 2026
authors:
- Redha Boukhari
- Yulliwas Ameur
- Mehammed Daoui
halurl: https://hal.science/hal-05743316
status: Accepted conference paper; proceedings forthcoming.
bibtexurl: /files/publications.bib
citation: 'Redha Boukhari; Yulliwas Ameur; Mehammed Daoui. "AgentFlowShield: Defending LLM Agents Against Metadata Side Channels." AICCSA 2026. HAL: hal-05743316.'
pdfurl: /publication/2026-09-18-agentflowshield/paper.pdf
excerpt: Tool-augmented LLM agents produce structured, multi-phase network traffic whose encrypted metadata—packet sizes, inter-arrival times, burst boundaries, and streaming cadence—can reveal which tools were invoked, whether r…
---

**Status:** Accepted conference paper; proceedings forthcoming.

**Conference period:** 2026-10. The page date records this listing; it is not a proceedings publication date.

## Abstract

Tool-augmented LLM agents produce structured, multi-phase network traffic whose encrypted metadata—packet sizes, inter-arrival times, burst boundaries, and streaming cadence—can reveal which tools were invoked, whether retrieval or memory was used, and coarse properties of the underlying task. We study this leakage in a scoped single-endpoint deployment model and introduce AgentFlowShield, a phase-aware egress shaping layer combining bucket padding, frame aggregation, bounded jitter, tool normalisation, memory envelopes, and a risk-aware controller. On a 6,300-trace controlled testbed we evaluate six inference attacks under no-defence, generic, and phaseaware defences, probe generalisation with a template-disjoint split, and evaluate three defence-aware adversaries. We provide a bounded within-phase size-channel analysis, identify residual leakage channels, and demonstrate the defence architecture in a controlled loopback testbed with synthetic WAN noise. AgentFlowShield-full preserves low engineering overhead (24 % measured latency overhead in the final utility run) but does not eliminate leakage against the strongest standard-split adversaries (97-100% residual AUPRC on A1-A4). Its clearest gains appear in the template-disjoint and policy-aware settings: D9 shows mixed results in unseen-template splits, with workflow-type AUPRC increasing from 0.385 to 0.453 (indicating higher detectability) and tool-type decreasing from 0.512 to 0.490, while policy-aware A1 fusion drops from 0.995 under random padding to 0.442 under D9. The final results therefore show a narrower but more defensible claim: phase-aware shaping helps generalisation-resistant and calibrated attacks, but fixed-envelope defences still leave strong residual standard-split signals.

## Open manuscript

The PDF is an author manuscript, with an IEEE copyright and version notice. The version of record will be linked when its DOI is available.
