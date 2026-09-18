---
title: 'From Attack Scenario to Measurable Detection Improvement: A Knowledge-Driven ATT&CK/D3FEND Framework for Instrumented Purple Teaming'
collection: publications
output_type: conference-record
permalink: /publication/2026-09-18-purple-teaming/
date: 2026-09-18
publication_year: 2026
event_month: 2026-11
venue: C&ESAR 2026
authors:
- Tristan Madani
- Yulliwas Ameur
- Samia Bouzefrane
halurl: https://hal.science/hal-05743354
status: Conference contribution listed in HAL; proceedings publication details are not yet verified.
bibtexurl: /files/publications.bib
citation: 'Tristan Madani; Yulliwas Ameur; Samia Bouzefrane. "From Attack Scenario to Measurable Detection Improvement: A Knowledge-Driven ATT&CK/D3FEND Framework for Instrumented Purple Teaming." C&ESAR 2026. HAL: hal-05743354.'
excerpt: Organizations run purple team exercises, find gaps, patch a few rules, and report success—but without a formal measurement framework, they cannot quantifyhow muchdetection improved orwhyspecific techniques went undetecte…
pdfurl: /publication/2026-09-18-purple-teaming/paper.pdf
---

**Status:** Conference contribution listed in HAL; proceedings publication details are not yet verified.

**Conference period:** 2026-11. The page date records this listing; it is not a proceedings publication date.

## Abstract

Organizations run purple team exercises, find gaps, patch a few rules, and report success—but without a formal measurement framework, they cannot quantifyhow muchdetection improved orwhyspecific techniques went undetected. Attack prediction models achieve strong F1 scores but produce no defensive output, while CTI knowledge graphs map threats to countermeasures without testing them on real telemetry. The gap betweenemulating an attackandproving that detection improvedremains open. We close this gap with a knowledge-graph-driven framework for instrumented purple teaming. Abidirectional knowledge graphencodes the full chain from ATT&CK technique to data source, detection strategy, analytic rule, log source, and sensor—not just the attack side. Each emulation step is annotated with expected telemetry and success criteria, so that when detection fails, backward traversal of the graph pinpointswhy: a missing log source, an absent rule, or an inadequate configuration. After targeted remediation, the same scenario is replayed and improvement is quantified through operational KPIs anchored by detection coverage (𝐶). We evaluate on four threat profiles—nation-state espionage (APT29), financial cybercrime (FIN6), state destructive operations (Sandworm), and big-game-hunting ransomware (Wizard Spider)—all sourced from the public CTID adversary emulation library [1]. The primary endpoint is detection coverage (𝐶), evaluated with a fixed-threshold decision rule (Δ𝐶 >0.10 in ≥3/4 scenarios). The four-step detection maturity ladder raises strict coverage from 𝐶0 = 23.1% (out-of-the-box SIEM) to 𝐶3 = 71.6% (with KGPT (Knowledge-Graph Purple Teaming)-guided rules), with the KG-guided rule engineering step alone contributing Δ𝐶3 = +30.3 percentage points on average. The decision rule is satisfied in all four scenarios.

## Available version

Author manuscript, 16 pages, archived on 13 May 2026. The PDF contains the authors’ CC BY 4.0 notice and is shared unchanged. The final proceedings version is not yet verified. Section 10 describes an artifact repository kept private during review; no public implementation is linked here.
