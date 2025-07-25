# Project TKG: Complete Blueprint

# Project TKG: State-of-the-Art & Gap Analysis Report

**Version:** 1.0
**Date:** 2025-07-24
**Status:** Final

## 1. Executive Summary

This report marks the conclusion of Phase 1 of Project TKG and serves as the foundational document for the subsequent design and implementation phases. It synthesizes the findings from two key research streams: an internal analysis of advanced graph architectures and an external state-of-the-art survey focused on implementing a MITRE ATT&CK-based knowledge graph.

A conflict was identified between the internal research, which concluded that a rigid, single-ontology model based solely on ATT&CK was a "concluded dead-end," and the project's mandate to implement such a model.

Per the project directive, this report confirms that Project TKG will proceed with a technique-centric ATT&CK model. The findings from the external "State-of-the-Art Survey Report," embodied in the `tkg_importer.py` script, are hereby declared the official foundation for the project's design and implementation. This document formally defines that foundation and identifies the remaining gaps to be addressed in Phase 2.

## 2. Acknowledging the Conflict

Two distinct and conflicting conclusions have emerged from our Phase 1 research:

*   **Internal Research Synthesis:** Our internal research into advanced graph architectures (`docs/knowledge_base_research/ADVANCED_GRAPH_ARCHITECTURES.md`) concluded that a flexible, multi-layered ontology (using UCO as an upper ontology) is the optimal approach for a scalable and extensible cybersecurity knowledge graph. This research explicitly identified the limitations of a single, rigid ontology like MITRE ATT&CK, deeming it a "concluded dead-end" for advanced use cases.

*   **External State-of-the-Art Survey:** A parallel research effort was conducted with the specific mandate to find the *best possible way* to implement a strictly ATT&CK-based graph. This research produced a "State-of-the-Art Survey Report" and a corresponding Python script, `src/ingestion/tkg_importer.py`, which represents the best practices for a technique-centric ATT&CK implementation.

## 3. Justification for the Path Forward

While the internal research presents a compelling case for a more advanced architecture, the project directive for Phase 1 is to deliver a knowledge graph based exclusively on the MITRE ATT&CK framework.

Therefore, the findings of the external state-of-the-art survey will be adopted as the definitive guide for this specific implementation. The `tkg_importer.py` script and its underlying schema are to be considered the authoritative foundation for Project TKG. This decision allows the project to move forward with a clear, well-defined, and defensible implementation that meets the immediate requirements, while acknowledging the potential for future evolution.

## 4. The Foundation for Project TKG

The official foundation for Project TKG's design is the schema and ETL patterns defined in the `src/ingestion/tkg_importer.py` script.

### 4.1. Core Principles

*   **Technique-Centric:** The model will exclusively import ATT&CK techniques, tactics, mitigations, and data sources, deliberately omitting threat actors, campaigns, and other entities.
*   **Detection-Focused:** The schema is designed to model the critical relationships between techniques and their detection mechanisms (data sources and components).

### 4.2. Graph Schema

The following graph schema is formally adopted for Project TKG:

```mermaid
graph TD
    subgraph ATT&CK Framework
        Tactic -- HAS_TECHNIQUE --> Technique
        Technique -- HAS_SUBTECHNIQUE --> SubTechnique
        Technique -- MITIGATED_BY --> Mitigation
        SubTechnique -- MITIGATED_BY --> Mitigation
        Technique -- DETECTED_BY --> DataComponent
        SubTechnique -- DETECTED_BY --> DataComponent
        DataSource -- HAS_COMPONENT --> DataComponent
    end

    classDef node fill:#f9f,stroke:#333,stroke-width:2px;
    class Tactic,Technique,SubTechnique,Mitigation,DataSource,DataComponent node;
```

### 4.3. ETL Pipeline

The ETL pipeline will be implemented as defined in `src/ingestion/tkg_importer.py`. Key features include:
*   Direct data fetching from the official MITRE CTI repository.
*   A two-phase, batched import process for nodes and relationships.
*   Defensive parsing and clear logging.

## 5. Identified Gaps

