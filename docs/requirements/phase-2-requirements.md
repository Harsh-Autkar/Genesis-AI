# Genesis-AI — Phase 2 Requirements & Evaluation Framework

## Document Status

- Project: Genesis-AI Research Intelligence Platform
- Blueprint Phase: 2 — Requirements & Evaluation Framework
- Status: Prepared for sign-off
- Source of truth: `docs/phase-0-blueprint.pdf`
- Previous implementation milestone:
  - Frontend foundation completed
  - FastAPI API foundation completed
- Architecture changes: None approved at this stage

---

# 1. Purpose

This document converts the Phase 0 Blueprint into concrete functional,
non-functional, evaluation, security, responsible-AI, deployment, and
acceptance requirements.

The system remains an evidence-grounded research decision-support platform.
It does not claim to determine scientific truth, absolute novelty,
publication acceptance, plagiarism, or research validity.

---

# 2. Product Definition

Genesis-AI analyzes research papers against retrieved scholarly evidence.

Core transformation:

Research Paper
→ Document Processing
→ Research Information Extraction
→ Scholarly Retrieval
→ Evidence Retrieval
→ Claim/Citation Verification
→ Novelty & Research-Gap Analysis
→ Quality Evaluation
→ Recommendations
→ User Action

Every important assessment must be traceable to evidence, reasoning,
sources, confidence, and limitations.

---

# 3. Target Users

## 3.1 Researchers

Researchers who want structured evidence-based self-review.

## 3.2 Students

Undergraduate and graduate students learning how existing research relates
to their own work.

## 3.3 Reviewers

Users who want a structured first-pass assessment to support, not replace,
human review.

---

# 4. Core Functional Requirements

## FR-001 Paper Upload

The system shall allow a user to upload a research paper in a supported
PDF format.

## FR-002 File Validation

The system shall validate file type and size before processing.

## FR-003 File Security

The system shall provide malware/security scanning before accepting a file
for processing.

## FR-004 Paper Storage

The system shall store an accepted paper using a reference that can be
associated with the user and research project.

## FR-005 Document Parsing

The system shall extract text and layout information from supported PDFs.

## FR-006 OCR Fallback

The system shall provide an OCR fallback for scanned/image-only documents
and identify lower-confidence extraction.

## FR-007 Structure Detection

The system shall identify research-paper structure including title,
abstract, sections, methods, results, and references where possible.

## FR-008 Research Information Extraction

The system shall extract structured research information including:

- claims
- methods
- datasets
- experiments
- results
- references

## FR-009 Embedding Generation

The system shall generate embeddings for appropriate text units used for
semantic comparison and retrieval.

## FR-010 Scholarly Retrieval

The system shall retrieve related scholarly literature from supported
scholarly sources.

Initial candidate providers include:

- OpenAlex
- Semantic Scholar
- Crossref
- arXiv

Provider usage must respect access terms, rate limits, and licensing.

## FR-011 Evidence Retrieval

The system shall retrieve relevant evidence passages from available
candidate literature.

## FR-012 Claim Verification

The system shall compare extracted claims with retrieved evidence.

Verification shall use:

- supported
- contradicted
- insufficient-evidence

rather than presenting verification as absolute scientific truth.

## FR-013 Citation Analysis

The system shall assess citation relevance using citation context and
available information about the cited work.

## FR-014 Literature Comparison

The system shall compare the analyzed paper with relevant retrieved
literature.

## FR-015 Novelty Estimation

The system shall estimate relative novelty against retrieved prior work.

The result shall explicitly communicate that the assessment is bounded by
the retrieved literature.

## FR-016 Research-Gap Analysis

The system shall identify candidate under-covered areas in retrieved
literature.

Research gaps shall be presented as candidates requiring researcher
evaluation.

## FR-017 Quality Evaluation

The system shall produce structured assessments across the defined
evaluation dimensions.

## FR-018 Recommendations

The system shall convert identified weaknesses into specific,
evidence-grounded recommendations.

## FR-019 Evidence Traceability

Each important generated assessment shall expose:

- evidence
- reasoning
- sources
- confidence
- limitations

## FR-020 Analysis Report

The system shall provide a structured report containing the analysis
results and supporting evidence.

---

# 5. Research Discovery Extension

The following capabilities are approved as product-direction extensions
and must not override the defined MVP sequence without deliberate scope
approval.

## RD-001 Research Discovery

Users should eventually be able to discover recent and relevant research
for a topic.

## RD-002 Research Landscape

