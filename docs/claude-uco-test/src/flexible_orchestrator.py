#!/usr/bin/env python3
"""
Flexible Orchestrator - Dynamic schema creator and payload ingester with Gemini AI.
"""

from neo4j import GraphDatabase
import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from dataclasses import dataclass
import hashlib
import datetime

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"

@dataclass
class NodeDefinition:
    """Definition for a dynamically created node type."""
    name: str
    description: str
    category: str
    properties: Dict[str, str]
    relationships: List[str]

@dataclass
class PayloadData:
    """Structured payload data from analysis."""
    name: str
    technique: str
    category: str
    description: str
    content: str
    file_path: str
    node_type: str
    relationships: Dict[str, List[str]]

class FlexibleOrchestrator:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Initialize Gemini AI
        self.setup_gemini()
        
        # Track created node types and relationships
        self.known_node_types = set(['Payload', 'Technique', 'Category', 'Source'])
        self.known_relationships = set(['DEFINES'])
        
    def setup_gemini(self):
        """Initialize Gemini AI with API key from .env file."""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        genai.configure(api_key=api_key)
                        print("✅ Gemini AI configured")
                        return
        
        print("⚠️  GEMINI_API_KEY not found in .env file")
        self.gemini_available = False
    
    def analyze_payload_with_ai(self, file_path: str, content: str) -> Optional[PayloadData]:
        """Use Gemini AI to analyze payload and suggest schema."""
        if not hasattr(self, 'gemini_available') or self.gemini_available == False:
            return self.analyze_payload_basic(file_path, content)
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Analyze this cybersecurity payload/exploit code and extract structured information:
            
            File: {file_path}
            Content: {content[:2000]}...
            
            Please provide a JSON response with:
            {{
                "name": "short descriptive name",
                "technique": "attack technique (e.g., SQL Injection, XSS, etc.)",
                "category": "main category (e.g., Web, Network, System, etc.)",
                "description": "detailed description of what this payload does",
                "node_type": "suggested node type (Payload, Exploit, Tool, Script, etc.)",
                "target_system": "target system type",
                "severity": "severity level (Low, Medium, High, Critical)",
                "relationships": {{
                    "TARGETS": ["target types"],
                    "USES": ["techniques or tools"],
                    "BELONGS_TO": ["categories"]
                }}
            }}
            
            Focus on cybersecurity context and be specific about attack techniques.
            """
            
            response = model.generate_content(prompt)
            
            # Try to parse JSON from response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            try:
                data = json.loads(response_text)
                
                return PayloadData(
                    name=data.get('name', Path(file_path).stem),
                    technique=data.get('technique', 'Unknown'),
                    category=data.get('category', 'General'),
                    description=data.get('description', 'No description'),
                    content=content,
                    file_path=file_path,
                    node_type=data.get('node_type', 'Payload'),
                    relationships=data.get('relationships', {})
                )
                
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse AI response as JSON, using basic analysis")
                return self.analyze_payload_basic(file_path, content)
                
        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}, using basic analysis")
            return self.analyze_payload_basic(file_path, content)
    
    def analyze_payload_basic(self, file_path: str, content: str) -> PayloadData:
        """Basic payload analysis without AI."""
        path_obj = Path(file_path)
        
        # Extract category from directory structure
        parts = path_obj.parts
        category = "General"
        technique = "Unknown"
        
        # Common payload categories and techniques
        category_mapping = {
            'sql': ('Web', 'SQL Injection'),
            'xss': ('Web', 'Cross-Site Scripting'),
            'xxe': ('Web', 'XML External Entity'),
            'lfi': ('Web', 'Local File Inclusion'),
            'rfi': ('Web', 'Remote File Inclusion'),
            'upload': ('Web', 'File Upload'),
            'command': ('System', 'Command Injection'),
            'ldap': ('Directory', 'LDAP Injection'),
            'nosql': ('Database', 'NoSQL Injection'),
            'template': ('Web', 'Template Injection'),
            'csrf': ('Web', 'Cross-Site Request Forgery'),
            'deserialization': ('Application', 'Deserialization'),
            'buffer': ('System', 'Buffer Overflow'),
            'privilege': ('System', 'Privilege Escalation')
        }
        
        # Look for keywords in path
        for keyword, (cat, tech) in category_mapping.items():
            if keyword.lower() in str(path_obj).lower():
                category = cat
                technique = tech
                break
        
        return PayloadData(
            name=path_obj.stem.replace('_', ' ').replace('-', ' ').title(),
            technique=technique,
            category=category,
            description=f"Payload from {path_obj.name}",
            content=content,
            file_path=file_path,
            node_type="Payload",
            relationships={
                "BELONGS_TO": [category],
                "USES": [technique]
            }
        )
    
    def create_dynamic_node_type(self, node_type: str, description: str = "") -> bool:
        """Dynamically create a new node type if it doesn't exist."""
        if node_type in self.known_node_types:
            return True
            
        print(f"🆕 Creating dynamic node type: {node_type}")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            try:
                # Add to schema registry
                cypher = """
                MATCH (registry:SchemaRegistry {name: 'PayloadKnowledgeGraph'})
                CREATE (node_type:NodeType {
                    name: $node_type,
                    description: $description,
                    category: 'dynamic',
                    dynamic: true,
                    created: datetime()
                })
                CREATE (registry)-[:DEFINES]->(node_type)
                RETURN node_type
                """
                
                result = session.run(cypher, node_type=node_type, description=description)
                if result.single():
                    self.known_node_types.add(node_type)
                    print(f"   ✅ Created node type: {node_type}")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Failed to create node type {node_type}: {e}")
                
        return False
    
    def create_dynamic_relationship(self, rel_type: str) -> bool:
        """Dynamically create a new relationship type if needed."""
        if rel_type in self.known_relationships:
            return True
            
        print(f"🔗 Registering dynamic relationship: {rel_type}")
        self.known_relationships.add(rel_type)
        return True
    
    def ingest_payload_data(self, payload_data: PayloadData) -> bool:
        """Ingest payload data with dynamic schema creation."""
        print(f"📥 Ingesting: {payload_data.name}")
        
        # Ensure node types exist
        self.create_dynamic_node_type(payload_data.node_type, f"Dynamic {payload_data.node_type}")
        self.create_dynamic_node_type("Technique", "Attack technique or method")
        self.create_dynamic_node_type("Category", "Payload category grouping")
        self.create_dynamic_node_type("Source", "Source file information")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            try:
                # Create payload node with dynamic type
                payload_id = hashlib.md5(payload_data.file_path.encode()).hexdigest()[:12]
                
                # Create main payload node
                cypher_payload = f"""
                CREATE (p:{payload_data.node_type}:Payload {{
                    id: $id,
                    name: $name,
                    description: $description,
                    file_path: $file_path,
                    content_hash: $content_hash,
                    created: datetime(),
                    size: $size
                }})
                RETURN p
                """
                
                content_hash = hashlib.sha256(payload_data.content.encode()).hexdigest()[:16]
                
                session.run(cypher_payload, 
                    id=payload_id,
                    name=payload_data.name,
                    description=payload_data.description,
                    file_path=payload_data.file_path,
                    content_hash=content_hash,
                    size=len(payload_data.content)
                )
                
                # Create technique node
                cypher_technique = """
                MERGE (t:Technique {name: $technique})
                SET t.description = $description,
                    t.updated = datetime()
                RETURN t
                """
                
                session.run(cypher_technique,
                    technique=payload_data.technique,
                    description=f"Attack technique: {payload_data.technique}"
                )
                
                # Create category node
                cypher_category = """
                MERGE (c:Category {name: $category})
                SET c.description = $description,
                    c.updated = datetime()
                RETURN c
                """
                
                session.run(cypher_category,
                    category=payload_data.category,
                    description=f"Payload category: {payload_data.category}"
                )
                
                # Create source node
                cypher_source = """
                MERGE (s:Source {path: $path})
                SET s.filename = $filename,
                    s.type = 'payload_file',
                    s.updated = datetime()
                RETURN s
                """
                
                session.run(cypher_source,
                    path=payload_data.file_path,
                    filename=Path(payload_data.file_path).name
                )
                
                # Create relationships
                relationships = [
                    (f"MATCH (p:{payload_data.node_type} {{id: $id}}) MATCH (t:Technique {{name: $technique}}) MERGE (p)-[:USES]->(t)", "technique"),
                    (f"MATCH (p:{payload_data.node_type} {{id: $id}}) MATCH (c:Category {{name: $category}}) MERGE (p)-[:BELONGS_TO]->(c)", "category"),
                    (f"MATCH (p:{payload_data.node_type} {{id: $id}}) MATCH (s:Source {{path: $path}}) MERGE (p)-[:FROM_SOURCE]->(s)", "source")
                ]
                
                for cypher, rel_type in relationships:
                    if rel_type == "technique":
                        self.create_dynamic_relationship("USES")
                        session.run(cypher, id=payload_id, technique=payload_data.technique)
                    elif rel_type == "category":
                        self.create_dynamic_relationship("BELONGS_TO")
                        session.run(cypher, id=payload_id, category=payload_data.category)
                    elif rel_type == "source":
                        self.create_dynamic_relationship("FROM_SOURCE")
                        session.run(cypher, id=payload_id, path=payload_data.file_path)
                
                # Create additional dynamic relationships from AI analysis
                for rel_type, targets in payload_data.relationships.items():
                    self.create_dynamic_relationship(rel_type)
                    for target in targets:
                        # Create target node if needed
                        cypher_target = """
                        MERGE (target:Entity {name: $name})
                        SET target.type = 'dynamic',
                            target.updated = datetime()
                        RETURN target
                        """
                        session.run(cypher_target, name=target)
                        
                        # Create relationship
                        cypher_rel = f"""
                        MATCH (p:{payload_data.node_type} {{id: $id}})
                        MATCH (target:Entity {{name: $target}})
                        MERGE (p)-[:{rel_type}]->(target)
                        """
                        session.run(cypher_rel, id=payload_id, target=target)
                
                print(f"   ✅ Ingested: {payload_data.name} ({payload_id})")
                return True
                
            except Exception as e:
                print(f"   ❌ Failed to ingest {payload_data.name}: {e}")
                return False
    
    def process_payload_file(self, file_path: str) -> bool:
        """Process a single payload file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Analyze with AI or basic method
            payload_data = self.analyze_payload_with_ai(file_path, content)
            
            if payload_data:
                return self.ingest_payload_data(payload_data)
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            
        return False
    
    def scan_and_ingest_payloads(self, payloads_dir: str, limit: int = 50) -> Dict[str, int]:
        """Scan PayloadsAllTheThings directory and ingest payload files."""
        print(f"🔍 Scanning payloads directory: {payloads_dir}")
        
        stats = {"processed": 0, "success": 0, "failed": 0}
        payloads_path = Path(payloads_dir)
        
        # Common payload file extensions
        payload_extensions = {'.py', '.php', '.js', '.txt', '.sh', '.sql', '.xml', '.json', '.yml', '.yaml'}
        
        # Scan for payload files
        for file_path in payloads_path.rglob("*"):
            if stats["processed"] >= limit:
                break
                
            if (file_path.is_file() and 
                file_path.suffix.lower() in payload_extensions and
                file_path.stat().st_size < 1024 * 1024):  # Skip files > 1MB
                
                stats["processed"] += 1
                
                if self.process_payload_file(str(file_path)):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                
                if stats["processed"] % 10 == 0:
                    print(f"   📊 Progress: {stats['processed']} processed, {stats['success']} success")
        
        return stats
    
    def show_ingestion_summary(self):
        """Show summary of ingested data."""
        print("📊 Ingestion Summary:")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count by node type
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result if record["label"] not in ["SchemaRegistry", "NodeType"]]
            
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"   📁 {label}: {count}")
            
            # Count relationships
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result if record["relationshipType"] != "DEFINES"]
            
            for rel_type in rel_types:
                result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
                count = result.single()["count"]
                print(f"   🔗 {rel_type}: {count}")
    
    def close(self):
        """Close the Neo4j driver."""
        self.driver.close()

def main():
    print("🎯 Starting Flexible Payload Orchestrator...")
    
    orchestrator = FlexibleOrchestrator()
    
    try:
        # Check if PayloadsAllTheThings exists
        payloads_dir = "../PayloadsAllTheThings"
        if not Path(payloads_dir).exists():
            print(f"❌ PayloadsAllTheThings directory not found: {payloads_dir}")
            return False
        
        # Process payload files
        stats = orchestrator.scan_and_ingest_payloads(payloads_dir, limit=20)  # Start with 20 files
        
        print(f"\n📊 Processing Results:")
        print(f"   📝 Processed: {stats['processed']} files")
        print(f"   ✅ Success: {stats['success']} files")
        print(f"   ❌ Failed: {stats['failed']} files")
        
        # Show summary
        orchestrator.show_ingestion_summary()
        
        print("\n✅ Flexible orchestration completed!")
        print("🎯 Database now contains dynamically ingested payload data!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        orchestrator.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)