Based on the chosen path, the following gaps have been identified and must be addressed in the design and implementation phases (Phase 2 and 3):

1.  **Graph Database Operations:** With Neo4j confirmed as the graph database, the focus shifts to operationalizing it. A plan for managing the self-hosted Docker container is required, including data volume persistence, backup and recovery strategies, resource allocation (CPU/memory), and monitoring for production readiness.

2.  **Query Interface:** The project will adopt **`graphiti`** as the official query interface. This library provides a dual-access model for interacting with the knowledge graph: a programmatic, Pydantic-based interface for developers to execute raw Cypher, and a high-level, natural language interface for analysts. The implementation will involve wrapping `graphiti` in a simple API to expose these capabilities to other systems.

3.  **Data Updates and Synchronization:** The current script performs a full, destructive import. A strategy for incremental updates and synchronization with the MITRE ATT&CK framework is required for long-term maintenance.

4.  **Extensibility:** The chosen model is intentionally rigid. A plan for future extensibility, potentially incorporating the findings of the internal research (e.g., a multi-layered ontology), should be developed to guide the project's long-term evolution.

5.  **Technology Validation and Proof of Concept:** Before full implementation, a Proof of Concept (PoC) must be developed to validate `graphiti`'s ability to handle the complexity of the TKG schema and anticipated query patterns. This PoC will serve to de-risk the technology choice and inform the design of the final API wrapper.

## 6. Conclusion

This report provides a clear and decisive path forward for Project TKG. By adopting the technique-centric ATT&CK model defined by the external state-of-the-art survey, the project can proceed with a well-defined and defensible foundation. The identified gaps provide a clear roadmap for the work to be done in the upcoming design and implementation phases.

# Project TKG: Formal Graph Schema Specification

**Version:** 1.0
**Date:** 2025-07-24
**Status:** Final

## 1. Introduction

This document provides the formal specification for the Project TKG graph schema. It is the primary deliverable for Phase 2 and is based on the foundational principles and schema adopted in the `STATE_OF_THE_ART_AND_GAP_ANALYSIS.md` report. The schema is a direct formalization of the ETL logic implemented in the `src/ingestion/tkg_importer.py` script.

The purpose of this specification is to provide a comprehensive, machine-readable, and human-understandable definition of the graph's structure, ensuring consistency and clarity for all development, integration, and query activities.

### 1.1. Core Principles

The schema adheres to the following core principles:

*   **Technique-Centric:** The model exclusively imports and represents MITRE ATT&CK techniques, tactics, mitigations, and data sources. It is designed to capture the relationships between adversarial behaviors and the means to detect and mitigate them.
*   **Detection-Focused:** The schema is optimized to model the critical relationships between techniques and their detection mechanisms, specifically through the `DataComponent` and `DataSource` nodes.
*   **Exclusion Mandate:** To maintain a sharp focus and avoid the complexities of modeling temporal or attributional data, this schema explicitly forbids the creation of nodes representing `ThreatGroup`, `Campaign`, `Software`, `Malware`, or any other temporal entities.

## 2. Schema Visualization

The following diagram illustrates the formal relationships between the nodes in the TKG schema.

```mermaid
graph TD
    subgraph TKG Schema
        Tactic -- HAS_TECHNIQUE --> Technique
        Technique -- HAS_SUBTECHNIQUE --> SubTechnique
        Technique -- MITIGATED_BY --> Mitigation
        SubTechnique -- MITIGATED_BY --> Mitigation
        Technique -- DETECTED_BY --> DataComponent
        SubTechnique -- DETECTED_BY --> DataComponent
        DataSource -- HAS_COMPONENT --> DataComponent
    end

    classDef nodeStyle fill:#f9f,stroke:#333,stroke-width:2px;
    class Tactic,Technique,SubTechnique,Mitigation,DataSource,DataComponent nodeStyle;
```

## 3. Node Definitions

This section details the labels and properties for each node type in the schema. Properties are derived directly from the MITRE ATT&CK Enterprise Matrix via the `tkg_importer.py` script.

### 3.1. `Tactic`

Represents a high-level tactical goal of an adversary, such as "Initial Access" or "Execution."

