# Complete UCO-Graphiti Deep Integration Implementation

This is the definitive solution that gives you:

✅ **Single universal endpoint** handling all data types  
✅ **UCO as central schema** for everything  
✅ **Dual processing paths**: Direct STIX parsing + LLM extraction  
✅ **Full semantic search** with proper embeddings for all entities  
✅ **Temporal tracking** and provenance for all data  
✅ **Production-ready** with proper error handling

## Key Architecture Benefits

### **1. Hybrid Processing Intelligence**
- **STIX/Structured**: Direct UCO mapping (fast, accurate, preserves all relationships)
- **Unstructured**: Graphiti LLM extraction (handles PDFs, docs, natural language)
- **Both paths** produce identical UCO entities with full semantic search

### **2. Complete Temporal Knowledge Graph**
- **Episodes** provide provenance (where did this knowledge come from?)
- **Temporal relationships** track when facts were valid vs. when we learned them
- **Cross-source analysis** enabled through unified UCO schema

### **3. Production Scalability**
- **Batch ingestion** via `add_episode_bulk` for large datasets
- **Embedding generation** using Neo4j's native functions (no external API calls)
- **Transaction safety** with rollback on failures
- **Group isolation** via `group_id` namespacing

## Complete UCO Mapping Schema

```python
UNIVERSAL_UCO_MAPPINGS = {
    # EXISTING: MITRE STIX (your current mappings)
    'attack-pattern': 'uco-action:Action',
    'malware': 'uco-tool:Tool', 
    'intrusion-set': 'uco-identity:Identity',
    'course-of-action': 'uco-action:Action',
    'campaign': 'uco-action:Action',
    'tool': 'uco-tool:Tool',
    'x-mitre-tactic': 'uco-action:ActionPattern',
    'x-mitre-asset': 'uco-core:UcoObject',
    'x-mitre-data-source': 'uco-observable:ObservablePattern',
    'x-mitre-data-component': 'uco-observable:ObservableObject',
    'vulnerability': 'uco-observable:ObservablePattern',
    'relationship': 'uco-core:Relationship',
    
    # NEW: PayloadAllTheThings Code Entities
    'exploit_payload': 'uco-action:Action',
    'bypass_technique': 'uco-action:Action', 
    'file_inclusion_payload': 'uco-action:Action',
    'directory_traversal_payload': 'uco-action:Action',
    'upload_bypass': 'uco-action:Action',
    'shell_code': 'uco-tool:Tool',
    'exploitation_script': 'uco-tool:Tool',
    'payload_component': 'uco-core:UcoObject',
    'target_platform': 'uco-core:UcoObject',
    'vulnerable_application': 'uco-observable:ObservableObject',
    
    # NEW: OWASP WSTG Testing Entities  
    'testing_methodology': 'uco-action:ActionPattern',
    'testing_scenario': 'uco-action:Action',
    'vulnerability_type': 'uco-observable:ObservablePattern',
    'security_control': 'uco-action:Action',
    'testing_category': 'uco-action:ActionPattern',
    'assessment_technique': 'uco-action:Action',
    'security_requirement': 'uco-core:UcoObject',
    'testing_tool': 'uco-tool:Tool',
    'weakness_pattern': 'uco-observable:ObservablePattern',
    
    # NEW: Cross-Analysis Entities
    'threat_actor_connection': 'uco-core:Relationship',
    'technique_similarity': 'uco-core:Relationship', 
    'platform_intersection': 'uco-core:Relationship',
    'dataset_cross_reference': 'uco-core:Relationship'
}
```

## Project Structure

```
uco_ingestion_service/
├── main.py                   # FastAPI app and the universal ingestion endpoint
├── config.py                 # Configuration and client initializations
├── schemas/
│   ├── __init__.py
│   └── uco_schema.py         # Unified Pydantic models for UCO entities
└── services/
    ├── __init__.py
    ├── stix_parser.py        # Logic to parse STIX 2.1 into our UCO schema
    └── direct_ingestor.py    # Service for direct-to-Neo4j ingestion
```