The system should organize retrieved literature by topic, method,
findings, limitations, and related research.

## RD-003 Research Evolution

The system may represent how research around a topic evolves over time.

## RD-004 Research Gap Exploration

Users should be able to inspect evidence associated with candidate gaps.

## RD-005 Research Positioning

Users should eventually be able to compare a proposed research direction
against retrieved prior work.

## RD-006 Research Workspace

Users should eventually be able to maintain a research project containing
literature, notes, papers, findings, gaps, and analysis history.

## RD-007 Research Improvement Loop

Users should eventually be able to analyze successive versions of their
paper and track improvements.

These extensions require architectural support but are not permitted to
cause uncontrolled MVP scope expansion.

---

# 6. Evaluation Framework

The initial evaluation framework contains the following dimensions.

## 6.1 Problem Formulation

Measures whether the research problem is clearly stated and motivated.

Potential signals:

- problem statement presence
- motivation completeness
- research-question clarity
- alignment between problem and proposed contribution

## 6.2 Novelty

Measures relative differentiation from retrieved prior work.

Potential signals:

- semantic similarity to nearest prior work
- contribution overlap
- methodological overlap
- dataset overlap
- retrieved prior-art coverage

Novelty is a relative estimate, not an absolute determination.

## 6.3 Literature Quality

Measures whether related-work coverage appears reasonably relevant,
current, and comprehensive.

Potential signals:

- relevant retrieved literature
- coverage of important related approaches
- recency
- citation/reference coverage

## 6.4 Methodology

Measures whether the methodology is sufficiently described and appropriate
for the stated problem.

Potential signals:

- method description completeness
- alignment between method and problem
- methodological detail
- comparison with related approaches

## 6.5 Experimental Rigor

Measures experimental design quality.

Potential signals:

- baselines
- comparisons
- ablations
- experimental controls
- evaluation design

## 6.6 Results Quality

Measures whether results are clearly reported and appropriately
contextualized.

Potential signals:

- metric reporting
- baseline comparison
- result completeness
- contextual explanation
- possible cherry-picking signals

## 6.7 Citation Integrity

Measures whether citations are relevant to the claims or statements they
support.

Potential signals:

- citation-context similarity
- cited-paper relevance
- citation coverage
- unsupported citation-context flags

## 6.8 Reproducibility

Measures reproducibility signals visible in the paper.

Potential signals:

- code availability
- dataset availability
- hyperparameters
- experimental configuration
- preprocessing details
- implementation details

## 6.9 Writing Clarity

Measures structural and linguistic clarity.

Potential signals:

- section organization
- clarity of extracted research information
- consistency
- readability indicators

This dimension must not become a subjective literary-quality judgment.

## 6.10 Research Impact

Provides an estimated impact signal based on retrieved context.

This must remain explicitly estimated and evidence-grounded.

---

# 7. Score Contract

No important score may be presented as an unexplained number.

Every dimension assessment must expose:

1. Score
2. Evidence
3. Reasoning
4. Sources
5. Confidence
6. Limitations

The scoring framework shall initially use measurable upstream signals and
rule-based aggregation.

LLMs may explain or reason over signals but shall not independently invent
the final score.

---

# 8. Confidence Requirements

Confidence shall reflect available evidence quality and agreement.

Confidence must decrease when:

- evidence is sparse
- retrieval is weak
- extraction confidence is low
- sources disagree
- full text is unavailable
- the assessment relies on incomplete information

Confidence must not be interpreted as probability of scientific truth.

---

# 9. Non-Functional Requirements

## NFR-001 Reliability

The system shall fail gracefully when individual pipeline stages fail.

## NFR-002 Explainability

Important outputs shall be traceable to evidence and reasoning.

## NFR-003 Reproducibility

Analysis configurations, model versions, prompts where relevant, and
retrieval information should be recordable.

## NFR-004 Performance

Fast validation operations should remain synchronous.

Long-running document processing and external retrieval operations shall
support asynchronous execution.

## NFR-005 Scalability

The architecture shall permit later scaling without requiring premature
microservice decomposition.

## NFR-006 Maintainability

Business logic shall remain modular and separated by responsibility.

## NFR-007 Testability

Core services and API contracts shall be independently testable.

## NFR-008 Observability

The system shall support structured logging, health monitoring, and later
evaluation reporting.

## NFR-009 Availability

External scholarly or LLM provider failures shall not crash the entire
application.

## NFR-010 Graceful Degradation

