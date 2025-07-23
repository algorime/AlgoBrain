# AlgoBrain Technical Specifications
## Detailed Implementation Guide for Red-Team Agent System

---

## **1. SYSTEM ARCHITECTURE OVERVIEW**

### **1.1 High-Level Architecture**

```mermaid
graph TB
    User[Red-Team Operator] --> API[AlgoBrain API]
    API --> Supervisor[Supervisor Agent]
    
    Supervisor --> RAG[Traditional RAG Agent]
    Supervisor --> GraphRAG[GraphRAG Agent]
    Supervisor --> Intel[Threat Intel Agent]
    
    RAG --> Qdrant[(Qdrant Vector DB)]
    GraphRAG --> Graphiti[Graphiti Server]
    Graphiti --> Neo4j[(Neo4j Graph DB)]
    Intel --> WebSearch[Web Search API]
    
    Qdrant --> SecureBERT[SecureBERT Embeddings]
    Neo4j --> MITRE[MITRE ATT&CK Data]
    
    Supervisor --> Synthesis[Response Synthesis]
    Synthesis --> User
```

### **1.2 Component Specifications**

| Component | Technology | Version | Purpose | Performance Target |
|-----------|------------|---------|---------|-------------------|
| **Supervisor Agent** | LangGraph + Gemini 2.5 Flash | Latest | Query routing & orchestration | < 100ms routing |
| **Traditional RAG** | Qdrant + SecureBERT | Latest | Payload & technique retrieval | < 500ms search |
| **GraphRAG Agent** | Graphiti + Neo4j | Latest | Relationship & chain analysis | < 1s traversal |
| **Threat Intel** | Tavily + Web APIs | Latest | Real-time threat data | < 2s fetch |
| **Vector Database** | Qdrant | Latest | Semantic search | < 50ms query |
| **Graph Database** | Neo4j | 5.22+ | Relationship storage | < 100ms cypher |
| **API Framework** | FastAPI | Latest | HTTP/WebSocket interface | < 50ms overhead |

---

## **2. DATA MODELS & SCHEMAS**

### **2.1 Core Data Structures**

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Literal
from datetime import datetime
from enum import Enum

class QueryType(str, Enum):
    PAYLOAD = "payload"
    TECHNIQUE = "technique" 
    CHAIN = "chain"
    TOOL = "tool"
    INTEL = "intelligence"
    ANALYSIS = "analysis"

class AttackPhase(str, Enum):
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial-access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege-escalation"
    DEFENSE_EVASION = "defense-evasion"
    CREDENTIAL_ACCESS = "credential-access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral-movement"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

class QueryClassification(BaseModel):
    primary_type: QueryType
    confidence: float = Field(ge=0.0, le=1.0)
    secondary_types: List[QueryType] = []
    requires_multi_agent: bool = False
    attack_phase: Optional[AttackPhase] = None

class TargetEnvironment(BaseModel):
    operating_systems: List[str] = []
    technologies: List[str] = []
    network_architecture: Optional[str] = None
    security_controls: List[str] = []
    privilege_level: Literal["user", "admin", "system", "unknown"] = "unknown"

class AttackContext(BaseModel):
    engagement_id: Optional[str] = None
    target_environment: TargetEnvironment
    current_phase: AttackPhase = AttackPhase.RECONNAISSANCE
    techniques_attempted: List[str] = []
    successful_techniques: List[str] = []
    discovered_vulnerabilities: List[str] = []
    acquired_credentials: List[Dict] = []
    pivot_points: List[str] = []
    objectives: List[str] = []

class KnowledgeSource(BaseModel):
    type: Literal["vector", "graph", "web", "llm"]
    collection: Optional[str] = None
    query_used: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    source_documents: List[str] = []
    mitre_techniques: List[str] = []

class PayloadResult(BaseModel):
    content: str
    payload_type: str
    target_platforms: List[str]
    complexity: Literal["low", "medium", "high"]
    stealth_rating: float = Field(ge=0.0, le=1.0)
    success_probability: float = Field(ge=0.0, le=1.0)
    detection_risk: float = Field(ge=0.0, le=1.0)
    prerequisites: List[str] = []
    variations: List[str] = []

class TechniqueResult(BaseModel):
    mitre_id: str
    name: str
    description: str
    tactic: str
    platforms: List[str]
    data_sources: List[str]
    permissions_required: List[str]
    related_techniques: List[str] = []
    tools: List[str] = []
    mitigations: List[str] = []

class AttackChain(BaseModel):
    chain_id: str
    techniques: List[TechniqueResult]
    relationships: List[Dict[str, str]]
    total_steps: int
    complexity_score: float = Field(ge=0.0, le=1.0)
    stealth_score: float = Field(ge=0.0, le=1.0)
    prerequisites: List[str] = []
    expected_outcomes: List[str] = []