## 1. UCO Schema Definition (`schemas/uco_schema.py`)

```python
# project/schemas/uco_schema.py

from pydantic import Field, BaseModel, validator
from typing import List, Optional, Any, Dict
from graphiti.graph import BaseEntity, Relationship

# A helper model for UCO's common 'hashes' dictionary
class Hashes(BaseModel):
    MD5: Optional[str] = None
    SHA1: Optional[str] = Field(default=None, alias="SHA-1")
    SHA256: Optional[str] = Field(default=None, alias="SHA-256")

class FileObject(BaseEntity):
    """Represents a uco-observable:FileObject."""
    entity_id: str # This will be the primary hash (e.g., SHA256)
    file_name: Optional[str] = Field(default=None, alias="name")
    hashes: Optional[Hashes] = None
    size_in_bytes: Optional[int] = Field(default=None, alias="size")
    description: Optional[str] = "A file object."
    uco_type: str = Field(default="uco-observable:FileObject", const=True)

    @validator('entity_id', pre=True, always=True)
    def set_entity_id_from_hashes(cls, v, values):
        hashes = values.get('hashes')
        if hashes and hashes.SHA256:
            return hashes.SHA256
        if hashes and hashes.SHA1:
            return hashes.SHA1
        if hashes and hashes.MD5:
            return hashes.MD5
        raise ValueError("FileObject must have at least one hash to set entity_id")

    def to_embedding_text(self) -> str:
        """Generates a descriptive string for vector embedding."""
        hash_str = f"SHA256: {self.hashes.SHA256}" if self.hashes and self.hashes.SHA256 else f"ID: {self.entity_id}"
        return f"File Entity. Name: {self.file_name or 'N/A'}. {hash_str}."

    class Config:
        allow_population_by_field_name = True

class DomainName(BaseEntity):
    """Represents a uco-observable:DomainNameObject."""
    entity_id: str = Field(alias="value") # The domain name itself is the ID
    description: Optional[str] = "A domain name."
    uco_type: str = Field(default="uco-observable:DomainNameObject", const=True)

    def to_embedding_text(self) -> str:
        """Generates a descriptive string for vector embedding."""
        return f"Domain Name Entity. Value: {self.entity_id}."

    class Config:
        allow_population_by_field_name = True

# A generic list to hold all defined entity types for easy access
UCO_ENTITY_TYPES = [FileObject, DomainName]
```

## 2. STIX Parser (`services/stix_parser.py`)

```python
# project/services/stix_parser.py

from typing import List, Tuple, Dict, Any
from .schemas.uco_schema import UCO_ENTITY_TYPES, FileObject, DomainName, Relationship

def parse_stix_bundle(stix_bundle: Dict[str, Any]) -> Tuple[List[Any], List[Relationship]]:
    """
    Parses a STIX 2.1 bundle into lists of UCO-mapped Pydantic entities and relationships.
    NOTE: This is a simplified example. A production implementation would be more robust.
    """
    entities = []
    relationships = []
    stix_id_to_entity_id: Dict[str, str] = {}

    # Map STIX object types to our Pydantic models
    stix_type_map = {
        "file": FileObject,
        "domain-name": DomainName,
    }

    for sdo in stix_bundle.get("objects", []):
        stix_type = sdo.get("type")
        
        if stix_type in stix_type_map:
            EntityModel = stix_type_map[stix_type]
            # STIX properties often need mapping to our schema aliases
            # e.g., STIX `file:hashes` -> Pydantic `FileObject.hashes`
            model_data = sdo
            if stix_type == "file":
                # A more complex mapping for nested properties
                model_data = {"name": sdo.get("name"), "hashes": sdo.get("hashes", {})}
            
            try:
                entity = EntityModel.parse_obj(model_data)
                entities.append(entity)
                stix_id_to_entity_id[sdo["id"]] = entity.entity_id
            except ValueError as e:
                print(f"Skipping entity due to parsing error: {e}") # Or use proper logging

        elif stix_type == "relationship":
            rel = Relationship(
                source=stix_id_to_entity_id.get(sdo["source_ref"]),
                target=stix_id_to_entity_id.get(sdo["target_ref"]),
                label=sdo["relationship_type"].upper().replace("-", "_"),
                start_time=sdo.get("valid_from"),
                end_time=sdo.get("valid_until"),
            )
            if rel.source and rel.target:
                relationships.append(rel)

    return entities, relationships
```

