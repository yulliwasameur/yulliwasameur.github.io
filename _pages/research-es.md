---
layout: single
title: "Yulliwas Ameur: privacidad, criptografía y seguridad de la IA"
permalink: /research/es/
lang: es
locale: es_ES
research_languages: true
author_profile: true
description: "Perfil de Yulliwas Ameur y cinco líneas de investigación en privacidad, criptografía y seguridad de agentes de IA, con publicaciones y código."
---

Soy docente e investigador en ciberseguridad en EFREI Paris, Francia. Estudio cómo proteger los datos y controlar las acciones de los sistemas de aprendizaje automático y de los agentes de IA. Esta selección presenta cinco contribuciones, sus resultados y sus límites.

[English](/research-highlights/) · [Español](/research/es/) · [Português do Brasil](/research/pt-br/) · [简体中文](/research/zh-hans/)

[Todas las publicaciones](/publications/) · [Bibliografía BibTeX](/files/publications.bib) · [Código](/code/) · [ORCID](https://orcid.org/0000-0003-1435-2982) · [Contacto](mailto:yulliwas.ameur@efrei.fr)

## 1. Agrupamiento sobre datos cifrados

*Secure k-means Clustering using Homomorphic Encryption*

El protocolo utiliza comparaciones con TFHE para asignar registros a grupos sin descifrar los datos en el servidor. En cada iteración, el cliente descifra los vectores de asignación y actualiza los centroides. La calidad del agrupamiento se mantiene próxima a la de k-means de Forgy en texto claro para cantidades moderadas de grupos. El coste del servidor está dominado por el refresco de los cifrados (*bootstrapping*).

Publicado en *Procedia Computer Science* 280 (2026), 576–583. [Ficha y resumen](/publication/2026-04-16-ant2026-secure-kmeans) · [DOI del artículo](https://doi.org/10.1016/j.procs.2026.04.073).

## 2. Cifrado homomórfico y privacidad diferencial

*Developing Adaptive Homomorphic Encryption through Exploration of Differential Privacy*

Este trabajo combina ambas técnicas en un modelo cliente–servidor y estudia cómo los parámetros de privacidad y ruido afectan a la precisión, el coste de cálculo y la privacidad. Los resultados son exploratorios; cada aplicación requiere su propia evaluación de utilidad y de las garantías de privacidad.

Publicado en *Journal of Cyber Security and Mobility* 13(5) (2024), 863–886. [Ficha y resumen](/publication/2024-07-01-jcsm-adaptive-he-dp) · [DOI del artículo](https://doi.org/10.13052/jcsm2245-1439.1353).

## 3. GovSecLLM++: pruebas de seguridad y evidencias de gobernanza

*GovSecLLM++: A Compliance-Aware Benchmark for Security Testing and Governance Evidence in LLM-Based Applications*

El paquete reúne herramientas de puntuación, resultados de reevaluación y pruebas adaptativas, resúmenes de validación humana y una ficha de datos. Emplea secretos y credenciales sintéticos. El software y el conjunto de datos tienen sus propios autores e identificadores. El paquete de código no incluye el PDF final del artículo y el DOI de las actas de SecAI, ESORICS 2026, todavía no está verificado.

[Ficha del artículo](/publication/2026-09-18-govsecllm-paper/) · [Código](https://github.com/yulliwasameur/GovSecLLMpp-SECAI2026) · [DOI general del software](https://doi.org/10.5281/zenodo.20636767) · [DOI de la versión del conjunto de datos](https://doi.org/10.5281/zenodo.20646702).

## 4. PQTrust-Agent: acuerdos entre políticas criptográficas

*PQTrust-Agent: Policy-Compiled Post-Quantum Trust Contracts for Web-of-Agents Communications*

Cada agente calcula las opciones compatibles con sus restricciones. Un contrato firmado por ambos extremos registra el acuerdo; si no existe una opción común, la operación se interrumpe antes de ejecutar la tarea. La evaluación reúne 1.040 observaciones en una sola máquina. La autenticación TLS sigue utilizando X.509 clásico y la mayoría de los casos factibles ofrece una única opción en la frontera común, lo que limita las conclusiones sobre la ventaja de la selección minimax. Estos resultados no demuestran el rendimiento a escala de Internet ni una autenticación de los extremos totalmente poscuántica.

Aceptado en WI-IAT 2026; actas pendientes de publicación. [Artículo y resumen](/publication/2026-09-18-pqtrust-agent/) · [Manuscrito de los autores](/publication/2026-09-18-pqtrust-agent/paper.pdf) · [Repositorio de código](https://github.com/Insaf19/PQtrust-agent-artifact).

## 5. AgentFlowShield: protección de los metadatos del tráfico

*AgentFlowShield: Defending LLM Agents Against Metadata Side Channels*

El sistema adapta el tráfico de un agente a sus fases de ejecución mediante relleno, agrupación de tramas, variaciones temporales acotadas y envolventes para la actividad de herramientas y memoria. La evaluación comprende 6.300 trazas controladas. Los resultados dependen del ataque y de la partición de los datos; persisten señales informativas. El banco de pruebas utiliza tráfico de bucle local y ruido WAN sintético, por lo que no demuestra la eliminación de fugas en redes de producción.

Aceptado en AICCSA 2026; actas pendientes de publicación. [Artículo y resumen](/publication/2026-09-18-agentflowshield/) · [Manuscrito de los autores](/publication/2026-09-18-agentflowshield/paper.pdf) · [Presentación](/publication/2026-09-18-agentflowshield/slides.pptx).

## Otros paquetes de software disponibles

- **ErrorCaps**, versión v3.0.1: benchmark sintético de inyección indirecta de instrucciones durante la recuperación de errores de agentes. Título del archivo: *ErrorCaps: committed-effect measurement of recovery-path injection defense (CRiSIS 2026 artifact)*. Publicado en Zenodo con licencia MIT. La etiqueta CRiSIS 2026 no acredita la aceptación del manuscrito. [Descripción](/publication/2026-08-28-software-errorcaps/) · [DOI de esta versión](https://doi.org/10.5281/zenodo.22147247).
- **Bearer, Bound, Attested**, versión v1.1: materiales experimentales y de análisis formal sobre vinculación de claves, procedencia y atestación en Zero Trust. Título del archivo: *Bearer, Bound, Attested: Factoring Key Binding, Provenance, and Attestation for Zero-Trust Enforcement (reproducible artefact)*. Publicado en Zenodo con licencia MIT; el artículo asociado figura como enviado a *IEEE Networking Letters*. [Descripción](/publication/bearer-bound-attested-software/) · [DOI de esta versión](https://doi.org/10.5281/zenodo.22146879).

Los títulos originales en inglés permiten localizar y citar los trabajos. Para utilizar software o datos, cite la versión concreta empleada. Las fichas enlazadas contienen las listas completas de autores y los materiales disponibles.
