---
layout: single
title: "Research highlights: privacy, cryptography and AI security"
permalink: /research-highlights/
author_profile: true
description: "English contribution summaries for five featured publications by Yulliwas Ameur, with research questions, limitations, citations and available code."
---

These five contributions are the works featured on my [ORCID profile](https://orcid.org/0000-0003-1435-2982). Each summary explains the question, the contribution and the scope of the evidence. Updated 19 September 2026.

[All publications](/publications/) · [Bibliography in BibTeX](/files/publications.bib) · [Research code](/code/) · [Professional contact](mailto:yulliwas.ameur@efrei.fr)

## Secure k-means clustering on encrypted data

**Question.** How can a cloud service assign records to clusters while keeping those records encrypted?

**Contribution.** The protocol uses TFHE comparisons to evaluate the assignment step on encrypted distances. The client decrypts the assignment vectors once per iteration, updates centroids locally, and returns the refreshed centroids. The server does not decrypt the data.

**Evidence and scope.** The paper compares encrypted clustering with plaintext Forgy k-means on real datasets. Clustering quality remains close for moderate cluster counts. The design requires client participation in each iteration, and bootstrapping dominates server runtime.

**Use and citation.** Relevant to privacy-preserving analytics and interactive encrypted clustering. Rezak Aziz, Yulliwas Ameur, Vincent Audigier and Samia Bouzefrane, *Procedia Computer Science* 280 (2026), 576–583. [Publication and abstract](/publication/2026-04-16-ant2026-secure-kmeans) · [Publisher DOI](https://doi.org/10.1016/j.procs.2026.04.073).

## Homomorphic encryption with differential privacy

**Question.** How do encryption and differential privacy affect the balance between classifier accuracy, computation and privacy?

**Contribution.** The paper combines the two mechanisms in a client–server model and studies sensitivity to the choices of privacy and noise parameters.

**Evidence and scope.** The study reports initial observations and parameter trade-offs. Its scope is an exploration of the hybrid model; individual deployments still need their own privacy accounting and utility evaluation.

**Use and citation.** Relevant to hybrid privacy mechanisms for machine learning. Yulliwas Ameur, Samia Bouzefrane and Soumya Banerjee, *Journal of Cyber Security and Mobility* 13(5) (2024), 863–886. [Publication and abstract](/publication/2024-07-01-jcsm-adaptive-he-dp) · [Publisher DOI](https://doi.org/10.13052/jcsm2245-1439.1353) · [HAL record](https://hal.science/hal-05330716).

## GovSecLLM++: security testing and governance evidence

**Question.** How can evaluations of LLM applications connect security tests to inspectable governance evidence?

**Contribution.** GovSecLLM++ provides a benchmark and artifact package with scoring utilities, strict rescoring outputs, adaptive test outputs, human-validation summaries and a data card. The public package uses synthetic secrets, policy records and credentials.

**Evidence and scope.** The available software and dataset support inspection of the recorded experiments. They have their own authors and persistent identifiers. The paper's final PDF is not included in the current code release, and the workshop proceedings DOI has not yet been verified.

**Use and citation.** Cite the exact software or dataset version used, in addition to the paper when discussing its contribution. Paper authors: Yulliwas Ameur, Insaf Imene Lasledj, Samia Bouzefrane and Lyes Khoukhi. SecAI, ESORICS 2026. [Paper record](/publication/2026-09-18-govsecllm-paper/) · [Code](https://github.com/yulliwasameur/GovSecLLMpp-SECAI2026) · [Software DOI](https://doi.org/10.5281/zenodo.20636767) · [Dataset version DOI](https://doi.org/10.5281/zenodo.20646702).

## PQTrust-Agent: enforcing compatible cryptographic policies

**Question.** How can two autonomous agents agree on a task without silently weakening incompatible security policies?

**Contribution.** Each endpoint compiles its hard constraints into a safe set. Commit–reveal fixes the negotiation inputs. A jointly signed task contract records the selected profile, while an empty intersection produces a verifiable conflict certificate and an abort before task execution.

**Evidence and scope.** The manuscript reports a pre-specified, single-machine campaign of 1,040 observations. Endpoint TLS authentication remains classical X.509. Most feasible scenarios had only one candidate on the common frontier, limiting conclusions about the advantage of the minimax selector. The findings do not establish Internet-scale performance or complete post-quantum endpoint authentication.

**Use and citation.** Yulliwas Ameur, Insaf Imene Lasledj and Samia Bouzefrane. Accepted for WI-IAT 2026, proceedings forthcoming. [Paper and abstract](/publication/2026-09-18-pqtrust-agent/) · [Author manuscript (PDF)](/publication/2026-09-18-pqtrust-agent/paper.pdf) · [Canonical code repository](https://github.com/Insaf19/PQtrust-agent-artifact) · [HAL record](https://hal.science/hal-05743305).

## AgentFlowShield: limiting information in agent traffic metadata

**Question.** What can an observer infer about an LLM agent from encrypted traffic sizes and timing, and how can the agent reduce that information?

**Contribution.** AgentFlowShield shapes outgoing traffic using the agent's execution phase. Its mechanisms include padding, frame aggregation, bounded jitter and envelopes for tool and memory activity.

**Evidence and scope.** The manuscript evaluates 6,300 controlled traces. Results depend on the attack and split: the policy-aware A1 fusion result falls from 0.995 AUPRC under random padding to 0.442 under the full defense, while standard-split attacks still retain strong signals. The loopback testbed uses synthetic WAN noise. These results do not establish the removal of metadata leakage in production networks.

**Use and citation.** Redha Boukhari, Yulliwas Ameur and Mehammed Daoui. Accepted for AICCSA 2026, proceedings forthcoming. [Paper and abstract](/publication/2026-09-18-agentflowshield/) · [Author manuscript (PDF)](/publication/2026-09-18-agentflowshield/paper.pdf) · [Author presentation (PowerPoint)](/publication/2026-09-18-agentflowshield/slides.pptx) · [HAL record](https://hal.science/hal-05743316).

## Related work in detection engineering

[ANUBIS: measuring detection improvement](/publication/2026-09-18-detection-engineering/) distinguishes alerts that fire from alerts with the correct ATT&CK mapping. [LLM4Sec: constraining rule generation](/publication/2026-09-18-knowledge-graph-siem/) investigates whether knowledge-graph context improves the structural correctness of generated Sigma rules. [Context vs. Compute](/publication/2026-09-19-context-vs-compute/) extends the comparison across model capacities and context conditions.
