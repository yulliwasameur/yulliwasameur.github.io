---
title: 'SmartPQ-Shield for Policy-Bounded Safe-Action Bandits in Adaptive Post-Quantum TLS'
collection: publications
output_type: conference-record
permalink: /publication/2026-09-30-wiiat2026-smartpq-shield/
date: 2026-09-30
publication_year: 2026
event_month: 2026-12
venue: WIAA'26 workshop, IEEE/WIC WI-IAT 2026
authors:
- Insaf Imene Lasledj
- Yulliwas Ameur
- Samia Bouzefrane
status: Article accepté le 30 septembre 2026 (atelier WIAA'26) ; version finale déposée, actes IEEE à paraître.
bibtexurl: /files/publications.bib
citation: 'Insaf Imene Lasledj, Yulliwas Ameur, Samia Bouzefrane. "SmartPQ-Shield for Policy-Bounded Safe-Action Bandits in Adaptive Post-Quantum TLS." WIAA''26 workshop, IEEE/WIC WI-IAT 2026, décembre 2026.'
excerpt: 'A policy-bounded controller for adaptive post-quantum TLS: a contextual bandit ranks only admissible configurations and a deterministic shield prevents any downgrade.'
---

**Statut :** article accepté le 30 septembre 2026 à l'atelier WIAA'26 d'IEEE/WIC WI-IAT 2026. Version finale déposée ; actes IEEE à paraître.

## Résumé

Adaptive post-quantum TLS must select cryptographic groups under changing network, endpoint and workload conditions without letting performance adaptation weaken the required security posture. SmartPQ-Shield separates policy authority from performance optimization: a trusted local policy defines the safe action set of each session, a contextual bandit only ranks the permitted configurations, and a deterministic pre-execution shield dispatches a compliant choice or safely aborts. Across 1.224 million simulated sessions, all shielded modes execute zero sub-floor configurations, whereas unshielded learners violate the floor in more than 98% of sessions; 900 OpenSSL/OQS handshakes confirm that all supported actions are executable.