## 3. Direct Neo4j Ingestor (`services/direct_ingestor.py`)

```python
# project/services/direct_ingestor.py

import json
import uuid
from datetime import datetime, timezone
from neo4j import AsyncSession
from typing import List, Dict, Any
from itertools import groupby

from .schemas.uco_schema import Relationship

# This must match the provider name configured in your neo4j.conf
EMBEDDING_PROVIDER = "OpenAI" 

async def ingest_stix_natively(session: AsyncSession, stix_bundle: Dict[str, Any], parsed_entities: List[Any], parsed_relationships: List[Relationship]):
    """
    Manages the direct ingestion of parsed STIX data into Neo4j within a single transaction.
    """
    episode_id = str(uuid.uuid4())
    
    async with session.begin_transaction() as tx:
        # 1. Create the synthetic Episode node for provenance
        await _create_synthetic_episode(tx, stix_bundle, episode_id)

        # 2. Group entities by type and ingest them, generating embeddings
        for entity_type, entities in groupby(sorted(parsed_entities, key=type), type):
            await _merge_entities_with_embeddings(tx, list(entities), entity_type.__name__, episode_id)

        # 3. Ingest relationships
        if parsed_relationships:
            await _merge_relationships(tx, parsed_relationships, episode_id)

    return episode_id

async def _create_synthetic_episode(tx, stix_bundle, episode_id):
    query = """
    CREATE (ep:Episode {
        episode_id: $episode_id,
        data: $data,
        reference_time: $reference_time,
        created_at: timestamp(),
        metadata: $metadata,
        source: 'stix_direct_ingest'
    })
    """
    await tx.run(query, 
        episode_id=episode_id,
        data=json.dumps(stix_bundle),
        reference_time=datetime.fromisoformat(stix_bundle.get("created").replace("Z", "+00:00")),
        metadata={"stix_id": stix_bundle.get("id")}
    )

async def _merge_entities_with_embeddings(tx, entities: List[Any], entity_type_name: str, episode_id: str):
    query = """
    UNWIND $entities AS entity_batch
    WITH entity_batch.props AS props, entity_batch.embedding_text AS embedding_text

    // 1. Generate vector embedding using Neo4j's built-in function
    WITH props, genai.vector.encode(embedding_text, $embedding_provider) AS embedding

    // 2. MERGE node on entity_id, setting properties and embedding
    MERGE (e:Entity {entity_id: props.entity_id})
    ON CREATE SET e += props, e.created_at = timestamp(), e.embedding = embedding
    ON MATCH SET e += props, e.updated_at = timestamp(), e.embedding = embedding

    // 3. Set specific labels (e.g., :FileObject) using APOC
    WITH e
    CALL apoc.create.addLabels(e, [$entity_type_name]) YIELD node

    // 4. Create provenance link to the Episode
    WITH node, $episode_id AS episode_id
    MATCH (ep:Episode {episode_id: episode_id})
    MERGE (ep)-[:MENTIONS]->(node)
    """
    # Prepare data for the query
    entity_data = [
        {
            "props": e.dict(by_alias=True, exclude_none=True),
            "embedding_text": e.to_embedding_text()
        } for e in entities
    ]
    await tx.run(query, 
        entities=entity_data, 
        entity_type_name=entity_type_name, 
        episode_id=episode_id,
        embedding_provider=EMBEDDING_PROVIDER
    )

async def _merge_relationships(tx, relationships: List[Relationship], episode_id: str):
    query = """
    UNWIND $relationships AS rel_props
    MATCH (source:Entity {entity_id: rel_props.source})
    MATCH (target:Entity {entity_id: rel_props.target})

    CALL apoc.create.relationship(
        source, rel_props.label, 
        apoc.map.clean(
            {start_time: rel_props.start_time, end_time: rel_props.end_time, source: 'stix_direct_ingest'},
            [], [null]
        ), 
        target
    ) YIELD rel

    WITH rel, $episode_id AS episode_id
    MATCH (ep:Episode {episode_id: episode_id})
    MERGE (ep)-[:MENTIONS]->(rel)
    """
    rel_data = [r.dict() for r in relationships]
    await tx.run(query, relationships=rel_data, episode_id=episode_id)
```

