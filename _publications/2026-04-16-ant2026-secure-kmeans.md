---
title: Secure k-means Clustering using Homomorphic Encryption
collection: publications
output_type: peer-reviewed
permalink: /publication/2026-04-16-ant2026-secure-kmeans
excerpt: Privacy-preserving k-means clustering on homomorphically encrypted data using TFHE.
date: 2026-04-16
venue: ANT / EDI40 2026 - Procedia Computer Science, vol. 280
paperurl: https://doi.org/10.1016/j.procs.2026.04.073
citation: 'Rezak Aziz, Yulliwas Ameur, Vincent Audigier, Samia Bouzefrane. "Secure k-means Clustering using Homomorphic Encryption." Procedia Computer Science, vol. 280, 2026, pp. 576-583. DOI: 10.1016/j.procs.2026.04.073.'
authors:
- Rezak Aziz
- Yulliwas Ameur
- Vincent Audigier
- Samia Bouzefrane
doi: 10.1016/j.procs.2026.04.073
publication_year: 2026
bibtexurl: /files/publications.bib
---

## Abstract

Machine Learning as a Service (MLaaS) enables users to outsource compute-intensive analytics, but processing sensitive data in clear on a cloud server raises strong privacy concerns. Fully Homomorphic Encryption (FHE) enables computations over encrypted data, yet implementing k-means under FHE is challenging because the assignment step requires repeated comparisons (argmin), while centroid updates involve divisions. We propose a TFHE-based privacy-preserving k-means protocol that performs the entire assignment step homomorphically. For each iteration, the cloud evaluates encrypted comparisons of squared Euclidean distance differences using TFHE programmable bootstrapping, and returns encrypted one-hot assignment vectors. The client decrypts only these assignment vectors once per iteration to update centroids in clear and sends the refreshed centroids back. This design eliminates any server-side decryption and avoids trusted third parties while keeping client work lightweight. We evaluate on several real datasets using ARI/NMI (when labels exist) and internal metrics (inertia/silhouette). The encrypted clustering closely matches plaintext Forgy k-means for moderate numbers of clusters, while runtime is dominated by bootstrapping operations and thus benefits from parallelization.
