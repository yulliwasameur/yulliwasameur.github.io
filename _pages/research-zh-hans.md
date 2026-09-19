---
layout: single
title: "Yulliwas Ameur：隐私保护、密码学与人工智能安全"
permalink: /research/zh-hans/
lang: zh-Hans
locale: zh_CN
research_languages: true
author_profile: true
description: "Yulliwas Ameur 的研究简介：隐私保护、密码学和人工智能智能体安全领域的五项研究，以及论文、代码和研究资源。"
---

我是法国 EFREI Paris 的网络安全教师与研究人员，研究如何保护数据，以及如何控制机器学习系统和人工智能智能体的行为。本页介绍五项研究的贡献、证据及适用范围。

[English](/research-highlights/) · [Español](/research/es/) · [Português do Brasil](/research/pt-br/) · [简体中文](/research/zh-hans/)

[全部研究成果](/publications/) · [BibTeX 参考文献](/files/publications.bib) · [代码](/code/) · [ORCID](https://orcid.org/0000-0003-1435-2982) · [联系我](mailto:yulliwas.ameur@efrei.fr)

## 1. 对加密数据进行聚类

*Secure k-means Clustering using Homomorphic Encryption*

该协议利用 TFHE 比较运算，将记录分配到不同的簇，服务器无需解密数据。客户端在每次迭代中解密分配向量，并更新聚类中心。当簇的数量适中时，其聚类质量接近明文数据上的 Forgy k-means。服务器的主要计算开销来自密文自举（bootstrapping）。

发表于 *Procedia Computer Science* 第 280 卷（2026），第 576–583 页。[论文信息与摘要](/publication/2026-04-16-ant2026-secure-kmeans) · [论文 DOI](https://doi.org/10.1016/j.procs.2026.04.073)。

## 2. 结合同态加密与差分隐私

*Developing Adaptive Homomorphic Encryption through Exploration of Differential Privacy*

该研究在客户端—服务器模型中结合两种机制，分析隐私和噪声参数如何影响分类准确率、计算开销与隐私保护。结果属于探索性研究；具体应用仍需单独评估数据效用和隐私保证。

发表于 *Journal of Cyber Security and Mobility* 第 13 卷第 5 期（2024），第 863–886 页。[论文信息与摘要](/publication/2024-07-01-jcsm-adaptive-he-dp) · [论文 DOI](https://doi.org/10.13052/jcsm2245-1439.1353)。

## 3. GovSecLLM++：安全测试与治理证据

*GovSecLLM++: A Compliance-Aware Benchmark for Security Testing and Governance Evidence in LLM-Based Applications*

研究资源包含评分工具、重新评分结果、自适应测试结果、人工验证摘要和数据说明文档，使用合成的秘密信息与凭据。软件和数据集各有独立的作者列表与标识符。目前的代码包不包含论文最终版 PDF，SecAI、ESORICS 2026 相关会议论文集的 DOI 尚未核实。

[论文信息](/publication/2026-09-18-govsecllm-paper/) · [代码](https://github.com/yulliwasameur/GovSecLLMpp-SECAI2026) · [软件总记录 DOI](https://doi.org/10.5281/zenodo.20636767) · [数据集特定版本 DOI](https://doi.org/10.5281/zenodo.20646702)。

## 4. PQTrust-Agent：协调智能体的密码策略

*PQTrust-Agent: Policy-Compiled Post-Quantum Trust Contracts for Web-of-Agents Communications*

每个智能体先计算符合自身约束的可选方案，再通过双方签名的任务合约记录协议结果。如果不存在共同方案，系统会在执行任务前终止操作。评估包含在单台机器上进行的 1,040 次观测。TLS 端点认证仍采用经典 X.509；大多数可行场景的共同前沿只有一个候选方案，因此对 minimax 选择策略优势的结论仍有限。这些结果并未证明其在互联网规模下的性能，也未证明端点认证已完全实现后量子安全。

已被 WI-IAT 2026 接收，会议论文集尚未发表。[论文与摘要](/publication/2026-09-18-pqtrust-agent/) · [作者稿 PDF](/publication/2026-09-18-pqtrust-agent/paper.pdf) · [代码仓库](https://github.com/Insaf19/PQtrust-agent-artifact)。

## 5. AgentFlowShield：减少流量元数据泄露

*AgentFlowShield: Defending LLM Agents Against Metadata Side Channels*

该系统根据智能体的执行阶段调整流量，采用填充、帧聚合、有界时间抖动，以及针对工具和内存活动的流量包络。评估使用了 6,300 条受控流量轨迹。结果取决于攻击方式和数据划分，部分信息信号仍然存在。测试环境采用本地回环流量和合成的广域网噪声，因此这些结果不能证明实际生产网络中的元数据泄露已被消除。

已被 AICCSA 2026 接收，会议论文集尚未发表。[论文与摘要](/publication/2026-09-18-agentflowshield/) · [作者稿 PDF](/publication/2026-09-18-agentflowshield/paper.pdf) · [演示文稿](/publication/2026-09-18-agentflowshield/slides.pptx)。

## 其他已公开的软件资源

- **ErrorCaps**，版本 v3.0.1：用于研究智能体错误恢复过程中的间接提示注入的合成基准。归档标题为 *ErrorCaps: committed-effect measurement of recovery-path injection defense (CRiSIS 2026 artifact)*。软件已在 Zenodo 发布，采用 MIT 许可证；标题中的 CRiSIS 2026 标签不代表相关论文已被接收。[资源说明](/publication/2026-08-28-software-errorcaps/) · [该版本 DOI](https://doi.org/10.5281/zenodo.22147247)。
- **Bearer, Bound, Attested**，版本 v1.1：关于零信任中的密钥绑定、来源与证明机制的实验和形式化分析资源。归档标题为 *Bearer, Bound, Attested: Factoring Key Binding, Provenance, and Attestation for Zero-Trust Enforcement (reproducible artefact)*。软件已在 Zenodo 发布，采用 MIT 许可证；归档将相关论文描述为向 *IEEE Networking Letters* 提交的稿件。[资源说明](/publication/bearer-bound-attested-software/) · [该版本 DOI](https://doi.org/10.5281/zenodo.22146879)。

本页保留论文和软件的英文原始标题，便于检索与引用。使用软件或数据时，请引用实际使用的具体版本。完整作者列表和可获取的材料见各项成果的链接页面。