class RiskAssessment(BaseModel):
    overall_risk: Literal["low", "medium", "high", "critical"]
    cvss_score: Optional[float] = Field(ge=0.0, le=10.0)
    business_impact: Literal["minimal", "moderate", "significant", "severe"]
    detection_probability: Literal["low", "medium", "high"]
    attribution_risk: Literal["low", "medium", "high"]
    legal_considerations: List[str] = []
    recommended_precautions: List[str] = []

class AgentResponse(BaseModel):
    agent_type: str
    response_content: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[KnowledgeSource]
    processing_time: float
    payloads: List[PayloadResult] = []
    techniques: List[TechniqueResult] = []
    attack_chains: List[AttackChain] = []
    risk_assessment: Optional[RiskAssessment] = None

class RedTeamQuery(BaseModel):
    query: str
    context: AttackContext
    user_preferences: Dict[str, Union[str, bool, float]] = {}
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RedTeamResponse(BaseModel):
    query_id: str
    classification: QueryClassification
    answer: str
    sources: List[KnowledgeSource]
    agent_responses: List[AgentResponse]
    updated_context: AttackContext
    next_steps: List[str] = []
    related_queries: List[str] = []
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### **2.2 Database Schemas**

#### **2.2.1 Qdrant Collections Schema**

```python
from qdrant_client.models import VectorParams, Distance

QDRANT_COLLECTIONS = {
    "payloads": {
        "vectors_config": VectorParams(size=768, distance=Distance.COSINE),
        "payload_schema": {
            "content": "text",
            "payload_type": "keyword",
            "attack_types": "keyword[]",
            "target_platforms": "keyword[]", 
            "complexity": "keyword",
            "stealth_rating": "float",
            "success_probability": "float",
            "detection_risk": "float",
            "prerequisites": "text[]",
            "source": "keyword",
            "mitre_techniques": "keyword[]",
            "created_date": "datetime",
            "last_verified": "datetime"
        }
    },
    
    "techniques": {
        "vectors_config": VectorParams(size=768, distance=Distance.COSINE),
        "payload_schema": {
            "content": "text",
            "mitre_id": "keyword",
            "name": "text",
            "tactic": "keyword",
            "platforms": "keyword[]",
            "data_sources": "keyword[]",
            "permissions_required": "keyword[]",
            "impact_type": "keyword[]",
            "defense_bypassed": "keyword[]",
            "source": "keyword",
            "confidence_score": "float"
        }
    },
    
    "tools": {
        "vectors_config": VectorParams(size=768, distance=Distance.COSINE),
        "payload_schema": {
            "content": "text",
            "tool_name": "keyword",
            "tool_category": "keyword",
            "operating_systems": "keyword[]",
            "skill_level": "keyword",
            "detection_risk": "float",
            "installation_complexity": "keyword",
            "usage_examples": "text[]",
            "mitre_techniques": "keyword[]",
            "last_updated": "datetime"
        }
    },
    
    "intelligence": {
        "vectors_config": VectorParams(size=768, distance=Distance.COSINE),
        "payload_schema": {
            "content": "text",
            "threat_actor": "keyword",
            "campaign": "keyword",
            "first_seen": "datetime",
            "last_seen": "datetime",
            "confidence": "float",
            "iocs": "text[]",
            "ttps": "keyword[]",
            "target_sectors": "keyword[]",
            "geographic_regions": "keyword[]"
        }
    }
}
```

#### **2.2.2 Neo4j Graph Schema**