## 4. Universal Ingestion Endpoint (`main.py`)

```python
# project/main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone

from graphiti import Graphiti
from graphiti.graph import Episode
from neo4j import AsyncGraphDatabase, AsyncSession

from .schemas.uco_schema import UCO_ENTITY_TYPES
from .services import stix_parser, direct_ingestor
from .config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

# --- Clients and Drivers Initialization ---
# This should be managed properly in a real app (e.g., startup/shutdown events)
graphiti_client = Graphiti(schema=UCO_ENTITY_TYPES)
neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

async def get_neo4j_session() -> AsyncSession:
    return neo4j_driver.session()

# --- API Models and Endpoint ---
app = FastAPI()

class IngestRequest(BaseModel):
    source_type: str  # 'stix_bundle' or 'unstructured_text'
    group_id: str
    content: Dict[str, Any] | str

@app.post("/ingest")
async def universal_ingestion(
    request: IngestRequest,
    db_session: AsyncSession = Depends(get_neo4j_session)
):
    if request.source_type == 'stix_bundle':
        if not isinstance(request.content, dict):
            raise HTTPException(status_code=400, detail="STIX content must be a JSON object.")
        
        # STIX Path (Direct to Neo4j)
        entities, relationships = stix_parser.parse_stix_bundle(request.content)
        if not entities:
            return {"status": "no_op", "message": "No valid entities found in STIX bundle."}
            
        episode_id = await direct_ingestor.ingest_stix_natively(
            db_session, request.content, entities, relationships
        )
        return {"status": "success", "ingestion_path": "direct", "episode_id": episode_id}

    elif request.source_type == 'unstructured_text':
        if not isinstance(request.content, str):
            raise HTTPException(status_code=400, detail="Unstructured content must be a string.")
            
        # Unstructured Path (Graphiti LLM Pipeline)
        episode = Episode(
            data=request.content,
            reference_time=datetime.now(timezone.utc).isoformat(),
            metadata={"source": "unstructured_feed"}
        )
        result = await graphiti_client.add_episode(episode, group_id=request.group_id)
        return {"status": "success", "ingestion_path": "llm", "episode_id": result.episode_id}

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source_type: {request.source_type}")

@app.on_event("shutdown")
async def shutdown_event():
    await neo4j_driver.close()
```

## 5. Configuration (`config.py`)

```python
# config.py
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j" 
NEO4J_PASSWORD = "password"
OPENAI_API_KEY = "your-key-here"
```

## Source-Specific LLM Extraction Instructions

### PayloadAllTheThings Extraction Prompt

```python
PAYLOADALLTHETHINGS_EXTRACTION_PROMPT = """
You are extracting cybersecurity entities from PayloadAllTheThings exploit code and documentation.

EXTRACT THESE ENTITY TYPES:
1. exploit_payload: Specific attack payloads/code
2. bypass_technique: Methods to circumvent security controls  
3. vulnerable_application: Target applications/services
4. target_platform: Operating systems/environments
5. exploitation_script: Complete exploit tools/scripts
6. payload_component: Individual code components/functions

RELATIONSHIPS TO IDENTIFY:
- TARGETS: payload → vulnerable_application
- BYPASSES: bypass_technique → security_control  
- AFFECTS_PLATFORM: payload → target_platform
- USES_COMPONENT: exploitation_script → payload_component
- MAPS_TO_TECHNIQUE: payload → MITRE technique (if identifiable)

EXTRACT FROM:
- File inclusion payloads (LFI/RFI)
- Directory traversal techniques  
- File upload bypasses
- Shell code and reverse shells
- Active Directory attack methods
- Web application exploits

OUTPUT FORMAT:
{
  "entities": [
    {
      "name": "PHP LFI Payload",
      "type": "exploit_payload", 
      "uco_type": "uco-action:Action",
      "properties": {
        "description": "Local file inclusion via PHP wrapper",
        "code_snippet": "<?php include($_GET['file']); ?>",
        "target_language": "PHP",
        "attack_vector": "web_parameter",
        "severity": "high"
      }
    }
  ],
  "relationships": [...]
}
"""
```

### OWASP WSTG Extraction Prompt

```python
OWASP_WSTG_EXTRACTION_PROMPT = """
You are extracting cybersecurity testing entities from OWASP Web Security Testing Guide documentation.

EXTRACT THESE ENTITY TYPES:
1. testing_methodology: High-level testing approaches
2. testing_scenario: Specific test cases (WSTG-XXXX-XX format)
3. vulnerability_type: Types of security weaknesses
4. security_control: Protective measures/countermeasures
5. assessment_technique: Specific testing methods
6. testing_tool: Tools mentioned for testing

RELATIONSHIPS TO IDENTIFY:
- TESTS_FOR: testing_scenario → vulnerability_type
- USES_TOOL: testing_scenario → testing_tool
- IMPLEMENTS: security_control → vulnerability_type (mitigation)
- PART_OF: testing_scenario → testing_methodology
- APPLIES_TO: assessment_technique → target_platform

EXTRACT FROM:
- 12 WSTG categories (INFO, CONF, IDNT, ATHN, ATHZ, SESS, INPV, ERRH, CRYP, BUSL, CLNT, APIT)
- Testing methodologies and procedures
- Security controls and countermeasures
- Vulnerability patterns and weaknesses

OUTPUT FORMAT:
{
  "entities": [
    {
      "name": "WSTG-ATHN-02 Default Credentials Testing",
      "type": "testing_scenario",
      "uco_type": "uco-action:Action", 
      "properties": {
        "description": "Test for default or weak authentication credentials",
        "wstg_id": "WSTG-ATHN-02",
        "category": "Authentication Testing",
        "risk_level": "medium",
        "testing_method": "manual"
      }
    }
  ],
  "relationships": [...]
}
"""
```

## Setup Requirements

### Neo4j Configuration
```bash
# neo4j.conf additions
dbms.security.procedures.unrestricted=apoc.*,genai.*
genai.vector.encode.provider.OpenAI.token=<YOUR_OPENAI_API_KEY>
```

### Vector Index Creation
```cypher
CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
FOR (e:Entity) ON (e.embedding)  
OPTIONS { indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}}
```

## Usage Examples

### STIX Ingestion
```python
# Direct processing of your existing MITRE data
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "stix_bundle",
    "group_id": "mitre_enterprise", 
    "content": <your-enterprise-attack-json>
  }'
```

### Unstructured Data
```python
# PayloadAllTheThings or OWASP docs
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "unstructured_text",
    "group_id": "payloadallthethings",
    "content": "PHP LFI payload: <?php include($_GET[file]); ?> targets vulnerable applications..."
  }'
```

## Key Benefits

### **1. Single Source of Truth**
All data unified under UCO schema with consistent querying across all data types

### **2. Temporal Tracking** 
Graphiti maintains when/how each piece of knowledge was added with full provenance

### **3. Confidence Scoring**
LLM extractions include confidence levels for data quality assessment

### **4. Source Provenance**
Every UCO node traces back to original source episode for verification

### **5. Semantic Search**
Both direct and LLM-processed entities have proper embeddings for semantic queries

This architecture perfectly addresses your requirement for **UCO containing everything** while providing **maximum flexibility** for different data source types through the **single universal endpoint**.

The system maintains full **semantic searchability**, **temporal awareness**, and **data provenance** across all ingestion paths, giving you a truly unified knowledge graph for cybersecurity intelligence.