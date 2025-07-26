    #!/usr/bin/env python3
"""
AlgoBrain - Multi-Agent Cybersecurity Intelligence Platform
Main application entry point implementing the LangGraph supervisor architecture.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .database.neo4j_client import Neo4jClient
from .database.qdrant_client import QdrantClient
from .agents.supervisor import SupervisorAgent
from .agents.traditional_rag import TraditionalRAGAgent
from .agents.graph_rag import GraphRAGAgent
from .agents.threat_intel import ThreatIntelAgent
from .ingestion.mitre_importer import MITREImporter
from .utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global clients
neo4j_client = None
qdrant_client = None
supervisor_agent = None


class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    context: Dict[str, Any] = {}
    session_id: str = "default"


class QueryResponse(BaseModel):
    """Response model for queries."""
    response: str
    confidence: float
    sources: list
    agent_path: list
    processing_time: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global neo4j_client, qdrant_client, supervisor_agent
    
    logger.info("Starting AlgoBrain application...")
    
    try:
        # Initialize database clients
        neo4j_client = Neo4jClient(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
        await neo4j_client.connect()
        
        qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        await qdrant_client.connect()
        
        # Initialize agents
        traditional_rag = TraditionalRAGAgent(qdrant_client)
        graph_rag = GraphRAGAgent(neo4j_client)
        threat_intel = ThreatIntelAgent()
        
        supervisor_agent = SupervisorAgent(
            traditional_rag=traditional_rag,
            graph_rag=graph_rag,
            threat_intel=threat_intel
        )
        
        # Initialize MITRE ATT&CK data if needed
        mitre_importer = MITREImporter(neo4j_client)
        if await mitre_importer.should_import():
            logger.info("Importing MITRE ATT&CK data...")
            await mitre_importer.import_data()
        
        logger.info("AlgoBrain application started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Cleanup
        if neo4j_client:
            await neo4j_client.close()
        if qdrant_client:
            await qdrant_client.close()
        logger.info("AlgoBrain application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AlgoBrain",
    description="Multi-Agent Cybersecurity Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AlgoBrain - Multi-Agent Cybersecurity Intelligence Platform",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connections
        neo4j_status = await neo4j_client.health_check() if neo4j_client else False
        qdrant_status = await qdrant_client.health_check() if qdrant_client else False
        
        return {
            "status": "healthy" if neo4j_status and qdrant_status else "degraded",
            "neo4j": "connected" if neo4j_status else "disconnected",
            "qdrant": "connected" if qdrant_status else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a cybersecurity intelligence query."""
    if not supervisor_agent:
        raise HTTPException(status_code=503, detail="Supervisor agent not initialized")
    
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        result = await supervisor_agent.process_query(
            query=request.query,
            context=request.context,
            session_id=request.session_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/ingest/mitre")
async def ingest_mitre_data():
    """Manually trigger MITRE ATT&CK data ingestion."""
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j client not initialized")
    
    try:
        mitre_importer = MITREImporter(neo4j_client)
        await mitre_importer.import_data(force=True)
        return {"message": "MITRE ATT&CK data imported successfully"}
    except Exception as e:
        logger.error(f"MITRE data ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    try:
        stats = {}
        
        if neo4j_client:
            stats["neo4j"] = await neo4j_client.get_stats()
        
        if qdrant_client:
            stats["qdrant"] = await qdrant_client.get_stats()
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )