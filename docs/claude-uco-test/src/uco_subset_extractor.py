#!/usr/bin/env python3
"""
UCO Subset Extractor - Extract only relevant UCO classes for PayloadsAllTheThings integration.
"""

from neo4j import GraphDatabase
import sys

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"

class UCOSubsetExtractor:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Relevant UCO classes for cybersecurity payloads
        self.relevant_classes = [
            # Core UCO classes
            "UcoObject", "Item", "Bundle",
            
            # Tools and Actions
            "Tool", "Action", "AnalyticTool", 
            
            # Observable Objects (most important for payloads)
            "ObservableObject", "File", "Process", "Account", 
            "Software", "Application", "OperatingSystem",
            "NetworkConnection", "URL", "IPAddress", "DomainName",
            "EmailMessage", "EmailAccount", "MobileDevice",
            "WindowsRegistryKey", "WindowsRegistryValue",
            "Directory", "Archive", "CompressedStream",
            
            # Identity and Location
            "Identity", "Person", "Organization", "Location",
            
            # Security-specific observables
            "X509Certificate", "DigitalSignatureInfo",
            "Vulnerability", "CVE", "AttackPattern",
            "Malware", "ThreatActor"
        ]
        
        # Key relationships for payload analysis
        self.relevant_relationships = [
            "SUBCLASS_OF", "HAS_DOMAIN", "HAS_RANGE",
            "INSTRUMENT", "OBJECT", "PERFORMER", "RESULT",
            "ELEMENT", "CHILD", "PARENT"
        ]

    def analyze_current_db(self):
        """Analyze what's currently in the database."""
        print("🔍 Analyzing current UCO database...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count all node labels
            result = session.run("CALL db.labels()")
            all_labels = [record["label"] for record in result]
            print(f"   📊 Total node labels: {len(all_labels)}")
            
            # Count all relationship types
            result = session.run("CALL db.relationshipTypes()")
            all_rels = [record["relationshipType"] for record in result]
            print(f"   📊 Total relationship types: {len(all_rels)}")
            
            # Count UCO classes vs other nodes
            result = session.run("MATCH (c:UCOClass) RETURN count(c) AS count")
            uco_class_count = result.single()["count"]
            
            result = session.run("MATCH (p:UCOProperty) RETURN count(p) AS count") 
            uco_prop_count = result.single()["count"]
            
            print(f"   📊 UCO Classes: {uco_class_count}")
            print(f"   📊 UCO Properties: {uco_prop_count}")
            print(f"   📊 Other nodes: {len(all_labels) - 2}")  # Minus UCOClass and UCOProperty

    def find_relevant_uco_classes(self):
        """Find which of our relevant classes actually exist in UCO."""
        print("🎯 Finding relevant UCO classes for payloads...")
        
        found_classes = []
        missing_classes = []
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for class_name in self.relevant_classes:
                result = session.run(
                    "MATCH (c:UCOClass {name: $name}) RETURN c.name, c.comment",
                    name=class_name
                )
                record = result.single()
                
                if record:
                    found_classes.append({
                        'name': record['c.name'],
                        'comment': record['c.comment']
                    })
                else:
                    missing_classes.append(class_name)
        
        print(f"   ✅ Found {len(found_classes)} relevant UCO classes")
        print(f"   ❌ Missing {len(missing_classes)} classes")
        
        if missing_classes:
            print(f"   📝 Missing classes: {', '.join(missing_classes[:10])}")
        
        return found_classes, missing_classes

    def extract_payload_relevant_subset(self):
        """Extract a focused subset for payload analysis."""
        print("🎯 Extracting payload-relevant UCO subset...")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Create a new database/schema for the subset
            cypher = """
            // Create a focused view for payload analysis
            MATCH (c:UCOClass) 
            WHERE c.name IN $relevant_classes
            WITH collect(c) as relevant_nodes
            
            // Get their hierarchies
            MATCH (sub:UCOClass)-[:SUBCLASS_OF*]->(super:UCOClass)
            WHERE sub IN relevant_nodes OR super IN relevant_nodes
            
            RETURN sub.name as subclass, super.name as superclass, 
                   sub.comment as sub_comment, super.comment as super_comment
            ORDER BY superclass, subclass
            """
            
            result = session.run(cypher, relevant_classes=self.relevant_classes)
            hierarchies = list(result)
            
            print(f"   📊 Found {len(hierarchies)} relevant class hierarchies")
            
            return hierarchies

    def create_focused_payload_schema(self):
        """Create a new, focused schema for payload analysis."""
        print("🏗️  Creating focused payload schema...")
        
        # Clear any existing payload-specific nodes
        with self.driver.session(database=NEO4J_DATABASE) as session:
            session.run("MATCH (n:PayloadRelevant) DETACH DELETE n")
            
            # Create focused payload-relevant nodes
            for class_name in self.relevant_classes:
                result = session.run(
                    """
                    MATCH (c:UCOClass {name: $name})
                    CREATE (p:PayloadRelevant:UCOFocused {
                        name: c.name,
                        comment: c.comment,
                        uri: c.uri,
                        type: 'Class',
                        category: CASE 
                            WHEN c.name IN ['Tool', 'AnalyticTool'] THEN 'Tool'
                            WHEN c.name IN ['Action'] THEN 'Action' 
                            WHEN c.name IN ['File', 'Process', 'Software', 'Application'] THEN 'Observable'
                            WHEN c.name IN ['NetworkConnection', 'URL', 'IPAddress'] THEN 'Network'
                            WHEN c.name IN ['Account', 'Person', 'Identity'] THEN 'Identity'
                            ELSE 'Core'
                        END
                    })
                    RETURN p
                    """,
                    name=class_name
                )
                
                if result.single():
                    print(f"      ✅ Created focused node for: {class_name}")

    def create_payload_mapping_guide(self):
        """Create a guide for mapping PayloadsAllTheThings to UCO."""
        print("📋 Creating PayloadsAllTheThings -> UCO mapping guide...")
        
        mapping_guide = {
            "SQL Injection": {
                "uco_class": "Tool",
                "observable": "WebApplication", 
                "action": "ExploitVulnerability",
                "target": "Database"
            },
            "XSS": {
                "uco_class": "Tool",
                "observable": "WebApplication",
                "action": "InjectScript", 
                "target": "Browser"
            },
            "File Upload": {
                "uco_class": "Tool",
                "observable": "File",
                "action": "UploadMaliciousFile",
                "target": "WebServer"
            },
            "Command Injection": {
                "uco_class": "Tool", 
                "observable": "Process",
                "action": "ExecuteCommand",
                "target": "OperatingSystem"
            },
            "Directory Traversal": {
                "uco_class": "Tool",
                "observable": "Directory", 
                "action": "TraverseFileSystem",
                "target": "FileSystem"
            }
        }
        
        for category, mapping in mapping_guide.items():
            print(f"   📝 {category}:")
            print(f"      Tool Type: {mapping['uco_class']}")
            print(f"      Target Observable: {mapping['observable']}")
            print(f"      Action: {mapping['action']}")

    def show_focused_summary(self):
        """Show a summary of the focused schema."""
        print("📊 Focused UCO Schema Summary:")
        
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(
                """
                MATCH (p:PayloadRelevant)
                RETURN p.category as category, count(p) as count
                ORDER BY count DESC
                """
            )
            
            categories = list(result)
            for category in categories:
                print(f"   📁 {category['category']}: {category['count']} classes")
            
            # Show total
            result = session.run("MATCH (p:PayloadRelevant) RETURN count(p) as total")
            total = result.single()["total"]
            print(f"   🎯 Total focused classes: {total} (vs 1,177 original)")

    def close(self):
        """Close the Neo4j driver."""
        self.driver.close()

def main():
    print("🎯 Extracting Focused UCO Subset for PayloadsAllTheThings...")
    
    extractor = UCOSubsetExtractor()
    
    try:
        # Analyze current state
        extractor.analyze_current_db()
        
        # Find relevant classes
        found, missing = extractor.find_relevant_uco_classes()
        
        # Extract subset
        hierarchies = extractor.extract_payload_relevant_subset()
        
        # Create focused schema
        extractor.create_focused_payload_schema()
        
        # Create mapping guide
        extractor.create_payload_mapping_guide()
        
        # Show summary
        extractor.show_focused_summary()
        
        print("\n✅ Focused UCO subset extraction completed!")
        print("🎯 Now you have a manageable subset for payload integration!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        extractor.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)