The system shall communicate when analysis is limited by unavailable
full text, retrieval failure, extraction failure, or provider failure.

---

# 10. Security and Privacy Requirements

## SEC-001 Authentication

User accounts shall be protected by authentication.

## SEC-002 Authorization

Users shall only access resources they are authorized to access.

## SEC-003 Private Papers

Uploaded user papers shall be treated as private user data.

## SEC-004 Training Restriction

User-uploaded papers shall not be used to train shared models without
explicit user consent.

## SEC-005 Secrets

API credentials and secrets shall not be stored in source control.

## SEC-006 File Validation

Uploaded files shall undergo type, size, and security validation.

## SEC-007 External Content Licensing

External scholarly content shall be used according to applicable access
and licensing terms.

---

# 11. Responsible AI Requirements

## RAI-001

The system shall identify itself as research decision support.

## RAI-002

The system shall not claim definitive scientific truth.

## RAI-003

Novelty shall be presented as a relative estimate bounded by retrieved
literature.

## RAI-004

Claim verification shall use supported, contradicted, or
insufficient-evidence labels.

## RAI-005

The system shall expose uncertainty and limitations.

## RAI-006

The system shall avoid unsupported claims in generated explanations.

## RAI-007

The system shall preserve evidence provenance for generated assessments.

---

# 12. Deployment Requirements

The application shall be designed for eventual deployment.

The deployment architecture shall support:

- Next.js frontend
- FastAPI backend
- persistent database
- object/file storage
- asynchronous processing
- external scholarly APIs
- environment-based configuration
- logging and monitoring

The MVP shall avoid premature infrastructure including:

- Kubernetes
- microservice-per-feature deployment
- dedicated vector database
- custom foundation-model training
- unnecessary multi-database architecture

---

# 13. Data Requirements

Development data may consist of a small manually collected set of
appropriate sample papers.

External scholarly metadata may be retrieved from supported providers at
query time.

Training datasets shall only be used when licensing permits.

Evaluation data shall eventually contain a curated benchmark suitable for
human comparison.

All external data usage shall record source and licensing information
where required.

---

# 14. Evaluation Requirements

The system shall eventually be evaluated against human judgment.

Evaluation shall include:

- retrieval relevance
- information extraction correctness
- citation verification quality
- scoring behavior
- explanation grounding
- hallucination behavior

The system shall not be treated as its own ground truth.

A later benchmark shall compare system outputs with knowledgeable human
reviewers.

---

# 15. Research Questions

The project shall investigate:

### RQ1
How effectively can evidence-grounded AI evaluate research-paper quality
compared with human reviewers?

### RQ2
How accurately can retrieval-based systems identify potentially
unsupported scientific claims?

### RQ3
How effectively can semantic literature comparison identify potential
research gaps?

These questions require benchmark data, human evaluation, agreement
metrics, and documented error analysis before research claims are made.

---

# 16. MVP Boundary

The MVP shall prioritize the blueprint pipeline through the recommendation
stage:

Document Processing
→ Research Information Extraction
→ Scholarly Retrieval
→ Claim Verification
→ Novelty/Gap Analysis
→ Quality Scoring
→ Recommendations

The following remain later-stage capabilities unless explicitly promoted
through a documented decision:

- knowledge graph
- AI peer-review simulation
- multimodal figure/equation understanding
- distributed infrastructure beyond the planned scalability path
- advanced model training/fine-tuning

---

# 17. Acceptance Criteria

Phase 2 requirements are accepted when:

- [ ] Functional requirements are documented
- [ ] Non-functional requirements are documented
- [ ] Evaluation dimensions are defined
- [ ] Score evidence requirements are defined
- [ ] Confidence requirements are defined
- [ ] Security requirements are defined
- [ ] Responsible-AI requirements are defined
- [ ] Deployment requirements are defined
- [ ] Data/licensing requirements are defined
- [ ] MVP boundaries are explicit
- [ ] Research questions are documented
- [ ] Research Discovery extension is documented without uncontrolled
      scope expansion
- [ ] Requirements document is reviewed and signed off

---

# 18. Phase 2 Sign-Off

Status: PENDING PROJECT OWNER APPROVAL

Project Owner: ____________________

Date: ____________________

Approval:

[ ] Approved

[ ] Changes requested

---

# 19. Blueprint Consistency

This document remains subordinate to
`docs/phase-0-blueprint.pdf`.

Any deliberate deviation from the blueprint must be documented through
an Architecture Decision Record.

No numerical performance target is invented before benchmark evidence
exists.