```cypher
-- Node Constraints
CREATE CONSTRAINT technique_mitre_id FOR (t:Technique) REQUIRE t.mitre_id IS UNIQUE;
CREATE CONSTRAINT tactic_name FOR (ta:Tactic) REQUIRE ta.name IS UNIQUE;
CREATE CONSTRAINT tool_name FOR (to:Tool) REQUIRE to.name IS UNIQUE;
CREATE CONSTRAINT group_mitre_id FOR (g:Group) REQUIRE g.mitre_id IS UNIQUE;
CREATE CONSTRAINT mitigation_mitre_id FOR (m:Mitigation) REQUIRE m.mitre_id IS UNIQUE;
CREATE CONSTRAINT vulnerability_cve FOR (v:Vulnerability) REQUIRE v.cve_id IS UNIQUE;

-- Performance Indexes
CREATE INDEX technique_name FOR (t:Technique) ON (t.name);
CREATE INDEX technique_platforms FOR (t:Technique) ON (t.platforms);
CREATE INDEX tool_category FOR (to:Tool) ON (to.category);
CREATE INDEX group_name FOR (g:Group) ON (g.name);

-- Full-text Search Indexes
CREATE FULLTEXT INDEX technique_search FOR (t:Technique) ON EACH [t.name, t.description];
CREATE FULLTEXT INDEX tool_search FOR (to:Tool) ON EACH [to.name, to.description];

-- Node Properties Schema
// Technique Node
(:Technique {
    mitre_id: "T1059.001",
    name: "PowerShell",
    description: "Adversaries may abuse PowerShell commands...",
    platforms: ["Windows"],
    data_sources: ["Command", "Process"],
    permissions_required: ["User", "Administrator"],
    defense_bypassed: ["Anti-virus", "Host intrusion prevention systems"],
    impact_type: ["Execute"],
    created: datetime("2017-05-31T21:30:44.329Z"),
    modified: datetime("2023-10-03T20:58:12.142Z")
})

// Tactic Node
(:Tactic {
    mitre_id: "TA0002",
    name: "Execution", 
    description: "The adversary is trying to run malicious code.",
    created: datetime("2018-10-17T00:14:20.652Z"),
    modified: datetime("2019-07-19T17:43:41.967Z")
})

// Tool Node
(:Tool {
    mitre_id: "S0154",
    name: "Cobalt Strike",
    description: "Cobalt Strike is a commercial penetration testing tool...",
    type: "malware",
    platforms: ["Windows"],
    aliases: ["CS"],
    created: datetime("2018-04-18T17:59:24.739Z"),
    modified: datetime("2023-04-14T20:44:26.495Z")
})

// Group Node
(:Group {
    mitre_id: "G0016",
    name: "APT29",
    description: "APT29 is threat group that has been attributed to Russia...",
    aliases: ["YTTRIUM", "The Dukes", "Cozy Bear"],
    created: datetime("2017-05-31T21:31:53.197Z"),
    modified: datetime("2023-09-29T20:50:52.249Z")
})

-- Relationship Types and Properties
// Technique belongs to Tactic
(:Technique)-[:BELONGS_TO]->(:Tactic)

// Group uses Technique
(:Group)-[:USES {first_seen: datetime(), confidence: "high"}]->(:Technique)

// Tool implements Technique
(:Tool)-[:IMPLEMENTS {effectiveness: "high"}]->(:Technique)

// Technique leads to another Technique
(:Technique)-[:LEADS_TO {probability: 0.8, conditions: ["successful_execution"]}]->(:Technique)

// Mitigation addresses Technique
(:Mitigation)-[:MITIGATES {effectiveness: "partial"}]->(:Technique)

// Technique exploits Vulnerability
(:Technique)-[:EXPLOITS {reliability: "high"}]->(:Vulnerability)
```

---

## **3. API SPECIFICATIONS**

### **3.1 RESTful API Endpoints**

#### **3.1.1 Core Query Endpoint**

```python
@app.post("/api/v1/query", response_model=RedTeamResponse)
async def process_red_team_query(
    query: RedTeamQuery,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> RedTeamResponse:
    """
    Main endpoint for red-team intelligence queries.
    
    Supports:
    - Payload generation and retrieval
    - Attack technique analysis  
    - Attack chain planning
    - Tool recommendations
    - Threat intelligence lookup
    """
    
    # Validate query and context
    validation_result = await validate_red_team_request(query, current_user)
    if not validation_result.allowed:
        raise HTTPException(
            status_code=400,
            detail=validation_result.reason
        )
    
    # Process query through supervisor agent
    response = await supervisor_agent.process_query(query)
    
    # Log for audit purposes
    background_tasks.add_task(
        audit_logger.log_query,
        query=query,
        response=response,
        user=current_user
    )
    
    return response

# Request/Response Examples
"""
POST /api/v1/query
{
    "query": "SQL injection payloads for MySQL 8.0 with WAF bypass",
    "context": {
        "target_environment": {
            "technologies": ["MySQL 8.0", "Apache", "PHP"],
            "security_controls": ["ModSecurity WAF"],
            "privilege_level": "user"
        },
        "current_phase": "initial-access",
        "engagement_id": "ENG-2025-001"
    },
    "user_preferences": {
        "technical_depth": "expert",
        "include_mitigations": false,
        "response_format": "detailed"
    },
    "session_id": "sess_abc123"
}

Response:
{
    "query_id": "q_def456",
    "classification": {
        "primary_type": "payload",
        "confidence": 0.95,
        "attack_phase": "initial-access"
    },
    "answer": "Based on your target environment (MySQL 8.0 with ModSecurity), here are effective SQL injection payloads...",
    "sources": [
        {
            "type": "vector",
            "collection": "payloads", 
            "relevance_score": 0.92,
            "source_documents": ["PayloadAllTheThings", "PortSwigger"]
        }
    ],
    "agent_responses": [
        {
            "agent_type": "traditional_rag",
            "confidence": 0.9,
            "payloads": [
                {
                    "content": "'; SELECT SLEEP(5)-- -",
                    "payload_type": "time_based_blind",
                    "target_platforms": ["MySQL"],
                    "stealth_rating": 0.7,
                    "success_probability": 0.85,
                    "detection_risk": 0.3
                }
            ]
        }
    ],
    "next_steps": [
        "Test payloads in isolated environment",
        "Consider privilege escalation techniques",
        "Review database access controls"
    ],
    "confidence_score": 0.88,
    "processing_time": 1.2
}
"""
```

#### **3.1.2 Attack Chain Analysis Endpoint**

```python
@app.post("/api/v1/attack-chain", response_model=List[AttackChain])
async def analyze_attack_chain(
    request: AttackChainRequest
) -> List[AttackChain]:
    """
    Analyze possible attack chains from current position to target objective.
    """
    
    chains = await graph_rag_agent.analyze_attack_paths(
        start_technique=request.current_technique,
        target_objective=request.objective,
        constraints=request.constraints
    )
    
    return chains

# Request Model
class AttackChainRequest(BaseModel):
    current_technique: str  # MITRE ID or technique name
    objective: str  # "privilege_escalation", "data_exfiltration", etc.
    max_steps: int = 6
    constraints: Dict[str, Any] = {}  # Platform, stealth requirements, etc.
```

#### **3.1.3 Tool Recommendation Endpoint**

```python
@app.post("/api/v1/tools/recommend")
async def recommend_tools(
    request: ToolRecommendationRequest
) -> ToolRecommendationResponse:
    """
    Recommend tools based on technique, environment, and user skill level.
    """
    
    recommendations = await tool_recommendation_engine.recommend(
        technique=request.technique,
        environment=request.environment,
        user_profile=request.user_profile
    )
    
    return recommendations
```

#### **3.1.4 Threat Intelligence Endpoint**

```python
@app.get("/api/v1/threat-intel/{technique_id}")
async def get_threat_intelligence(
    technique_id: str,
    include_recent: bool = True,
    confidence_threshold: float = 0.7
) -> ThreatIntelligenceResponse:
    """
    Get current threat intelligence for specific technique.
    """
    
    intel = await threat_intel_agent.get_latest_intelligence(
        technique_id=technique_id,
        include_recent=include_recent,
        confidence_threshold=confidence_threshold
    )
    
    return intel
```

### **3.2 WebSocket Interface**

```python
@app.websocket("/ws/analysis")
async def websocket_analysis(websocket: WebSocket):
    """
    Real-time analysis interface for complex multi-step operations.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive analysis request
            data = await websocket.receive_json()
            
            if data["type"] == "start_analysis":
                # Begin streaming analysis
                async for step in supervisor_agent.stream_analysis(data):
                    await websocket.send_json({
                        "type": "analysis_step",
                        "step": step.name,
                        "progress": step.progress,
                        "results": step.results,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                await websocket.send_json({
                    "type": "analysis_complete",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        logger.info("Client disconnected from analysis stream")
```

---

## **4. AGENT IMPLEMENTATION SPECIFICATIONS**

### **4.1 Supervisor Agent Implementation**

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, add_messages

class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    classification: QueryClassification
    agent_results: Dict[str, Any]
    final_response: Optional[str]
    processing_metadata: Dict[str, Any]

