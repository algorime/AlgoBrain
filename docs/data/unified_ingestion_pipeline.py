"""
Unified Ingestion Pipeline for MITRE ATT&CK Enterprise and ICS Datasets
Implements Graph-First architecture with event-driven synchronization
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Third-party imports (would be installed)
# from neo4j import AsyncGraphDatabase
# from redis.asyncio import Redis
# import aiohttp
# from qdrant_client import QdrantClient
# from elasticsearch import AsyncElasticsearch

from mitre_uco_mapping import MitreUCOConverter, UCONode, UCORelationship

@dataclass
class IngestionConfig:
    """Configuration for the ingestion pipeline"""
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_url: str = "redis://localhost:6379"
    elasticsearch_url: str = "http://localhost:9200"
    qdrant_url: str = "http://localhost:6333"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 256
    batch_size: int = 100
    max_retries: int = 3

class UnifiedIngestionPipeline:
    """
    Main ingestion pipeline that implements the Graph-First architecture
    from FINAL.md with event-driven synchronization
    """
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.converter = MitreUCOConverter()
        self.logger = logging.getLogger(__name__)
        
        # Initialize connections (would be async in real implementation)
        # self.neo4j_driver = AsyncGraphDatabase.driver(config.neo4j_uri, auth=(config.neo4j_user, config.neo4j_password))
        # self.redis_client = Redis.from_url(config.redis_url)
        # self.es_client = AsyncElasticsearch([config.elasticsearch_url])
        # self.qdrant_client = QdrantClient(url=config.qdrant_url)
        
        self.stats = {
            'nodes_processed': 0,
            'relationships_processed': 0,
            'cross_references_created': 0,
            'errors': 0
        }
    
    async def initialize_infrastructure(self) -> None:
        """Initialize the quad-partite data infrastructure"""
        
        self.logger.info("Initializing Neo4j schema...")
        await self._execute_neo4j_schema()
        
        self.logger.info("Setting up Qdrant collections...")
        await self._setup_qdrant_collections()
        
        self.logger.info("Creating Elasticsearch indexes...")
        await self._setup_elasticsearch_indexes()
        
        self.logger.info("Configuring Redis streams...")
        await self._setup_redis_streams()
        
        self.logger.info("Infrastructure initialization complete")
    
    async def _execute_neo4j_schema(self) -> None:
        """Execute the Neo4j schema DDL"""
        schema_path = Path("neo4j_schema_ddl.cypher")
        if schema_path.exists():
            with open(schema_path) as f:
                schema_ddl = f.read()
            
            # In real implementation:
            # async with self.neo4j_driver.session() as session:
            #     await session.run(schema_ddl)
            
            self.logger.info("Neo4j schema applied successfully")
        else:
            self.logger.warning("Schema file not found, skipping schema setup")
    
    async def _setup_qdrant_collections(self) -> None:
        """Setup Qdrant collections for vector storage"""
        collections = {
            "attack_patterns": {
                "size": self.config.embedding_dimensions,
                "distance": "Cosine"
            },
            "threat_actors": {
                "size": self.config.embedding_dimensions,
                "distance": "Cosine"
            },
            "malware": {
                "size": self.config.embedding_dimensions,
                "distance": "Cosine"
            },
            "tools": {
                "size": self.config.embedding_dimensions,
                "distance": "Cosine"
            },
            "campaigns": {
                "size": self.config.embedding_dimensions,
                "distance": "Cosine"
            },
            "ics_assets": {
                "size": self.config.embedding_dimensions,
                "distance": "Cosine"
            }
        }
        
        # In real implementation:
        # for collection_name, config in collections.items():
        #     self.qdrant_client.recreate_collection(
        #         collection_name=collection_name,
        #         vectors_config=VectorParams(size=config["size"], distance=config["distance"])
        #     )
        
        self.logger.info(f"Created {len(collections)} Qdrant collections")
    
    async def _setup_elasticsearch_indexes(self) -> None:
        """Setup Elasticsearch indexes for full-text search"""
        indexes = {
            "mitre_attack_patterns": {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "mitre_id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "platforms": {"type": "keyword"},
                        "tactics": {"type": "keyword"},
                        "source_dataset": {"type": "keyword"},
                        "uco_type": {"type": "keyword"},
                        "created": {"type": "date"},
                        "modified": {"type": "date"}
                    }
                }
            },
            "mitre_entities": {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "mitre_id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "type": {"type": "keyword"},
                        "source_dataset": {"type": "keyword"},
                        "aliases": {"type": "keyword"},
                        "external_references": {"type": "nested"}
                    }
                }
            }
        }
        
        # In real implementation:
        # for index_name, index_config in indexes.items():
        #     await self.es_client.indices.create(index=index_name, body=index_config, ignore=400)
        
        self.logger.info(f"Created {len(indexes)} Elasticsearch indexes")
    
    async def _setup_redis_streams(self) -> None:
        """Setup Redis streams for event-driven synchronization"""
        streams = [
            "mitre_node_updates",
            "mitre_relationship_updates", 
            "cross_reference_updates",
            "vectorization_queue",
            "elasticsearch_queue"
        ]
        
        # In real implementation:
        # for stream in streams:
        #     try:
        #         await self.redis_client.xgroup_create(stream, "processors", id="0", mkstream=True)
        #     except Exception as e:
        #         if "BUSYGROUP" not in str(e):
        #             raise
        
        self.logger.info(f"Configured {len(streams)} Redis streams")
    
    async def ingest_dataset(self, dataset_path: str, dataset_name: str) -> Dict[str, int]:
        """
        Ingest a complete MITRE dataset following the Graph-First approach
        """
        self.logger.info(f"Starting ingestion of {dataset_name} dataset from {dataset_path}")
        
        # Phase 1: Store raw data in object store (MinIO)
        raw_data_uri = await self._store_raw_data(dataset_path, dataset_name)
        
        # Phase 2: Convert to UCO format
        self.converter.process_dataset(dataset_path, dataset_name)
        
        # Phase 3: Batch process nodes (Graph-First)
        node_stats = await self._process_nodes_batch(self.converter.converted_nodes.values())
        
        # Phase 4: Process relationships
        rel_stats = await self._process_relationships_batch(self.converter.converted_relationships)
        
        # Phase 5: Generate cross-dataset connections if this is the second dataset
        cross_stats = {"cross_references": 0}
        if len(set(node.source_dataset for node in self.converter.converted_nodes.values())) > 1:
            cross_connections = self.converter.get_cross_dataset_connections()
            cross_stats = await self._process_relationships_batch(cross_connections)
        
        # Update statistics
        self.stats['nodes_processed'] += node_stats['nodes']
        self.stats['relationships_processed'] += rel_stats['relationships'] 
        self.stats['cross_references_created'] += cross_stats.get('cross_references', 0)
        
        return {
            'dataset': dataset_name,
            'nodes': node_stats['nodes'],
            'relationships': rel_stats['relationships'],
            'cross_references': cross_stats.get('cross_references', 0),
            'raw_data_uri': raw_data_uri
        }
    
    async def _store_raw_data(self, dataset_path: str, dataset_name: str) -> str:
        """Store raw dataset in object store (MinIO)"""
        
        # In real implementation:
        # bucket_name = "mitre-raw-data"
        # object_name = f"{dataset_name}/{datetime.now().isoformat()}.json"
        # 
        # minio_client = Minio(
        #     self.config.minio_endpoint,
        #     access_key=self.config.minio_access_key,
        #     secret_key=self.config.minio_secret_key,
        #     secure=False
        # )
        # 
        # minio_client.fput_object(bucket_name, object_name, dataset_path)
        # uri = f"minio://{bucket_name}/{object_name}"
        
        uri = f"file://{dataset_path}"  # Placeholder for demo
        self.logger.info(f"Stored raw data at {uri}")
        return uri
    
    async def _process_nodes_batch(self, nodes: List[UCONode]) -> Dict[str, int]:
        """Process nodes in batches using Graph-First approach"""
        
        processed = 0
        batch = []
        
        for node in nodes:
            batch.append(node)
            
            if len(batch) >= self.config.batch_size:
                await self._create_neo4j_nodes(batch)
                await self._publish_node_events(batch)
                processed += len(batch)
                batch = []
                
                self.logger.info(f"Processed {processed} nodes...")
        
        # Process remaining nodes
        if batch:
            await self._create_neo4j_nodes(batch)
            await self._publish_node_events(batch)
            processed += len(batch)
        
        return {"nodes": processed}
    
    async def _create_neo4j_nodes(self, nodes: List[UCONode]) -> None:
        """Create nodes in Neo4j (Graph-First)"""
        
        # Group nodes by type for efficient batch creation
        nodes_by_type = {}
        for node in nodes:
            node_type = self._get_neo4j_label(node.mitre_type)
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        # Create nodes by type
        for node_type, type_nodes in nodes_by_type.items():
            cypher_query = self._build_node_creation_query(node_type, type_nodes)
            
            # In real implementation:
            # async with self.neo4j_driver.session() as session:
            #     await session.run(cypher_query, {"nodes": [asdict(node) for node in type_nodes]})
            
            self.logger.debug(f"Created {len(type_nodes)} {node_type} nodes in Neo4j")
    
    def _get_neo4j_label(self, mitre_type: str) -> str:
        """Convert MITRE type to Neo4j label"""
        label_mapping = {
            'attack-pattern': 'AttackPattern',
            'malware': 'Malware',
            'intrusion-set': 'ThreatActor',
            'course-of-action': 'Mitigation',
            'tool': 'Tool',
            'campaign': 'Campaign',
            'x-mitre-tactic': 'Tactic',
            'x-mitre-asset': 'ICSAsset',
            'x-mitre-data-source': 'DataSource',
            'x-mitre-data-component': 'DataComponent',
            'x-mitre-matrix': 'Matrix',
            'x-mitre-collection': 'Collection'
        }
        return label_mapping.get(mitre_type, 'MitreObject')
    
    def _build_node_creation_query(self, node_type: str, nodes: List[UCONode]) -> str:
        """Build Cypher query for batch node creation"""
        
        return f"""
        UNWIND $nodes AS nodeData
        CREATE (n:{node_type} {{
            id: nodeData.id,
            mitre_id: nodeData.mitre_id,
            name: nodeData.name,
            description: nodeData.description,
            mitre_type: nodeData.mitre_type,
            uco_type: nodeData.uco_type,
            source_dataset: nodeData.source_dataset,
            created: datetime(),
            properties: nodeData.properties
        }})
        SET n += nodeData.properties
        """
    
    async def _publish_node_events(self, nodes: List[UCONode]) -> None:
        """Publish node creation events to Redis streams for async processing"""
        
        for node in nodes:
            event_data = {
                'event_type': 'node_created',
                'node_id': node.id,
                'neo4j_label': self._get_neo4j_label(node.mitre_type),
                'content': node.description or node.name or '',
                'source_dataset': node.source_dataset,
                'timestamp': datetime.now().isoformat()
            }
            
            # In real implementation:
            # await self.redis_client.xadd("mitre_node_updates", event_data)
            # await self.redis_client.xadd("vectorization_queue", event_data)
            # await self.redis_client.xadd("elasticsearch_queue", event_data)
            
            self.logger.debug(f"Published events for node {node.id}")
    
    async def _process_relationships_batch(self, relationships: List[UCORelationship]) -> Dict[str, int]:
        """Process relationships in batches"""
        
        processed = 0
        batch = []
        
        for rel in relationships:
            batch.append(rel)
            
            if len(batch) >= self.config.batch_size:
                await self._create_neo4j_relationships(batch)
                await self._publish_relationship_events(batch)
                processed += len(batch)
                batch = []
        
        # Process remaining relationships
        if batch:
            await self._create_neo4j_relationships(batch)
            await self._publish_relationship_events(batch)
            processed += len(batch)
        
        return {"relationships": processed}
    
    async def _create_neo4j_relationships(self, relationships: List[UCORelationship]) -> None:
        """Create relationships in Neo4j"""
        
        # Group relationships by type for efficient creation
        rels_by_type = {}
        for rel in relationships:
            rel_type = rel.relationship_type.upper().replace('-', '_')
            if rel_type not in rels_by_type:
                rels_by_type[rel_type] = []
            rels_by_type[rel_type].append(rel)
        
        # Create relationships by type
        for rel_type, type_rels in rels_by_type.items():
            cypher_query = f"""
            UNWIND $relationships AS relData
            MATCH (source {{id: relData.source_ref}})
            MATCH (target {{id: relData.target_ref}})
            CREATE (source)-[r:{rel_type} {{
                id: relData.id,
                relationship_type: relData.relationship_type,
                uco_relationship_type: relData.uco_relationship_type,
                source_dataset: relData.source_dataset,
                created: datetime()
            }}]->(target)
            SET r += relData.properties
            """
            
            # In real implementation:
            # async with self.neo4j_driver.session() as session:
            #     await session.run(cypher_query, {"relationships": [asdict(rel) for rel in type_rels]})
            
            self.logger.debug(f"Created {len(type_rels)} {rel_type} relationships in Neo4j")
    
    async def _publish_relationship_events(self, relationships: List[UCORelationship]) -> None:
        """Publish relationship events for downstream processing"""
        
        for rel in relationships:
            event_data = {
                'event_type': 'relationship_created',
                'relationship_id': rel.id,
                'source_ref': rel.source_ref,
                'target_ref': rel.target_ref,
                'relationship_type': rel.relationship_type,
                'source_dataset': rel.source_dataset,
                'timestamp': datetime.now().isoformat()
            }
            
            # In real implementation:
            # await self.redis_client.xadd("mitre_relationship_updates", event_data)
            
            self.logger.debug(f"Published event for relationship {rel.id}")
    
    async def run_async_workers(self) -> None:
        """Start asynchronous workers for vectorization and indexing"""
        
        # In real implementation, these would be separate processes/services
        workers = [
            self._vectorization_worker(),
            self._elasticsearch_worker(),
            self._monitoring_worker()
        ]
        
        await asyncio.gather(*workers)
    
    async def _vectorization_worker(self) -> None:
        """Worker for generating embeddings and storing in Qdrant"""
        self.logger.info("Vectorization worker started")
        
        # In real implementation:
        # while True:
        #     try:
        #         messages = await self.redis_client.xreadgroup(
        #             "processors", "vectorization", {"vectorization_queue": ">"}, count=10, block=1000
        #         )
        #         
        #         for stream, msgs in messages:
        #             for msg_id, fields in msgs:
        #                 await self._process_vectorization_event(fields)
        #                 await self.redis_client.xack("vectorization_queue", "processors", msg_id)
        #     
        #     except Exception as e:
        #         self.logger.error(f"Vectorization worker error: {e}")
        #         await asyncio.sleep(5)
    
    async def _elasticsearch_worker(self) -> None:
        """Worker for indexing content in Elasticsearch"""
        self.logger.info("Elasticsearch worker started")
        
        # Similar implementation to vectorization worker
        # Process events from elasticsearch_queue
    
    async def _monitoring_worker(self) -> None:
        """Worker for monitoring and reporting progress"""
        self.logger.info("Monitoring worker started")
        
        # In real implementation:
        # while True:
        #     self.logger.info(f"Pipeline stats: {self.stats}")
        #     await asyncio.sleep(30)
    
    async def get_ingestion_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ingestion statistics"""
        
        # In real implementation, query Neo4j, Qdrant, ES for current counts
        neo4j_stats = {
            'total_nodes': self.stats['nodes_processed'],
            'total_relationships': self.stats['relationships_processed'],
            'enterprise_nodes': 0,  # Query Neo4j
            'ics_nodes': 0,         # Query Neo4j
            'cross_references': self.stats['cross_references_created']
        }
        
        return {
            'neo4j': neo4j_stats,
            'processing_stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }

async def main():
    """Main execution function for testing"""
    
    logging.basicConfig(level=logging.INFO)
    
    config = IngestionConfig()
    pipeline = UnifiedIngestionPipeline(config)
    
    try:
        # Initialize infrastructure
        await pipeline.initialize_infrastructure()
        
        # Ingest both datasets
        enterprise_stats = await pipeline.ingest_dataset(
            'enterprise-attack-17.1.json', 
            'enterprise'
        )
        
        ics_stats = await pipeline.ingest_dataset(
            'ics-attack-17.1.json',
            'ics'
        )
        
        # Get final statistics
        final_stats = await pipeline.get_ingestion_statistics()
        
        print(f"Ingestion Complete!")
        print(f"Enterprise: {enterprise_stats}")
        print(f"ICS: {ics_stats}")
        print(f"Final Stats: {final_stats}")
        
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        raise

if __name__ == "__main__":
    # Test the UCO conversion
    converter = MitreUCOConverter()
    converter.process_dataset('enterprise-attack-17.1.json', 'enterprise')
    converter.process_dataset('ics-attack-17.1.json', 'ics')
    
    cross_connections = converter.get_cross_dataset_connections()
    converter.converted_relationships.extend(cross_connections)
    
    print(f"UCO Conversion Complete!")
    print(f"Total Nodes: {len(converter.converted_nodes)}")
    print(f"Total Relationships: {len(converter.converted_relationships)}")
    
    # Show some sample mappings
    print("\nSample UCO Mappings:")
    for i, (node_id, node) in enumerate(list(converter.converted_nodes.items())[:5]):
        print(f"{i+1}. {node.mitre_type} -> {node.uco_type}: {node.name}")