| Property      | Type   | Description                               | Example                  |
|---------------|--------|-------------------------------------------|--------------------------|
| `id`          | String | The unique identifier (tactic name).      | `initial-access`         |
| `name`        | String | The full name of the tactic.              | `Initial Access`         |
| `shortname`   | String | The short name of the tactic.             | `initial-access`         |
| `description` | String | The official description from MITRE.      | `The adversary is...`    |
| `url`         | String | The URL to the official MITRE documentation. | `https://attack.mitre.org/...` |

### 3.2. `Technique` / `SubTechnique`

Represents a specific adversarial technique or sub-technique. Both are stored with the `Technique` label, differentiated by the `is_subtechnique` property.

| Property            | Type    | Description                                                 | Example                  |
|---------------------|---------|-------------------------------------------------------------|--------------------------|
| `id`                | String  | The unique MITRE ATT&CK ID.                                 | `T1548`                  |
| `stix_id`           | String  | The unique STIX 2.1 identifier.                             | `attack-pattern--...`    |
| `name`              | String  | The full name of the technique.                             | `Abuse Elevation Control Mechanism` |
| `description`       | String  | The official description from MITRE.                        | `Adversaries may...`     |
| `url`               | String  | The URL to the official MITRE documentation.                | `https://attack.mitre.org/...` |
| `is_subtechnique`   | Boolean | `true` if the node is a sub-technique, otherwise `false`.   | `true`                   |

### 3.3. `Mitigation`

Represents a security control or action that can mitigate one or more techniques.

| Property      | Type   | Description                               | Example                  |
|---------------|--------|-------------------------------------------|--------------------------|
| `id`          | String | The unique MITRE ATT&CK ID.               | `M1047`                  |
| `stix_id`     | String | The unique STIX 2.1 identifier.           | `course-of-action--...`  |
| `name`        | String | The full name of the mitigation.          | `Audit`                  |
| `description` | String | The official description from MITRE.      | `System auditing can be...`|

### 3.4. `DataSource`

Represents a source of data that can be collected to detect adversarial activity.

| Property      | Type   | Description                               | Example                  |
|---------------|--------|-------------------------------------------|--------------------------|
| `id`          | String | The unique MITRE ATT&CK ID.               | `DS0017`                 |
| `stix_id`     | String | The unique STIX 2.1 identifier.           | `x-mitre-data-source--...`|
| `name`        | String | The full name of the data source.         | `Command`                |
| `description` | String | The official description from MITRE.      | `Adversaries may execute...`|

### 3.5. `DataComponent`

Represents a specific field or element within a `DataSource`.

| Property      | Type   | Description                               | Example                  |
|---------------|--------|-------------------------------------------|--------------------------|
| `id`          | String | The unique STIX 2.1 identifier.           | `x-mitre-data-component--...` |
| `name`        | String | The full name of the data component.      | `Command Execution`      |
| `description` | String | The official description from MITRE.      | `Execution of commands...` |

## 4. Relationship Definitions

This section defines the directed relationships that connect the nodes in the graph.

| Source         | Relationship         | Target          | Description                                            |
|----------------|----------------------|-----------------|--------------------------------------------------------|
| `(:Tactic)`    | `-[:HAS_TECHNIQUE]->` | `(:Technique)`  | A Tactic is composed of one or more Techniques.        |
| `(:Technique)` | `-[:HAS_SUBTECHNIQUE]->`| `(:Technique)`  | A Technique can have one or more Sub-techniques.       |
| `(:Technique)` | `-[:MITIGATED_BY]->` | `(:Mitigation)` | A Technique can be mitigated by one or more Mitigations. |
| `(:Technique)` | `-[:DETECTED_BY]->`  | `(:DataComponent)`| A Technique can be detected by observing a Data Component. |
| `(:DataSource)`| `-[:HAS_COMPONENT]->`| `(:DataComponent)`| A DataSource is composed of one or more Data Components. |

*Note: The `(:Technique)` - `[:MITIGATED_BY]` -> `(:Mitigation)` relationship also applies to Sub-techniques.*

