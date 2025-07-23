# AlgoBrain Centralized Knowledge Base

This document serves as the centralized knowledge base for the AlgoBrain project, synthesizing information from all existing documentation. It is designed to be a single source of truth for creating all project-related papers and documentation.

---

## 1. Core Architecture

*   **Pattern:** Multi-Agent Supervisor, orchestrated through LangGraph.
*   **State Management:** TypedDict with explicit state transitions for type safety and clarity.
*   **Routing:** Conditional routing logic based on query classification, handled by the Supervisor Agent.
*   **Performance:** Asynchronous and concurrent agent execution for optimized performance.

### 1.1. Agents

*   **Supervisor Agent:**
    *   **Technology:** Gemini 2.5 Flash
    *   **Responsibilities:** Query analysis, intent classification, dynamic tool selection, context management, and response synthesis.
*   **Traditional RAG Agent:**
    *   **Technology:** Qdrant + SecureBERT
    *   **Purpose:** Handles specific queries related to payloads, techniques, and tool documentation.
*   **GraphRAG Agent:**
    *   **Technology:** Graphiti + Neo4j + MITRE ATT&CK
    *   **Purpose:** Manages attack relationship analysis, technique chaining, and strategic planning.
*   **Threat Intelligence Agent:**
    *   **Technology:** Tavily Web Search + CVE Databases
    *   **Purpose:** Provides real-time threat data, information on current exploits, and emerging vulnerabilities.

---

## 2. Technology Stack

| Component       | Technology         | Version | Justification                               |
|-----------------|--------------------|---------|---------------------------------------------|
| **LLM**         | Gemini 2.5 Flash   | Latest  | Fast reasoning, ideal for orchestration     |
| **Orchestration** | LangGraph          | Latest  | State-of-the-art for agentic workflows      |
| **Vector DB**   | Qdrant             | Latest  | High performance, existing setup            |
| **Graph DB**    | Neo4j              | 5.22+   | Required for Graphiti's GraphRAG            |
| **GraphRAG**    | Graphiti           | Latest  | Leading solution for knowledge graph RAG    |
| **Embeddings**  | SecureBERT         | Latest  | Optimized for the cybersecurity domain      |
| **Web Search**  | Tavily             | Latest  | Enables real-time threat intelligence       |
| **API Framework** | FastAPI            | Latest  | High-performance and asynchronous support   |
| **Container**   | Docker             | Latest  | Ensures consistent deployment environments  |

---

## 3. Knowledge Base and Data Sources

### 3.1. Graph Knowledge Base (Neo4j)

*   **Backbone:** MITRE ATT&CK framework.
*   **Node Types:** Techniques, Tactics, Tools, Groups, Mitigations, Vulnerabilities, Payloads, IOCs.
*   **Edge Types:** `EXPLOITS`, `LEADS_TO`, `REQUIRES`, `USES`, `BYPASSES`, `MITIGATES`.
*   **Data Ingestion:** Automated pipeline for processing STIX 2.1 data from the official MITRE repository.

### 3.2. Vector Knowledge Base (Qdrant)

*   **Embedding Model:** SecureBERT (768 dimensions).
*   **Collections:**
    *   `payloads`: Exploitation payloads and PoCs.
    *   `techniques`: Attack techniques and procedures.
    *   `tools`: Red-team tools and usage guides.
    *   `intelligence`: Threat intelligence and Indicators of Compromise (IOCs).
*   **Search:** Hybrid search combining semantic embeddings with keyword filtering.

### 3.3. Primary Data Sources

*   PayloadAllTheThings
*   OWASP Testing Guide
*   MITRE ATT&CK Framework
*   CWE Database
*   Tool Documentation (Burp Suite, OWASP ZAP, sqlmap, etc.)
*   CVE Database
*   Security Research Papers

---

## 4. Key Features

*   **Attack Chain Analysis:** Maps multi-step attack paths using graph traversal.
*   **Contextual Payload Generation:** Creates attack payloads based on the target's environment and constraints.
*   **Tool Recommendation Engine:** Suggests appropriate tools based on the technique, target, and user preferences.
*   **Risk Assessment Integration:** Provides risk context and impact assessments for techniques.

---

## 5. Development Roadmap

### Phase 1: Foundation Setup (Weeks 1-2)
*   **Objective:** Establish core infrastructure and a basic multi-agent architecture.
*   **Deliverables:** A working multi-agent system with existing SQLi knowledge, a Docker deployment setup, and basic web API endpoints.

### Phase 2: Knowledge Graph Development (Weeks 3-5)
*   **Objective:** Implement comprehensive GraphRAG with MITRE ATT&CK integration.
*   **Deliverables:** A fully populated MITRE ATT&CK knowledge graph, a GraphRAG agent with relationship analysis, and an expanded vector knowledge base.

### Phase 3: Advanced Features (Weeks 6-8)
*   **Objective:** Implement specialized penetration testing features.
*   **Deliverables:** A threat intelligence agent with real-time capabilities, an advanced payload generation system, and an intelligent tool recommendation engine.

### Phase 4: Production Optimization (Weeks 9-10)
*   **Objective:** Optimize for production deployment and user experience.
*   **Deliverables:** A production-ready system with monitoring, optimized performance, and comprehensive documentation.

---

## 6. Security and Compliance

*   **Ethical Usage:** A validation layer to check for prohibited language and require explicit authorization context.
*   **Audit & Compliance:** A comprehensive logging system to track all queries and responses for audit purposes.
*   **Rate Limiting:** Implemented to prevent abuse and ensure system stability.