class SupervisorAgent:
    def __init__(
        self,
        llm_client: GeminiClient,
        traditional_rag: TraditionalRAGAgent,
        graph_rag: GraphRAGAgent,
        threat_intel: ThreatIntelAgent
    ):
        self.llm = llm_client
        self.agents = {
            "traditional_rag": traditional_rag,
            "graph_rag": graph_rag,
            "threat_intel": threat_intel
        }
        self.classifier = QueryClassifier()
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for agent orchestration."""
        
        workflow = StateGraph(SupervisorState)
        
        # Add nodes
        workflow.add_node("classify", self._classify_query)
        workflow.add_node("route", self._route_to_agents)
        workflow.add_node("synthesize", self._synthesize_response)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "classify",
            self._should_route_multi_agent,
            {
                "single": "route",
                "multi": "route",
                "direct": "synthesize"
            }
        )
        
        workflow.add_edge("route", "synthesize")
        workflow.add_edge("synthesize", END)
        
        workflow.set_entry_point("classify")
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _classify_query(self, state: SupervisorState) -> Dict:
        """Classify incoming query and determine routing strategy."""
        
        classification = await self.classifier.classify(state["query"])
        
        return {
            "classification": classification,
            "processing_metadata": {
                "classification_time": time.time(),
                "confidence": classification.confidence
            }
        }
    
    async def _route_to_agents(self, state: SupervisorState) -> Dict:
        """Route query to appropriate agents based on classification."""
        
        classification = state["classification"]
        results = {}
        
        # Determine which agents to invoke
        agents_to_invoke = []
        
        if classification.primary_type in ["payload", "technique"]:
            agents_to_invoke.append("traditional_rag")
        
        if classification.primary_type in ["chain", "analysis"]:
            agents_to_invoke.append("graph_rag")
        
        if classification.primary_type == "intel" or classification.requires_multi_agent:
            agents_to_invoke.append("threat_intel")
        
        # Execute agents concurrently
        tasks = []
        for agent_name in agents_to_invoke:
            tasks.append(
                self.agents[agent_name].process(
                    state["query"],
                    state.get("attack_context", {})
                )
            )
        
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Package results
        for i, agent_name in enumerate(agents_to_invoke):
            if not isinstance(agent_results[i], Exception):
                results[agent_name] = agent_results[i]
            else:
                logger.error(f"Agent {agent_name} failed: {agent_results[i]}")
                results[agent_name] = {"error": str(agent_results[i])}
        
        return {"agent_results": results}
    
    async def _synthesize_response(self, state: SupervisorState) -> Dict:
        """Synthesize final response from agent results."""
        
        synthesis_prompt = self._build_synthesis_prompt(
            state["query"],
            state["agent_results"]
        )
        
        final_response = await self.llm.generate(synthesis_prompt)
        
        return {
            "final_response": final_response,
            "processing_metadata": {
                **state.get("processing_metadata", {}),
                "synthesis_time": time.time(),
                "agents_used": list(state["agent_results"].keys())
            }
        }
```

### **4.2 Traditional RAG Agent Implementation**

```python
from qdrant_client import AsyncQdrantClient
from sentence_transformers import SentenceTransformer

class TraditionalRAGAgent:
    def __init__(
        self,
        qdrant_client: AsyncQdrantClient,
        embedder: SentenceTransformer  # SecureBERT model
    ):
        self.client = qdrant_client
        self.embedder = embedder
        self.collection_router = CollectionRouter()
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Process query through traditional vector search."""
        
        start_time = time.time()
        
        # Route to appropriate collections
        target_collections = await self.collection_router.route(query, context)
        
        # Generate embedding
        query_embedding = self.embedder.encode(query)
        
        # Search across collections
        search_results = await self._federated_search(
            query_embedding,
            target_collections,
            context
        )
        
        # Format results
        response_content = await self._format_results(search_results, query)
        
        processing_time = time.time() - start_time
        
        return AgentResponse(
            agent_type="traditional_rag",
            response_content=response_content,
            confidence=self._calculate_confidence(search_results),
            sources=self._extract_sources(search_results),
            processing_time=processing_time,
            payloads=self._extract_payloads(search_results),
            techniques=self._extract_techniques(search_results)
        )
    
    async def _federated_search(
        self,
        query_embedding: np.ndarray,
        collections: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, List]:
        """Search across multiple collections with context-based filtering."""
        
        search_tasks = []
        
        for collection in collections:
            # Build collection-specific filters
            filters = self._build_filters(collection, context)
            
            search_tasks.append(
                self.client.search(
                    collection_name=collection,
                    query_vector=query_embedding.tolist(),
                    query_filter=filters,
                    limit=10,
                    with_payload=True,
                    with_vectors=False
                )
            )
        
        results = await asyncio.gather(*search_tasks)
        
        # Combine and rank results
        combined_results = {}
        for i, collection in enumerate(collections):
            combined_results[collection] = results[i]
        
        return combined_results
```

### **4.3 GraphRAG Agent Implementation**

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient

class GraphRAGAgent:
    def __init__(
        self,
        graphiti_client: Graphiti,
        mitre_mapper: MITREATTACKMapper
    ):
        self.client = graphiti_client
        self.mitre_mapper = mitre_mapper
        self.cypher_generator = CypherQueryGenerator()
    
    async def process(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Process query through graph traversal and relationship analysis."""
        
        start_time = time.time()
        
        # Determine query intent for graph operations
        graph_intent = await self._analyze_graph_intent(query, context)
        
        results = []
        
        if graph_intent.type == "attack_chain":
            results = await self._analyze_attack_chains(
                graph_intent.start_technique,
                graph_intent.target_objective,
                context
            )
        elif graph_intent.type == "technique_relationships":
            results = await self._find_technique_relationships(
                graph_intent.technique,
                graph_intent.relationship_types
            )
        elif graph_intent.type == "tool_mapping":
            results = await self._map_tools_to_techniques(
                graph_intent.techniques,
                context.get("target_environment", {})
            )
        
        processing_time = time.time() - start_time
        
        return AgentResponse(
            agent_type="graph_rag",
            response_content=await self._format_graph_results(results),
            confidence=self._calculate_graph_confidence(results),
            sources=self._extract_graph_sources(results),
            processing_time=processing_time,
            attack_chains=self._extract_attack_chains(results),
            techniques=self._extract_graph_techniques(results)
        )
    
    async def _analyze_attack_chains(
        self,
        start_technique: str,
        target_objective: str,
        context: Dict[str, Any]
    ) -> List[AttackChain]:
        """Find optimal attack chains using graph traversal."""
        
        # Convert objective to graph query
        cypher_query = self.cypher_generator.build_attack_chain_query(
            start_technique=start_technique,
            objective=target_objective,
            max_steps=context.get("max_steps", 6),
            platform_constraints=context.get("target_environment", {}).get("operating_systems", [])
        )
        
        # Execute graph traversal
        graph_results = await self.client.execute_cypher(cypher_query)
        
        # Convert to attack chain objects
        attack_chains = []
        for result in graph_results:
            chain = AttackChain(
                chain_id=f"chain_{hash(str(result))}",
                techniques=await self._extract_chain_techniques(result),
                relationships=await self._extract_chain_relationships(result),
                total_steps=len(result.get("path", [])),
                complexity_score=await self._calculate_chain_complexity(result),
                stealth_score=await self._calculate_stealth_score(result)
            )
            attack_chains.append(chain)
        
        return attack_chains
```