## 5. Machine-Readable Schema (Cypher DDL)

The following Cypher Data Definition Language (DDL) statements can be used to enforce the schema's structure and constraints in a Neo4j database.

```cypher
-- Create constraints for unique identification and performance
CREATE CONSTRAINT ON (t:Tactic) ASSERT t.name IS UNIQUE;
CREATE CONSTRAINT ON (t:Technique) ASSERT t.id IS UNIQUE;
CREATE CONSTRAINT ON (m:Mitigation) ASSERT m.id IS UNIQUE;
CREATE CONSTRAINT ON (ds:DataSource) ASSERT ds.id IS UNIQUE;
CREATE CONSTRAINT ON (dc:DataComponent) ASSERT dc.id IS UNIQUE;

-- Optional: Create indexes for faster lookups on common properties
CREATE INDEX ON :Technique(name);
CREATE INDEX ON :Mitigation(name);
CREATE INDEX ON :DataSource(name);
CREATE INDEX ON :DataComponent(name);

# Technical Implementation Blueprint: Project TKG

**Version:** 1.0
**Date:** 2025-07-24
**Status:** Final

## 1. Introduction

This document provides the complete technical blueprint for the implementation of the Project TKG knowledge graph. It is intended for solution architects and the development team, providing a practical and actionable guide to building and operationalizing the system.

This blueprint is the primary deliverable of the project's design phase and is based on the foundational decisions established in the `STATE_OF_THE_ART_AND_GAP_ANALYSIS.md` and the `docs/FORMAL_GRAPH_SCHEMA_SPECIFICATION.md`.

## 2. Technology Stack Recommendation

This section formalizes the technology choices for the project, providing justifications based on the project's specific requirements.

### 2.1. Graph Database: Neo4j

**Recommendation:** The project will use **Neo4j** as its graph database.

**Justification:**
The choice to formalize Neo4j is based on a comprehensive evaluation of its capabilities against the project's needs, as identified in the gap analysis. While the reference implementation `src/ingestion/tkg_importer.py` already uses Neo4j, this decision is now confirmed for the following reasons:

1.  **Query Language Expressiveness (Cypher):** Neo4j's query language, Cypher, is a declarative, pattern-matching language that is highly intuitive for graph traversal. Its ASCII-art-like syntax makes it easy to express complex relationships and queries, which is critical for the ?? reasoning layer. When compared to alternatives like Gremlin (imperative) or SPARQL (RDF-focused), Cypher provides a more direct and readable way to model the intricate paths required by security analysts.

2.  **Scalability and Performance:** Neo4j is a native graph database, meaning it stores data in a graph structure from the ground up. This results in index-free adjacency, allowing for extremely fast traversal of relationships regardless of the total dataset size. For a knowledge graph that will grow with the MITRE ATT&CK framework and potentially other sources, this performance characteristic is paramount.

3.  **Ease of Integration and Ecosystem:** Neo4j has a mature ecosystem with robust client libraries for major programming languages, including the Python driver used in the reference importer. Its strong community support, extensive documentation, and enterprise-ready features (e.g., clustering, security, monitoring) make it a low-risk, high-reward choice for a production system.

4.  **Deployment Flexibility (Docker):** Deploying Neo4j via Docker provides unmatched flexibility and portability. It allows for a consistent environment across development, staging, and production, simplifies dependency management, and enables scalable, isolated deployments. This aligns with modern DevOps practices and ensures the project's infrastructure is both robust and maintainable.

### 2.1.1. Deployment Model: Self-Hosted Docker

**Recommendation:** Neo4j will be deployed as a self-hosted container using Docker. This approach provides a consistent, portable, and isolated environment for the database, simplifying dependency management and ensuring reproducibility across development, testing, and production environments.

**Example `docker-compose.yml`:**
```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    container_name: project_tkg_neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - ./neo4j/data:/data
      - ./neo4j/logs:/logs
      - ./neo4j/conf:/var/lib/neo4j/conf
    environment:
      - NEO4J_AUTH=neo4j/your_strong_password
```

### 2.2. Query Interface Layer: graphiti

**Recommendation:** The project will use **`graphiti`** as the primary library for data modeling and query interaction.

**Justification:**
`graphiti` directly addresses the need for a formal, accessible query interface. Its selection is justified by three key features:

1.  **Schema-First Development:** By using Pydantic models to define the graph schema, `graphiti` provides a Python-native, type-safe, and self-documenting layer for all graph interactions. This aligns with the project's goal of maintaining a clear and enforceable schema.
2.  **Simplified Data Access:** The library automatically deserializes query results into Pydantic objects, abstracting away the manual parsing of database records and simplifying application logic.
3.  **Natural Language Accessibility:** `graphiti`'s built-in capability to translate natural language questions into Cypher queries significantly lowers the barrier to entry for security analysts and other non-developer stakeholders, allowing them to explore the knowledge graph without writing Cypher.

**Architecture:**
The following diagram illustrates how `graphiti` will serve as the intermediary between the application layer and the Neo4j database.

```mermaid
graph TD
    subgraph Application Layer
        A[API Endpoint (e.g., FastAPI)]
        B[Natural Language Query]
        C[Programmatic Query (Cypher)]
    end

    subgraph Query Interface
        G[graphiti]
    end

    subgraph Database
        N[Neo4j]
    end

    B -- Translates --> G
    C -- Executes --> G
    A -- Wraps --> G
    G -- Cypher --> N
```

## 3. Automated Ingestion Pipeline

This section formally documents the design of the automated ingestion pipeline, which is responsible for populating and maintaining the knowledge graph.

### 3.1. Reference Implementation

The official reference implementation for the ingestion pipeline is the Python script located at `src/ingestion/tkg_importer.py`. All development must adhere to the principles and patterns established in this script.

### 3.2. Pipeline Architecture

The ingestion pipeline is designed as a four-stage process, ensuring data integrity, performance, and idempotency.

```mermaid
graph TD
    A[1. Fetch Latest STIX Data] --> B[2. Parse and Filter Schema]
    B --> C[3. Transform to Graph Structures]
    C --> D[4. Idempotent Database Write]

    subgraph "src/ingestion/tkg_importer.py"
        A
        B
        C
        D
    end

    subgraph External
        E[MITRE ATT&CK CTI Repo]
    end

    subgraph Internal
        F[Neo4j Database]
    end

    E -- HTTPS GET --> A
    D -- Bolt Connection --> F
```

### 3.3. Key Functions

1.  **Fetching Latest Dataset:** The pipeline initiates by making an HTTP GET request to the official MITRE CTI repository to download the latest Enterprise ATT&CK dataset in STIX 2.1 format. This ensures the graph is always built from the most current, authoritative source.

2.  **Parsing and Filtering:** The raw STIX data is loaded into a memory store. During this process, objects are filtered against a strict allow-list (`ALLOWED_TYPES`) to enforce the project's technique-centric schema. Only `attack-pattern`, `course-of-action`, `x-mitre-tactic`, `x-mitre-data-source`, and `x-mitre-data-component` objects are retained.

3.  **Transforming to Graph-Native Structures:** The filtered STIX objects are transformed into a format suitable for Neo4j. This involves extracting key properties and preparing them for batch import as nodes and relationships that conform to the `FORMAL_GRAPH_SCHEMA_SPECIFICATION.md`.

4.  **Idempotent Database Writing:** The transformed data is written to the Neo4j database using an idempotent `MERGE` operation. This ensures that running the import multiple times will not create duplicate nodes or relationships. The process is batched by node and relationship type for high performance and reliability, and it begins by clearing the database to ensure a fresh, consistent state with each run.


# Model API-key
A working Gemini API key (with google-ai-studio as provider) is present in ./.env file:
GEMINI_API_KEY=AIzaSyBj0TK4W3ua2Ux5hchDiAZUqRSS-ivZs3w
GEMINI_MODEL_PROVIDER=google_ai_studio  # Options: "google_ai_studio", "vertex_ai"
GEMINI_CHAT_MODEL=models/gemini-2.5-flash-preview-05-20
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-exp-03-07
