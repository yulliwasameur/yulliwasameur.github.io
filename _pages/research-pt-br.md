---
layout: single
title: "Yulliwas Ameur: privacidade, criptografia e segurança da IA"
permalink: /research/pt-br/
lang: pt-BR
locale: pt_BR
research_languages: true
author_profile: true
description: "Perfil de Yulliwas Ameur e cinco linhas de pesquisa em privacidade, criptografia e segurança de agentes de IA, com publicações e código."
---

Sou professor e pesquisador em cibersegurança na EFREI Paris, França. Pesquiso como proteger dados e controlar as ações de sistemas de aprendizado de máquina e agentes de IA. Esta seleção apresenta cinco contribuições, seus resultados e suas limitações.

[English](/research-highlights/) · [Español](/research/es/) · [Português do Brasil](/research/pt-br/) · [简体中文](/research/zh-hans/)

[Todas as publicações](/publications/) · [Bibliografia BibTeX](/files/publications.bib) · [Código](/code/) · [ORCID](https://orcid.org/0000-0003-1435-2982) · [Contato](mailto:yulliwas.ameur@efrei.fr)

## 1. Agrupamento de dados criptografados

*Secure k-means Clustering using Homomorphic Encryption*

O protocolo usa comparações com TFHE para atribuir registros a grupos sem descriptografar os dados no servidor. A cada iteração, o cliente descriptografa os vetores de atribuição e atualiza os centroides. A qualidade do agrupamento permanece próxima à do k-means de Forgy sobre dados em claro para quantidades moderadas de grupos. O custo do servidor é dominado pelo procedimento de renovação dos textos cifrados (*bootstrapping*).

Publicado em *Procedia Computer Science* 280 (2026), 576–583. [Registro e resumo](/publication/2026-04-16-ant2026-secure-kmeans) · [DOI do artigo](https://doi.org/10.1016/j.procs.2026.04.073).

## 2. Criptografia homomórfica e privacidade diferencial

*Developing Adaptive Homomorphic Encryption through Exploration of Differential Privacy*

O trabalho combina essas duas técnicas em um modelo cliente–servidor e estuda como os parâmetros de privacidade e ruído afetam a acurácia, o custo computacional e a privacidade. Os resultados são exploratórios; cada aplicação exige sua própria avaliação de utilidade e das garantias de privacidade.

Publicado em *Journal of Cyber Security and Mobility* 13(5) (2024), 863–886. [Registro e resumo](/publication/2024-07-01-jcsm-adaptive-he-dp) · [DOI do artigo](https://doi.org/10.13052/jcsm2245-1439.1353).

## 3. GovSecLLM++: testes de segurança e evidências de governança

*GovSecLLM++: A Compliance-Aware Benchmark for Security Testing and Governance Evidence in LLM-Based Applications*

O pacote reúne ferramentas de pontuação, resultados de reavaliação e de testes adaptativos, resumos de validação humana e uma ficha de dados. Utiliza segredos e credenciais sintéticos. O software e o conjunto de dados têm seus próprios autores e identificadores. O pacote de código não inclui o PDF final do artigo, e o DOI dos anais do SecAI, ESORICS 2026, ainda não foi verificado.

[Registro do artigo](/publication/2026-09-18-govsecllm-paper/) · [Código](https://github.com/yulliwasameur/GovSecLLMpp-SECAI2026) · [DOI geral do software](https://doi.org/10.5281/zenodo.20636767) · [DOI da versão do conjunto de dados](https://doi.org/10.5281/zenodo.20646702).

## 4. PQTrust-Agent: acordos entre políticas criptográficas

*PQTrust-Agent: Policy-Compiled Post-Quantum Trust Contracts for Web-of-Agents Communications*

Cada agente calcula as opções compatíveis com suas restrições. Um contrato assinado pelos dois participantes registra o acordo; quando não há uma opção comum, a operação é interrompida antes da execução da tarefa. A avaliação reúne 1.040 observações em uma única máquina. A autenticação TLS continua usando X.509 clássico, e a maioria dos casos viáveis apresenta apenas uma opção na fronteira comum, o que limita as conclusões sobre a vantagem da seleção minimax. Esses resultados não demonstram o desempenho em escala de Internet nem uma autenticação dos endpoints inteiramente pós-quântica.

Aceito no WI-IAT 2026; anais ainda não publicados. [Artigo e resumo](/publication/2026-09-18-pqtrust-agent/) · [Manuscrito dos autores](/publication/2026-09-18-pqtrust-agent/paper.pdf) · [Repositório de código](https://github.com/Insaf19/PQtrust-agent-artifact).

## 5. AgentFlowShield: proteção dos metadados de tráfego

*AgentFlowShield: Defending LLM Agents Against Metadata Side Channels*

O sistema adapta o tráfego do agente às fases de execução com preenchimento, agregação de quadros, variações temporais limitadas e envelopes para atividades de ferramentas e memória. A avaliação compreende 6.300 traços de tráfego controlados. Os resultados dependem do ataque e da divisão dos dados; sinais informativos permanecem. O ambiente de testes usa tráfego de loopback e ruído WAN sintético, por isso não demonstra a eliminação de vazamentos em redes de produção.

Aceito no AICCSA 2026; anais ainda não publicados. [Artigo e resumo](/publication/2026-09-18-agentflowshield/) · [Manuscrito dos autores](/publication/2026-09-18-agentflowshield/paper.pdf) · [Apresentação](/publication/2026-09-18-agentflowshield/slides.pptx).

## Outros pacotes de software disponíveis

- **ErrorCaps**, versão v3.0.1: benchmark sintético de injeção indireta de instruções durante a recuperação de erros de agentes. Título do arquivo: *ErrorCaps: committed-effect measurement of recovery-path injection defense (CRiSIS 2026 artifact)*. Publicado no Zenodo sob a licença MIT. A identificação CRiSIS 2026 não comprova a aceitação do manuscrito. [Descrição](/publication/2026-08-28-software-errorcaps/) · [DOI desta versão](https://doi.org/10.5281/zenodo.22147247).
- **Bearer, Bound, Attested**, versão v1.1: materiais experimentais e de análise formal sobre vinculação de chaves, proveniência e atestação em Zero Trust. Título do arquivo: *Bearer, Bound, Attested: Factoring Key Binding, Provenance, and Attestation for Zero-Trust Enforcement (reproducible artefact)*. Publicado no Zenodo sob a licença MIT; o artigo associado é descrito como uma submissão ao *IEEE Networking Letters*. [Descrição](/publication/bearer-bound-attested-software/) · [DOI desta versão](https://doi.org/10.5281/zenodo.22146879).

Os títulos originais em inglês permitem localizar e citar os trabalhos. Ao utilizar software ou dados, cite a versão específica utilizada. Os registros vinculados apresentam as listas completas de autores e os materiais disponíveis.