---

## **5. PERFORMANCE OPTIMIZATION SPECIFICATIONS**

### **5.1 Caching Strategy**

```python
import redis.asyncio as redis
from functools import wraps
import pickle
import hashlib

class RedTeamCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 300  # 5 minutes
    
    def cache_query_result(self, ttl: Optional[int] = None):
        """Decorator for caching query results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = await self.redis.get(cache_key)
                if cached_result:
                    return pickle.loads(cached_result)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                serialized = pickle.dumps(result)
                await self.redis.setex(
                    cache_key,
                    ttl or self.default_ttl,
                    serialized
                )
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate deterministic cache key."""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return f"redteam:cache:{hashlib.md5(key_data.encode()).hexdigest()}"

# Usage example
cache = RedTeamCache("redis://localhost:6379")

class CachedRAGAgent(TraditionalRAGAgent):
    @cache.cache_query_result(ttl=600)  # Cache for 10 minutes
    async def search_payloads(self, query: str, filters: Dict) -> List[PayloadResult]:
        return await super().search_payloads(query, filters)
```

### **5.2 Database Connection Pooling**

```python
from qdrant_client import AsyncQdrantClient
from neo4j import AsyncGraphDatabase
import asyncio

class DatabaseManager:
    def __init__(self):
        self.qdrant_pool = None
        self.neo4j_pool = None
        self._lock = asyncio.Lock()
    
    async def get_qdrant_client(self) -> AsyncQdrantClient:
        """Get Qdrant client with connection pooling."""
        if not self.qdrant_pool:
            async with self._lock:
                if not self.qdrant_pool:
                    self.qdrant_pool = AsyncQdrantClient(
                        url=config.QDRANT_URL,
                        api_key=config.QDRANT_API_KEY,
                        timeout=10.0,
                        # Connection pool settings
                        prefer_grpc=True,
                        grpc_port=6334
                    )
        return self.qdrant_pool
    
    async def get_neo4j_driver(self):
        """Get Neo4j driver with connection pooling."""
        if not self.neo4j_pool:
            async with self._lock:
                if not self.neo4j_pool:
                    self.neo4j_pool = AsyncGraphDatabase.driver(
                        config.NEO4J_URI,
                        auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
                        max_connection_lifetime=3600,
                        max_connection_pool_size=50,
                        connection_acquisition_timeout=60.0
                    )
        return self.neo4j_pool

# Global database manager
db_manager = DatabaseManager()
```

### **5.3 Async Processing Pipeline**

```python
import asyncio
from asyncio import Semaphore

class AsyncProcessingPipeline:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = Semaphore(max_concurrent)
        self.task_queue = asyncio.Queue()
        self.result_cache = {}
    
    async def process_batch(
        self,
        queries: List[str],
        processor_func: Callable
    ) -> Dict[str, Any]:
        """Process multiple queries concurrently with rate limiting."""
        
        tasks = []
        for query in queries:
            task = self._process_with_semaphore(query, processor_func)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Format results
        formatted_results = {}
        for i, query in enumerate(queries):
            if isinstance(results[i], Exception):
                formatted_results[query] = {"error": str(results[i])}
            else:
                formatted_results[query] = results[i]
        
        return formatted_results
    
    async def _process_with_semaphore(
        self,
        query: str,
        processor_func: Callable
    ) -> Any:
        """Process single query with concurrency control."""
        async with self.semaphore:
            return await processor_func(query)
```

---

## **6. SECURITY & AUDIT SPECIFICATIONS**

### **6.1 Authentication & Authorization**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

class SecurityManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expire_minutes = 60
    
    async def authenticate_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """Authenticate user from JWT token."""
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            # Verify user exists and has red-team access
            user = await self.get_user(user_id)
            if not user or not user.has_redteam_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for red-team operations"
                )
            
            return user
            
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    
    async def authorize_engagement(
        self,
        user: User,
        engagement_id: Optional[str]
    ) -> bool:
        """Verify user is authorized for specific engagement."""
        if not engagement_id:
            return True  # General queries allowed
        
        engagement = await self.get_engagement(engagement_id)
        return user.id in engagement.authorized_users

class User(BaseModel):
    id: str
    username: str
    role: str
    has_redteam_access: bool
    authorized_engagements: List[str]
    created_at: datetime
    last_login: Optional[datetime]
