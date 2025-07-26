#!/usr/bin/env python3
"""
UCO Schema Loader - Load UCO ontology constraints and structure into Neo4j.
"""

from neo4j import GraphDatabase
from pathlib import Path
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import sys
from typing import Dict, List, Set
import re

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"

# UCO namespaces
UCO_CORE = Namespace("https://ontology.unifiedcyberontology.org/uco/core/")
UCO_ACTION = Namespace("https://ontology.unifiedcyberontology.org/uco/action/")
UCO_OBSERVABLE = Namespace("https://ontology.unifiedcyberontology.org/uco/observable/")
UCO_TOOL = Namespace("https://ontology.unifiedcyberontology.org/uco/tool/")
UCO_IDENTITY = Namespace("https://ontology.unifiedcyberontology.org/uco/identity/")
UCO_LOCATION = Namespace("https://ontology.unifiedcyberontology.org/uco/location/")

class UCOSchemaLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.ontology_path = Path("ontology/uco")
        self.classes = set()
        self.properties = set()
        
    def load_ontology_files(self) -> Dict[str, Graph]:
        """Load all UCO TTL files into RDFLib graphs."""
        graphs = {}
        
        ttl_files = [
            "core/core.ttl",
            "action/action.ttl", 
            "observable/observable.ttl",
            "tool/tool.ttl",
            "identity/identity.ttl",
            "location/location.ttl"
        ]
        
        for ttl_file in ttl_files:
            file_path = self.ontology_path / ttl_file
            if file_path.exists():
                print(f"📚 Loading {ttl_file}...")
                g = Graph()
                g.parse(file_path, format="turtle")
                graphs[ttl_file] = g
                print(f"   ✅ Loaded {len(g)} triples")
            else:
                print(f"   ⚠️  File not found: {file_path}")
                
        return graphs
    
    def extract_classes_and_properties(self, graphs: Dict[str, Graph]):
        """Extract UCO classes and properties from the ontology."""
        for file_name, graph in graphs.items():
            print(f"🔍 Analyzing {file_name}...")
            
            # Extract classes
            for subj, pred, obj in graph.triples((None, RDF.type, OWL.Class)):
                class_name = self.extract_local_name(str(subj))
                if class_name:
                    self.classes.add(class_name)
                    
            # Extract properties  
            for subj, pred, obj in graph.triples((None, RDF.type, OWL.ObjectProperty)):
                prop_name = self.extract_local_name(str(subj))
                if prop_name:
                    self.properties.add(prop_name)
                    
            for subj, pred, obj in graph.triples((None, RDF.type, OWL.DatatypeProperty)):
                prop_name = self.extract_local_name(str(subj))
                if prop_name:
                    self.properties.add(prop_name)
                    
        print(f"📊 Found {len(self.classes)} UCO classes")
        print(f"📊 Found {len(self.properties)} UCO properties")
    
    def extract_local_name(self, uri: str) -> str:
        """Extract the local name from a UCO URI."""
        if "unifiedcyberontology.org/uco/" in uri:
            # Extract the part after the last '/' or ':'
            return uri.split('/')[-1].split(':')[-1]
        return None
    
    def create_constraints(self):
        """Create Neo4j constraints for UCO classes."""
        print("🔧 Creating UCO constraints...")
        
        constraints = [
            # Core UCO constraints
            "CREATE CONSTRAINT uco_object_id FOR (o:UcoObject) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT uco_item_id FOR (i:Item) REQUIRE i.id IS UNIQUE", 
            "CREATE CONSTRAINT uco_action_id FOR (a:Action) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT uco_identity_id FOR (i:Identity) REQUIRE i.id IS UNIQUE",
            
            # Observable constraints
            "CREATE CONSTRAINT observable_object_id FOR (o:ObservableObject) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT file_id FOR (f:File) REQUIRE f.id IS UNIQUE",
            
            # Tool constraints  
            "CREATE CONSTRAINT tool_id FOR (t:Tool) REQUIRE t.id IS UNIQUE",
        ]
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"   ✅ Created: {constraint.split('FOR')[0].split('CONSTRAINT')[1].strip()}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"   ⚠️  Already exists: {constraint.split('FOR')[0].split('CONSTRAINT')[1].strip()}")
                    else:
                        print(f"   ❌ Failed: {e}")
    
    def create_indexes(self):
        """Create performance indexes for UCO properties."""
        print("🔧 Creating UCO indexes...")
        
        indexes = [
            "CREATE INDEX uco_object_name FOR (o:UcoObject) ON (o.name)",
            "CREATE INDEX uco_object_description FOR (o:UcoObject) ON (o.description)",
            "CREATE INDEX action_start_time FOR (a:Action) ON (a.startTime)",
            "CREATE INDEX action_end_time FOR (a:Action) ON (a.endTime)",
            "CREATE INDEX observable_hash FOR (o:ObservableObject) ON (o.hash)",
            "CREATE INDEX file_name FOR (f:File) ON (f.name)",
            "CREATE INDEX tool_name FOR (t:Tool) ON (t.name)",
        ]
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for index in indexes:
                try:
                    session.run(index)
                    print(f"   ✅ Created: {index.split('FOR')[0].split('INDEX')[1].strip()}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"   ⚠️  Already exists: {index.split('FOR')[0].split('INDEX')[1].strip()}")
                    else:
                        print(f"   ❌ Failed: {e}")
    
    def load_sample_uco_data(self):
        """Load a sample UCO structure to verify schema."""
        print("📝 Loading sample UCO data...")
        
        cypher = """
        // Create sample UCO objects following the ontology
        CREATE (bundle:Bundle:UcoObject {
            id: 'example-bundle-001',
            name: 'Sample UCO Bundle',
            description: 'Sample bundle for testing UCO schema'
        })
        
        CREATE (tool:Tool:UcoObject {
            id: 'example-tool-001', 
            name: 'Sample Security Tool',
            description: 'Example tool for demonstration'
        })
        
        CREATE (action:Action:UcoObject {
            id: 'example-action-001',
            name: 'Sample Security Action',
            description: 'Example action performed with tool',
            startTime: datetime()
        })
        
        CREATE (observable:ObservableObject:UcoObject {
            id: 'example-observable-001',
            name: 'Sample Observable',
            description: 'Example observable object'
        })
        
        // Create UCO relationships
        CREATE (action)-[:INSTRUMENT]->(tool)
        CREATE (action)-[:OBJECT]->(observable)
        CREATE (bundle)-[:ELEMENT]->(tool)
        CREATE (bundle)-[:ELEMENT]->(action)
        CREATE (bundle)-[:ELEMENT]->(observable)
        
        RETURN bundle, tool, action, observable
        """
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            try:
                result = session.run(cypher)
                count = len(list(result))
                print(f"   ✅ Created {count} sample UCO objects")
            except Exception as e:
                print(f"   ❌ Failed to create sample data: {e}")
    
    def verify_schema(self):
        """Verify the UCO schema was loaded correctly."""
        print("🔍 Verifying UCO schema...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Check constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = list(result)
            print(f"   📋 Total constraints: {len(constraints)}")
            
            # Check indexes
            result = session.run("SHOW INDEXES")
            indexes = list(result)
            print(f"   📋 Total indexes: {len(indexes)}")
            
            # Check sample data
            result = session.run("MATCH (n:UcoObject) RETURN count(n) AS count")
            node_count = result.single()["count"]
            print(f"   📊 UCO objects created: {node_count}")
            
            # Check relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            rel_count = result.single()["count"]
            print(f"   📊 Relationships created: {rel_count}")
    
    def close(self):
        """Close the Neo4j driver."""
        self.driver.close()

def main():
    print("🚀 Starting UCO Schema Loading...")
    
    loader = UCOSchemaLoader()
    
    try:
        # Load ontology files
        graphs = loader.load_ontology_files()
        if not graphs:
            print("❌ No ontology files found!")
            return False
            
        # Extract classes and properties
        loader.extract_classes_and_properties(graphs)
        
        # Create constraints and indexes
        loader.create_constraints()
        loader.create_indexes()
        
        # Load sample data
        loader.load_sample_uco_data()
        
        # Verify everything worked
        loader.verify_schema()
        
        print("\n✅ UCO schema loading completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ UCO schema loading failed: {e}")
        return False
        
    finally:
        loader.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)