#!/usr/bin/env python3
"""
Comprehensive UCO Ontology Loader - Load the complete UCO class hierarchy and relationships.
"""

from neo4j import GraphDatabase
from pathlib import Path
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import sys
from typing import Dict, List, Set, Tuple
import re

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"

class ComprehensiveUCOLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.ontology_path = Path("ontology/uco")
        self.unified_graph = Graph()
        self.uco_classes = {}  # URI -> local_name
        self.uco_properties = {}  # URI -> local_name  
        self.class_hierarchy = []  # (subclass, superclass) pairs
        self.property_domains = []  # (property, domain_class) pairs
        self.property_ranges = []   # (property, range_class) pairs
        
    def load_all_ontology_files(self):
        """Load all UCO TTL files into a unified graph."""
        print("📚 Loading complete UCO ontology...")
        
        ttl_files = [
            "master/uco.ttl",
            "core/core.ttl",
            "action/action.ttl", 
            "observable/observable.ttl",
            "tool/tool.ttl",
            "identity/identity.ttl",
            "location/location.ttl",
            "types/types.ttl",
            "vocabulary/vocabulary.ttl",
            "pattern/pattern.ttl",
            "marking/marking.ttl",
            "time/time.ttl",
            "analysis/analysis.ttl",
            "configuration/configuration.ttl",
            "role/role.ttl",
            "victim/victim.ttl"
        ]
        
        total_triples = 0
        for ttl_file in ttl_files:
            file_path = self.ontology_path / ttl_file
            if file_path.exists():
                print(f"   📖 Loading {ttl_file}...")
                try:
                    self.unified_graph.parse(file_path, format="turtle")
                    file_triples = len(self.unified_graph) - total_triples
                    total_triples = len(self.unified_graph)
                    print(f"      ✅ Added {file_triples} triples")
                except Exception as e:
                    print(f"      ❌ Error loading {ttl_file}: {e}")
            else:
                print(f"      ⚠️  File not found: {ttl_file}")
                
        print(f"📊 Total triples loaded: {total_triples}")
        return total_triples > 0
    
    def extract_uco_classes(self):
        """Extract all UCO classes and their hierarchy."""
        print("🔍 Extracting UCO classes...")
        
        # Find all OWL classes in UCO namespaces
        for subj, pred, obj in self.unified_graph.triples((None, RDF.type, OWL.Class)):
            uri_str = str(subj)
            if "unifiedcyberontology.org/uco/" in uri_str:
                local_name = self.extract_local_name(uri_str)
                if local_name:
                    self.uco_classes[uri_str] = local_name
        
        # Extract subclass relationships
        for subj, pred, obj in self.unified_graph.triples((None, RDFS.subClassOf, None)):
            subj_str = str(subj)
            obj_str = str(obj)
            
            if ("unifiedcyberontology.org/uco/" in subj_str and 
                "unifiedcyberontology.org/uco/" in obj_str):
                
                subclass = self.extract_local_name(subj_str)
                superclass = self.extract_local_name(obj_str)
                
                if subclass and superclass:
                    self.class_hierarchy.append((subclass, superclass))
        
        print(f"   📊 Found {len(self.uco_classes)} UCO classes")
        print(f"   📊 Found {len(self.class_hierarchy)} inheritance relationships")
    
    def extract_uco_properties(self):
        """Extract all UCO properties and their domains/ranges."""
        print("🔍 Extracting UCO properties...")
        
        # Find object properties
        for subj, pred, obj in self.unified_graph.triples((None, RDF.type, OWL.ObjectProperty)):
            uri_str = str(subj)
            if "unifiedcyberontology.org/uco/" in uri_str:
                local_name = self.extract_local_name(uri_str)
                if local_name:
                    self.uco_properties[uri_str] = local_name
        
        # Find datatype properties  
        for subj, pred, obj in self.unified_graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            uri_str = str(subj)
            if "unifiedcyberontology.org/uco/" in uri_str:
                local_name = self.extract_local_name(uri_str)
                if local_name:
                    self.uco_properties[uri_str] = local_name
        
        # Extract property domains
        for subj, pred, obj in self.unified_graph.triples((None, RDFS.domain, None)):
            prop_str = str(subj)
            domain_str = str(obj)
            
            if ("unifiedcyberontology.org/uco/" in prop_str and 
                "unifiedcyberontology.org/uco/" in domain_str):
                
                prop_name = self.extract_local_name(prop_str)
                domain_name = self.extract_local_name(domain_str)
                
                if prop_name and domain_name:
                    self.property_domains.append((prop_name, domain_name))
        
        # Extract property ranges
        for subj, pred, obj in self.unified_graph.triples((None, RDFS.range, None)):
            prop_str = str(subj)
            range_str = str(obj)
            
            if ("unifiedcyberontology.org/uco/" in prop_str and 
                "unifiedcyberontology.org/uco/" in range_str):
                
                prop_name = self.extract_local_name(prop_str)
                range_name = self.extract_local_name(range_str)
                
                if prop_name and range_name:
                    self.property_ranges.append((prop_name, range_name))
        
        print(f"   📊 Found {len(self.uco_properties)} UCO properties")
        print(f"   📊 Found {len(self.property_domains)} property domain relationships")
        print(f"   📊 Found {len(self.property_ranges)} property range relationships")
    
    def extract_local_name(self, uri: str) -> str:
        """Extract the local name from a UCO URI."""
        if "unifiedcyberontology.org/uco/" in uri:
            # Extract the part after the last '/' or '#'
            if '#' in uri:
                return uri.split('#')[-1]
            else:
                return uri.split('/')[-1]
        return None
    
    def create_uco_class_nodes(self):
        """Create nodes for all UCO classes."""
        print("🏗️  Creating UCO class nodes...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Create UCO Class nodes
            for uri, local_name in self.uco_classes.items():
                # Get rdfs:label and rdfs:comment if available
                label_query = f"<{uri}> rdfs:label ?label"
                comment_query = f"<{uri}> rdfs:comment ?comment"
                
                label = None
                comment = None
                
                # Try to get label and comment from the graph
                for subj, pred, obj in self.unified_graph.triples((URIRef(uri), RDFS.label, None)):
                    label = str(obj)
                    break
                    
                for subj, pred, obj in self.unified_graph.triples((URIRef(uri), RDFS.comment, None)):
                    comment = str(obj)
                    break
                
                cypher = f"""
                MERGE (c:UCOClass {{uri: $uri, name: $name}})
                SET c.label = $label,
                    c.comment = $comment,
                    c.type = 'Class'
                """
                
                try:
                    session.run(cypher, uri=uri, name=local_name, label=label, comment=comment)
                except Exception as e:
                    print(f"      ❌ Error creating class {local_name}: {e}")
        
        print(f"   ✅ Created {len(self.uco_classes)} UCO class nodes")
    
    def create_uco_property_nodes(self):
        """Create nodes for all UCO properties."""
        print("🏗️  Creating UCO property nodes...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for uri, local_name in self.uco_properties.items():
                # Get rdfs:label and rdfs:comment if available
                label = None
                comment = None
                
                for subj, pred, obj in self.unified_graph.triples((URIRef(uri), RDFS.label, None)):
                    label = str(obj)
                    break
                    
                for subj, pred, obj in self.unified_graph.triples((URIRef(uri), RDFS.comment, None)):
                    comment = str(obj)
                    break
                
                cypher = f"""
                MERGE (p:UCOProperty {{uri: $uri, name: $name}})
                SET p.label = $label,
                    p.comment = $comment,
                    p.type = 'Property'
                """
                
                try:
                    session.run(cypher, uri=uri, name=local_name, label=label, comment=comment)
                except Exception as e:
                    print(f"      ❌ Error creating property {local_name}: {e}")
        
        print(f"   ✅ Created {len(self.uco_properties)} UCO property nodes")
    
    def create_class_hierarchy(self):
        """Create subclass relationships."""
        print("🔗 Creating UCO class hierarchy...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for subclass, superclass in self.class_hierarchy:
                cypher = """
                MATCH (sub:UCOClass {name: $subclass})
                MATCH (super:UCOClass {name: $superclass})
                MERGE (sub)-[:SUBCLASS_OF]->(super)
                """
                
                try:
                    session.run(cypher, subclass=subclass, superclass=superclass)
                except Exception as e:
                    print(f"      ❌ Error creating hierarchy {subclass} -> {superclass}: {e}")
        
        print(f"   ✅ Created {len(self.class_hierarchy)} subclass relationships")
    
    def create_property_relationships(self):
        """Create property domain and range relationships."""
        print("🔗 Creating property domain/range relationships...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Create domain relationships
            for prop_name, domain_name in self.property_domains:
                cypher = """
                MATCH (p:UCOProperty {name: $prop_name})
                MATCH (c:UCOClass {name: $domain_name})
                MERGE (p)-[:HAS_DOMAIN]->(c)
                """
                
                try:
                    session.run(cypher, prop_name=prop_name, domain_name=domain_name)
                except Exception as e:
                    print(f"      ❌ Error creating domain {prop_name} -> {domain_name}: {e}")
            
            # Create range relationships  
            for prop_name, range_name in self.property_ranges:
                cypher = """
                MATCH (p:UCOProperty {name: $prop_name})
                MATCH (c:UCOClass {name: $range_name})
                MERGE (p)-[:HAS_RANGE]->(c)
                """
                
                try:
                    session.run(cypher, prop_name=prop_name, range_name=range_name)
                except Exception as e:
                    print(f"      ❌ Error creating range {prop_name} -> {range_name}: {e}")
        
        print(f"   ✅ Created {len(self.property_domains)} domain relationships")
        print(f"   ✅ Created {len(self.property_ranges)} range relationships")
    
    def verify_uco_ontology(self):
        """Verify the complete UCO ontology was loaded."""
        print("🔍 Verifying complete UCO ontology...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count UCO classes
            result = session.run("MATCH (c:UCOClass) RETURN count(c) AS count")
            class_count = result.single()["count"]
            print(f"   📊 UCO Classes: {class_count}")
            
            # Count UCO properties
            result = session.run("MATCH (p:UCOProperty) RETURN count(p) AS count") 
            prop_count = result.single()["count"]
            print(f"   📊 UCO Properties: {prop_count}")
            
            # Count subclass relationships
            result = session.run("MATCH ()-[r:SUBCLASS_OF]->() RETURN count(r) AS count")
            subclass_count = result.single()["count"]
            print(f"   📊 Subclass relationships: {subclass_count}")
            
            # Count domain/range relationships
            result = session.run("MATCH ()-[r:HAS_DOMAIN|HAS_RANGE]->() RETURN count(r) AS count")
            prop_rel_count = result.single()["count"]
            print(f"   📊 Property relationships: {prop_rel_count}")
            
            # Show some example classes
            result = session.run("MATCH (c:UCOClass) RETURN c.name LIMIT 10")
            example_classes = [record["c.name"] for record in result]
            print(f"   📝 Example classes: {', '.join(example_classes)}")
    
    def close(self):
        """Close the Neo4j driver."""
        self.driver.close()

def main():
    print("🚀 Starting Comprehensive UCO Ontology Loading...")
    
    loader = ComprehensiveUCOLoader()
    
    try:
        # Load all ontology files
        if not loader.load_all_ontology_files():
            print("❌ Failed to load ontology files!")
            return False
        
        # Extract classes and properties
        loader.extract_uco_classes()
        loader.extract_uco_properties()
        
        # Create the ontology structure in Neo4j
        loader.create_uco_class_nodes()
        loader.create_uco_property_nodes()
        loader.create_class_hierarchy()
        loader.create_property_relationships()
        
        # Verify the results
        loader.verify_uco_ontology()
        
        print("\n✅ Complete UCO ontology loading successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ UCO ontology loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        loader.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)