```

### **6.2 Audit Logging System**

```python
from sqlalchemy import Column, String, DateTime, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
import logging

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    engagement_id = Column(String, nullable=True)
    
    # Query details
    query_text = Column(Text, nullable=False)
    query_classification = Column(String, nullable=False)
    query_confidence = Column(Float, nullable=False)
    
    # Processing details
    agents_used = Column(JSON, nullable=False)
    processing_time = Column(Float, nullable=False)
    response_confidence = Column(Float, nullable=False)
    
    # Risk assessment
    risk_level = Column(String, nullable=False)
    contains_payloads = Column(Boolean, default=False)
    contains_exploits = Column(Boolean, default=False)
    
    # Response metadata
    sources_accessed = Column(JSON, nullable=False)
    techniques_referenced = Column(JSON, nullable=True)
    tools_referenced = Column(JSON, nullable=True)

class RedTeamAuditLogger:
    def __init__(self, db_session):
        self.db = db_session
        self.logger = logging.getLogger("redteam.audit")
    
    async def log_query(
        self,
        query: RedTeamQuery,
        response: RedTeamResponse,
        user: User
    ):
        """Log red-team query with full audit trail."""
        
        audit_record = AuditLog(
            id=response.query_id,
            user_id=user.id,
            session_id=query.session_id,
            engagement_id=query.context.engagement_id,
            query_text=query.query,
            query_classification=response.classification.primary_type,
            query_confidence=response.classification.confidence,
            agents_used=[r.agent_type for r in response.agent_responses],
            processing_time=response.processing_time,
            response_confidence=response.confidence_score,
            risk_level=self._assess_query_risk(query, response),
            contains_payloads=self._contains_payloads(response),
            contains_exploits=self._contains_exploits(response),
            sources_accessed=[s.type for s in response.sources],
            techniques_referenced=self._extract_techniques(response),
            tools_referenced=self._extract_tools(response)
        )
        
        # Store in database
        self.db.add(audit_record)
        await self.db.commit()
        
        # Log to file for compliance
        self.logger.info(
            f"REDTEAM_QUERY user={user.id} "
            f"engagement={query.context.engagement_id} "
            f"classification={response.classification.primary_type} "
            f"risk={audit_record.risk_level} "
            f"agents={audit_record.agents_used}"
        )
```

### **6.3 Rate Limiting & Abuse Prevention**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

class RedTeamRateLimiter:
    def __init__(self):
        self.limiter = Limiter(
            key_func=self._get_user_key,
            default_limits=["100/hour", "10/minute"]
        )
    
    def _get_user_key(self, request):
        """Get rate limiting key based on user authentication."""
        # Extract user ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, verify=False)
                return f"user:{payload.get('sub', 'anonymous')}"
            except:
                pass
        return get_remote_address(request)
    
    def red_team_limit(self, rate: str):
        """Custom rate limiter for red-team operations."""
        return self.limiter.limit(rate)

# Usage in endpoints
rate_limiter = RedTeamRateLimiter()

@app.post("/api/v1/query")
@rate_limiter.red_team_limit("20/minute")
async def process_query(request: Request, query: RedTeamQuery):
    # Process query...
    pass
```

---

## **7. DEPLOYMENT SPECIFICATIONS**

### **7.1 Production Docker Compose**

```yaml
version: '3.8'

services:
  # Reverse Proxy & Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - algobrain-api
    restart: unless-stopped

  # AlgoBrain API (Multi-instance)
  algobrain-api:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QDRANT_URL=http://qdrant:6333
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    depends_on:
      qdrant:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
      - ./config/qdrant.yaml:/qdrant/config/production.yaml
    command: ["./qdrant", "--config-path", "/qdrant/config/production.yaml"]
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 6G
        reservations:
          cpus: '1.0'
          memory: 3G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Graph Database
  neo4j:
    image: neo4j:5.22.0-enterprise
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_conf:/conf
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
      - NEO4J_dbms_memory_heap_initial_size=2G
      - NEO4J_dbms_memory_heap_max_size=6G
      - NEO4J_dbms_memory_pagecache_size=2G
      - NEO4J_dbms_connector_bolt_thread_pool_min_size=5
      - NEO4J_dbms_connector_bolt_thread_pool_max_size=400
    deploy:
      resources:
        limits:
          cpus: '3.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  # GraphRAG Server
  graphiti-server:
    image: zepai/graphiti:latest
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
    depends_on:
      neo4j:
        condition: service_healthy
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Cache Layer
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # SQL Database for Audit Logs
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

volumes:
  qdrant_data:
  neo4j_data:
  neo4j_logs:
  neo4j_conf:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: algobrain-prod
    driver: bridge
```

### **7.2 Kubernetes Production Deployment**

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: algobrain-prod

---
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: algobrain-secrets
  namespace: algobrain-prod
type: Opaque
stringData:
  gemini-api-key: "${GEMINI_API_KEY}"
  neo4j-password: "${NEO4J_PASSWORD}"
  jwt-secret: "${JWT_SECRET}"
  redis-password: "${REDIS_PASSWORD}"

---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: algobrain-config
  namespace: algobrain-prod
data:
  qdrant-url: "http://qdrant-service:6333"
  neo4j-uri: "bolt://neo4j-service:7687"
  redis-url: "redis://redis-service:6379"

