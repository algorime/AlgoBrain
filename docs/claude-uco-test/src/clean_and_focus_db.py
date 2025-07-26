#!/usr/bin/env python3
"""
Clean and Focus Database - Remove the enormous UCO ontology and keep only focused subset.
"""

from neo4j import GraphDatabase
import sys

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"

class DatabaseCleaner:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Keep only these focused UCO classes for payload work
        self.focused_classes = [
            # Core essentials
            "UcoObject", "Item", "Bundle", "Action", "Tool",
            
            # Observable objects for payloads
            "ObservableObject", "File", "Process", "Account", 
            "Software", "Application", "Directory",
            
            # Network-related
            "NetworkConnection", "URL", "IPAddress", "DomainName",
            
            # Identity
            "Identity", "Person", "Organization",
            
            # Security-specific
            "EmailMessage", "EmailAccount", "WindowsRegistryKey"
        ]
        
        # Key relationships we want to keep
        self.focused_relationships = [
            "SUBCLASS_OF", "INSTRUMENT", "OBJECT", "PERFORMER", 
            "RESULT", "ELEMENT", "HAS_FACET"
        ]

    def analyze_current_state(self):
        """Show what's currently in the database."""
        print("🔍 Analyzing current database state...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count all nodes
            result = session.run("MATCH (n) RETURN count(n) AS total")
            total_nodes = result.single()["total"]
            
            # Count all relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS total")
            total_rels = result.single()["total"]
            
            # Show labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            
            # Show relationship types
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result]
            
            print(f"   📊 Total nodes: {total_nodes:,}")
            print(f"   📊 Total relationships: {total_rels:,}")
            print(f"   📊 Node labels: {len(labels)}")
            print(f"   📊 Relationship types: {len(rel_types)}")
            
            return total_nodes, total_rels, labels, rel_types

    def backup_focused_data(self):
        """Backup the focused UCO classes we want to keep."""
        print("💾 Backing up focused UCO data...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Extract focused UCO class definitions
            focused_data = []
            
            for class_name in self.focused_classes:
                result = session.run(
                    """
                    MATCH (c:UCOClass {name: $name})
                    RETURN c.name as name, c.comment as comment, c.uri as uri
                    """,
                    name=class_name
                )
                record = result.single()
                if record:
                    focused_data.append({
                        'name': record['name'],
                        'comment': record['comment'], 
                        'uri': record['uri']
                    })
            
            print(f"   ✅ Backed up {len(focused_data)} focused UCO classes")
            return focused_data

    def clean_database(self):
        """Remove all existing data from the database."""
        print("🧹 Cleaning database completely...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Delete all relationships first
            result = session.run("MATCH ()-[r]->() DELETE r RETURN count(r) as deleted")
            deleted_rels = result.single()["deleted"]
            print(f"   🗑️  Deleted {deleted_rels:,} relationships")
            
            # Delete all nodes
            result = session.run("MATCH (n) DELETE n RETURN count(n) as deleted")
            deleted_nodes = result.single()["deleted"]
            print(f"   🗑️  Deleted {deleted_nodes:,} nodes")
            
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
            
            # Drop all indexes (except required ones)
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

    def create_focused_schema(self, focused_data):
        """Create a clean, focused schema with only what we need."""
        print("🏗️  Creating focused UCO schema...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Create focused UCO classes as both regular nodes and schema nodes
            for class_info in focused_data:
                # Create the UCO class definition node
                session.run(
                    """
                    CREATE (c:UCOClass {
                        name: $name,
                        comment: $comment,
                        uri: $uri,
                        type: 'FocusedClass'
                    })
                    """,
                    name=class_info['name'],
                    comment=class_info['comment'],
                    uri=class_info['uri']
                )
                print(f"      ✅ Created focused class: {class_info['name']}")
            
            # Create basic class hierarchy for key classes
            hierarchies = [
                ("Item", "UcoObject"),
                ("Bundle", "UcoObject"), 
                ("Action", "UcoObject"),
                ("Tool", "UcoObject"),
                ("ObservableObject", "UcoObject"),
                ("File", "ObservableObject"),
                ("Process", "ObservableObject"),
                ("Software", "ObservableObject"),
                ("Application", "Software"),
                ("Directory", "ObservableObject"),
                ("NetworkConnection", "ObservableObject"),
                ("URL", "ObservableObject"),
                ("IPAddress", "ObservableObject"),
                ("Account", "ObservableObject"),
                ("Identity", "UcoObject"),
                ("Person", "Identity"),
                ("Organization", "Identity")
            ]
            
            for subclass, superclass in hierarchies:
                if (subclass in self.focused_classes and 
                    superclass in self.focused_classes):
                    session.run(
                        """
                        MATCH (sub:UCOClass {name: $subclass})
                        MATCH (super:UCOClass {name: $superclass})
                        CREATE (sub)-[:SUBCLASS_OF]->(super)
                        """,
                        subclass=subclass,
                        superclass=superclass
                    )
            
            print(f"   ✅ Created {len(hierarchies)} class hierarchy relationships")

    def create_constraints_and_indexes(self):
        """Create essential constraints and indexes for the focused schema."""
        print("🔧 Creating focused constraints and indexes...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Essential constraints
            constraints = [
                "CREATE CONSTRAINT focused_uco_class_name FOR (c:UCOClass) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT payload_id FOR (p:Payload) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT exploit_id FOR (e:Exploit) REQUIRE e.id IS UNIQUE"
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
            
            # Essential indexes
            indexes = [
                "CREATE INDEX uco_class_name FOR (c:UCOClass) ON (c.name)",
                "CREATE INDEX payload_name FOR (p:Payload) ON (p.name)",
                "CREATE INDEX payload_category FOR (p:Payload) ON (p.category)"
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

    def verify_clean_state(self):
        """Verify the database is now clean and focused."""
        print("🔍 Verifying clean, focused state...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count focused UCO classes
            result = session.run("MATCH (c:UCOClass) RETURN count(c) AS count")
            uco_count = result.single()["count"]
            
            # Count total nodes
            result = session.run("MATCH (n) RETURN count(n) AS total")
            total_nodes = result.single()["total"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS total")
            total_rels = result.single()["total"]
            
            # Show labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            
            print(f"   📊 Focused UCO classes: {uco_count}")
            print(f"   📊 Total nodes: {total_nodes}")
            print(f"   📊 Total relationships: {total_rels}")
            print(f"   📊 Node labels: {labels}")
            
            # Show some example classes
            result = session.run("MATCH (c:UCOClass) RETURN c.name ORDER BY c.name LIMIT 10")
            example_classes = [record["c.name"] for record in result]
            print(f"   📝 Available UCO classes: {', '.join(example_classes)}")

    def close(self):
        """Close the Neo4j driver."""
        self.driver.close()

def main():
    print("🧹 Starting Database Cleanup and Focus...")
    
    cleaner = DatabaseCleaner()
    
    try:
        # Show current state
        total_nodes, total_rels, labels, rel_types = cleaner.analyze_current_state()
        
        if total_nodes > 1000:
            print(f"\n⚠️  Database is large ({total_nodes:,} nodes). Proceeding with cleanup...")
            
            # Backup focused data before cleaning
            focused_data = cleaner.backup_focused_data()
            
            # Clean everything
            cleaner.clean_database()
            
            # Recreate focused schema
            cleaner.create_focused_schema(focused_data)
            
            # Add constraints and indexes
            cleaner.create_constraints_and_indexes()
            
            # Verify results
            cleaner.verify_clean_state()
            
            print("\n✅ Database cleanup and focus completed!")
            print("🎯 Ready for PayloadsAllTheThings integration with focused UCO subset!")
        else:
            print(f"\n✅ Database is already clean ({total_nodes} nodes)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        cleaner.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)