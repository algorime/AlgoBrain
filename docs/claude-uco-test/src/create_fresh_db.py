#!/usr/bin/env python3
"""
Create Fresh Database - Clean existing database and start fresh for dynamic payload ingestion.
"""

from neo4j import GraphDatabase
import sys

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"  # Use existing database

class FreshDatabaseCreator:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
    def clean_existing_database(self):
        """Clean existing database completely."""
        print("🧹 Cleaning existing database completely...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Delete all relationships first
            result = session.run("MATCH ()-[r]->() DELETE r RETURN count(r) as deleted")
            deleted_rels = result.single()["deleted"]
            print(f"   🗑️  Deleted {deleted_rels} relationships")
            
            # Delete all nodes
            result = session.run("MATCH (n) DELETE n RETURN count(n) as deleted")
            deleted_nodes = result.single()["deleted"]
            print(f"   🗑️  Deleted {deleted_nodes} nodes")
            
            # Drop all constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = list(result)
            for constraint in constraints:
                constraint_name = constraint.get("name")
                if constraint_name:
                    try:
                        session.run(f"DROP CONSTRAINT {constraint_name}")
                        print(f"   🗑️  Dropped constraint: {constraint_name}")
                    except Exception as e:
                        print(f"   ⚠️  Could not drop constraint {constraint_name}: {e}")
            
            # Drop all indexes (except system ones)
            result = session.run("SHOW INDEXES")
            indexes = list(result)
            for index in indexes:
                index_name = index.get("name")
                if index_name and not index_name.startswith("system_"):
                    try:
                        session.run(f"DROP INDEX {index_name}")
                        print(f"   🗑️  Dropped index: {index_name}")
                    except Exception as e:
                        print(f"   ⚠️  Could not drop index {index_name}: {e}")
        
        return True
    
    def create_minimal_schema(self):
        """Create only the most basic schema needed for dynamic ingestion."""
        print("🏗️  Creating minimal base schema...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Basic constraints for core node types
            constraints = [
                "CREATE CONSTRAINT payload_id FOR (p:Payload) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT technique_id FOR (t:Technique) REQUIRE t.id IS UNIQUE", 
                "CREATE CONSTRAINT category_name FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT source_path FOR (s:Source) REQUIRE s.path IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    constraint_name = constraint.split("CONSTRAINT")[1].split("FOR")[0].strip()
                    print(f"   ✅ Created constraint: {constraint_name}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"   ⚠️  Constraint already exists")
                    else:
                        print(f"   ❌ Failed to create constraint: {e}")
            
            # Basic indexes for performance
            indexes = [
                "CREATE INDEX payload_name FOR (p:Payload) ON (p.name)",
                "CREATE INDEX technique_name FOR (t:Technique) ON (t.name)",
                "CREATE INDEX category_name_idx FOR (c:Category) ON (c.name)",
                "CREATE INDEX source_type FOR (s:Source) ON (s.type)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    index_name = index.split("INDEX")[1].split("FOR")[0].strip()
                    print(f"   ✅ Created index: {index_name}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"   ⚠️  Index already exists")
                    else:
                        print(f"   ❌ Failed to create index: {e}")
    
    def create_schema_registry(self):
        """Create a registry to track dynamically created schema elements."""
        print("📋 Creating schema registry...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Create schema registry nodes
            cypher = """
            // Create schema registry to track dynamic schema
            CREATE (registry:SchemaRegistry {
                name: 'PayloadKnowledgeGraph',
                version: '1.0.0',
                created: datetime(),
                description: 'Dynamic schema registry for payload knowledge graph'
            })
            
            // Create base node type definitions
            CREATE (payload_type:NodeType {
                name: 'Payload',
                description: 'Security payload or exploit code',
                category: 'core',
                dynamic: true
            })
            
            CREATE (technique_type:NodeType {
                name: 'Technique', 
                description: 'Attack technique or method',
                category: 'core',
                dynamic: true
            })
            
            CREATE (category_type:NodeType {
                name: 'Category',
                description: 'Payload category grouping',
                category: 'taxonomy',
                dynamic: true
            })
            
            CREATE (source_type:NodeType {
                name: 'Source',
                description: 'Source file or repository',
                category: 'metadata', 
                dynamic: true
            })
            
            // Link to registry
            CREATE (registry)-[:DEFINES]->(payload_type)
            CREATE (registry)-[:DEFINES]->(technique_type)
            CREATE (registry)-[:DEFINES]->(category_type)
            CREATE (registry)-[:DEFINES]->(source_type)
            
            RETURN registry, payload_type, technique_type, category_type, source_type
            """
            
            try:
                result = session.run(cypher)
                count = len(list(result))
                print(f"   ✅ Created schema registry with {count} base node types")
            except Exception as e:
                print(f"   ❌ Failed to create schema registry: {e}")
    
    def verify_fresh_database(self):
        """Verify the database is ready for dynamic ingestion."""
        print("🔍 Verifying fresh database state...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count total nodes
            result = session.run("MATCH (n) RETURN count(n) AS total")
            total_nodes = result.single()["total"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS total") 
            total_rels = result.single()["total"]
            
            # Show labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            
            # Show relationship types
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result]
            
            print(f"   📊 Total nodes: {total_nodes}")
            print(f"   📊 Total relationships: {total_rels}")
            print(f"   📊 Node labels: {labels}")
            print(f"   📊 Relationship types: {rel_types}")
            
            # Show schema registry
            result = session.run("MATCH (r:SchemaRegistry) RETURN r.name, r.version")
            registry = result.single()
            if registry:
                print(f"   📋 Schema registry: {registry['r.name']} v{registry['r.version']}")
            
            return total_nodes < 10  # Should be minimal
    
    def close(self):
        """Close the Neo4j driver."""
        self.driver.close()

def main():
    print("🆕 Creating Fresh Database for Dynamic Payload Ingestion...")
    
    creator = FreshDatabaseCreator()
    
    try:
        # Clean existing database
        if not creator.clean_existing_database():
            print("❌ Failed to clean database!")
            return False
        
        # Create minimal schema
        creator.create_minimal_schema()
        
        # Create schema registry
        creator.create_schema_registry()
        
        # Verify results
        if creator.verify_fresh_database():
            print("\n✅ Fresh database created successfully!")
            print("🎯 Ready for dynamic payload ingestion with flexible schema!")
            print(f"🔗 Database: {NEO4J_DATABASE}")
            print("📋 Schema registry enabled for dynamic node/relationship creation")
        else:
            print("\n⚠️  Database created but may not be optimal")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        creator.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)