---
# kubernetes/algobrain-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: algobrain-api
  namespace: algobrain-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: algobrain-api
  template:
    metadata:
      labels:
        app: algobrain-api
    spec:
      containers:
      - name: api
        image: algobrain:latest
        ports:
        - containerPort: 8080
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: algobrain-secrets
              key: gemini-api-key
        - name: QDRANT_URL
          valueFrom:
            configMapKeyRef:
              name: algobrain-config
              key: qdrant-url
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: algobrain-api-service
  namespace: algobrain-prod
spec:
  selector:
    app: algobrain-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

---

## **8. MONITORING & OBSERVABILITY**

### **8.1 Metrics Collection**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

class RedTeamMetrics:
    def __init__(self):
        # Query metrics
        self.query_total = Counter(
            'redteam_queries_total',
            'Total number of red-team queries',
            ['query_type', 'user_id', 'status']
        )
        
        self.query_duration = Histogram(
            'redteam_query_duration_seconds',
            'Time spent processing queries',
            ['query_type', 'agent_type']
        )
        
        self.agent_invocations = Counter(
            'redteam_agent_invocations_total',
            'Number of agent invocations',
            ['agent_type', 'status']
        )
        
        # Knowledge base metrics
        self.kb_size = Gauge(
            'redteam_knowledge_base_size',
            'Number of documents in knowledge base',
            ['collection']
        )
        
        self.confidence_scores = Histogram(
            'redteam_confidence_scores',
            'Distribution of confidence scores',
            ['agent_type']
        )
        
        # Error metrics
        self.errors_total = Counter(
            'redteam_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
    
    def record_query(
        self,
        query_type: str,
        user_id: str,
        duration: float,
        status: str
    ):
        """Record query metrics."""
        self.query_total.labels(
            query_type=query_type,
            user_id=user_id,
            status=status
        ).inc()
        
        self.query_duration.labels(
            query_type=query_type,
            agent_type="supervisor"
        ).observe(duration)
    
    def record_agent_invocation(
        self,
        agent_type: str,
        duration: float,
        confidence: float,
        status: str
    ):
        """Record agent-specific metrics."""
        self.agent_invocations.labels(
            agent_type=agent_type,
            status=status
        ).inc()
        
        self.confidence_scores.labels(
            agent_type=agent_type
        ).observe(confidence)

# Global metrics instance
metrics = RedTeamMetrics()
```

### **8.2 Health Check System**

```python
from typing import Dict, List
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ComponentHealth(BaseModel):
    name: str
    status: HealthStatus
    response_time: Optional[float]
    error_message: Optional[str]
    last_check: datetime

class SystemHealth(BaseModel):
    overall_status: HealthStatus
    components: List[ComponentHealth]
    timestamp: datetime

class HealthChecker:
    def __init__(
        self,
        qdrant_client: AsyncQdrantClient,
        neo4j_driver: AsyncDriver,
        redis_client: redis.Redis
    ):
        self.qdrant = qdrant_client
        self.neo4j = neo4j_driver
        self.redis = redis_client
    
    async def check_system_health(self) -> SystemHealth:
        """Perform comprehensive system health check."""
        
        checks = await asyncio.gather(
            self.check_qdrant(),
            self.check_neo4j(),
            self.check_redis(),
            self.check_gemini_api(),
            return_exceptions=True
        )
        
        components = []
        for check in checks:
            if isinstance(check, ComponentHealth):
                components.append(check)
            else:
                # Handle exception
                components.append(ComponentHealth(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    error_message=str(check),
                    last_check=datetime.utcnow()
                ))
        
        # Determine overall status
        if all(c.status == HealthStatus.HEALTHY for c in components):
            overall_status = HealthStatus.HEALTHY
        elif any(c.status == HealthStatus.UNHEALTHY for c in components):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
        
        return SystemHealth(
            overall_status=overall_status,
            components=components,
            timestamp=datetime.utcnow()
        )
    
    async def check_qdrant(self) -> ComponentHealth:
        """Check Qdrant vector database health."""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            collections = await self.qdrant.get_collections()
            response_time = time.time() - start_time
            
            if collections:
                return ComponentHealth(
                    name="qdrant",
                    status=HealthStatus.HEALTHY,
                    response_time=response_time,
                    last_check=datetime.utcnow()
                )
            else:
                return ComponentHealth(
                    name="qdrant",
                    status=HealthStatus.DEGRADED,
                    response_time=response_time,
                    error_message="No collections found",
                    last_check=datetime.utcnow()
                )
                
        except Exception as e:
            return ComponentHealth(
                name="qdrant",
                status=HealthStatus.UNHEALTHY,
                error_message=str(e),
                last_check=datetime.utcnow()
            )
```

---

This completes the comprehensive technical specifications for AlgoBrain. The document provides detailed implementation guidance for all system components, ensuring a production-ready red-team penetration testing agent with optimal performance, security, and observability.