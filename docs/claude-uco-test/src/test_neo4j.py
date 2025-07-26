#!/usr/bin/env python3
"""
Test script to verify Neo4j connectivity and basic operations.
"""

from neo4j import GraphDatabase
import sys

# Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ucosecure123"
NEO4J_DATABASE = "uco-graph"

def test_connection():
    """Test basic Neo4j connection."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("RETURN 'Neo4j is connected!' AS message")
            record = result.single()
            print(f"✅ Connection successful: {record['message']}")
            
            # Test database info
            result = session.run("CALL db.info()")
            info = result.single()
            print(f"✅ Database: {info['name']}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def check_uco_preparation():
    """Check if database is ready for UCO schema loading."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check existing constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]
            print(f"📋 Existing constraints: {len(constraints)}")
            
            # Check existing indexes  
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]
            print(f"📋 Existing indexes: {len(indexes)}")
            
            # Check node count
            result = session.run("MATCH (n) RETURN count(n) AS nodeCount")
            node_count = result.single()["nodeCount"]
            print(f"📊 Current nodes in database: {node_count}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Neo4j connectivity...")
    
    if test_connection():
        print("\n🔍 Checking database status...")
        check_uco_preparation()
        print("\n✅ Neo4j is ready for UCO schema loading!")
        sys.exit(0)
    else:
        print("\n❌ Please check Neo4j container and configuration.")
        sys.exit(1)