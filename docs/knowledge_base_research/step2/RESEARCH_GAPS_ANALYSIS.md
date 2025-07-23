# Research Gaps and Implementation-Focused Analysis

## 1. Introduction

This document synthesizes the findings from the initial research phase and identifies explicit "TODOs" and implicit research gaps that require more detailed, implementation-focused investigation. The goal is to translate the high-level architectural proposals into a set of actionable research questions and engineering tasks for the next phase of development.

The identified gaps are grouped into four key areas:
1.  **Schema & Ontology Implementation Details**
2.  **Ingestion Pipeline & AI Model-Specifics**
3.  **Human-in-the-Loop (HITL) System Design**
4.  **Governance & Operationalization**

---

## 2. Schema & Ontology Implementation Details

The research proposes a sophisticated, multi-layered ontology. However, the practical implementation details need to be specified.

### Explicit TODOs & Implicit Gaps:

*   **`VulnerabilityPattern` Node Attributes:** The `VulnerabilityPattern` node is central to the zero-day lifecycle model, but its specific attributes are undefined.
    *   **Research Question:** What specific properties should a `VulnerabilityPattern` node have? (e.g., `CWE-ID`, `CommonConsequences`, `MitigationPatterns`, `CodeSnippets`).
*   **Upper Ontology Selection:** The documents suggest the **Unified Cyber Ontology (UCO)** as a starting point for the Upper Ontology. A formal decision and potential customization plan are needed.
    *   **Research Question:** Is UCO the definitive choice? If so, which specific version should be adopted, and what extensions or modifications are necessary for our use case?
*   **Temporal Modeling Implementation:** The research mentions "Event Sourcing" as a complex pattern for temporal modeling but does not detail its implementation.
    *   **Research Question:** What is the precise data model and query strategy for the Event Sourcing pattern? How will graph projections at a specific point in time be handled efficiently?
*   **`Evidence` Node vs. Relationship Properties:** The documents propose a dual pattern for modeling confidence and evidence. Clear guidelines are needed for when to use the more complex `Evidence` node.
    *   **Research Question:** What is the definitive decision framework for choosing between properties on relationships and the full `Evidence` node reification pattern?

---

## 3. Ingestion Pipeline & AI Model-Specifics

The ingestion pipeline relies heavily on AI/ML models, but the specifics of their implementation, fine-tuning, and prompting are not yet detailed.

### Explicit TODOs & Implicit Gaps:

*   **LLM Prompt Engineering:** The "Few-Shot, Chain-of-Thought" prompt for relationship extraction is mentioned but not defined.
    *   **Research Question:** What are the exact, version-controlled prompts and few-shot examples that will be used for the relationship and attribute extraction tasks?
*   **LLM Fine-Tuning Strategy:** The documents mention using fine-tuned models but do not specify the strategy.
    *   **Research Question:** What is the detailed strategy for fine-tuning our LLMs? What datasets will be used? What is the feedback loop from the HITL system to the fine-tuning process?
*   **Tree-sitter Implementation:** The use of `tree-sitter` for structural parsing is proposed, but the specifics of how the Concrete Syntax Tree (CST) is traversed and converted into features are missing.
    *   **Research Question:** What is the specific algorithm or set of heuristics for traversing the CST and extracting structured features for graph ingestion?
*   **Embedding Model Selection:** The use of vector embeddings for entity linking is mentioned, but the specific models and validation strategy are not defined.
    *   **Research Question:** Which specific embedding models will be used for code and text? How will the quality of the embeddings be benchmarked and validated?

---

## 4. Human-in-the-Loop (HITL) System Design

The HITL system is a critical component for ensuring data quality, but its user interface and workflow are not designed.

### Explicit TODOs & Implicit Gaps:

*   **Validation UI/UX:** The "simple web-based interface" for analysts needs to be designed.
    *   **Research Question:** What is the detailed UI design and workflow for the HITL validation queue? How will analysts efficiently review, approve, reject, and correct assertions?
*   **Feedback Loop Mechanism:** The mechanism for feeding validated data back into the model fine-tuning process is not specified.
    *   **Research Question:** What is the technical architecture of the feedback loop? How is validated data collected, stored, and used to trigger retraining or fine-tuning jobs?

---

## 5. Governance & Operationalization

The research mentions the need for governance but does not detail the operational processes.

### Explicit TODOs & Implicit Gaps:

*   **Ontology Working Group (OWG) Charter:** The OWG is proposed but needs a formal charter.
    *   **Research Question:** What is the formal charter for the OWG, including its members, meeting cadence, and the process for proposing and approving changes to domain ontologies?
*   **Federation Decision Framework:** The hybrid federation model requires a decision framework that is not yet created.
    *   **Research Question:** What is the specific, quantitative decision framework for determining whether a data source should be materialized or virtualized?
*   **Data Quality Monitoring:** The need for automated data quality monitoring is stated, but the specific metrics and tools are not defined.
    *   **Research Question:** What are the specific data quality metrics to be monitored (e.g., staleness, completeness, consistency)? What tools will be used to implement this monitoring?