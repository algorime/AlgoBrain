#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
State-of-the-Art MITRE ATT&CK Knowledge Graph Importer

This script implements a robust, production-ready ETL pipeline to build a
technique-centric knowledge graph from the MITRE ATT&CK framework. It is the
synthesis of a state-of-the-art survey on best practices for ATT&CK data
ingestion and graph schema design.

Key Features:
- Technique-Centric: Exclusively models ATT&CK techniques, tactics,
  mitigations, and data sources, deliberately omitting threat actors and
  campaigns.
- Rich Schema: Implements a powerful graph schema that models not just the
  structural hierarchy of ATT&CK, but also the critical relationships between
  techniques and their detection mechanisms (data sources and components).
- Production-Ready ETL:
    - Fetches the latest Enterprise ATT&CK STIX data directly from MITRE's source.
    - Uses a two-phase, batched import process for high performance and reliability.
    - Employs defensive parsing to handle potential variations in data format.
    - Provides clear logging and progress indicators.
"""

import os
import requests
from stix2 import MemoryStore
from neo4j import GraphDatabase
from collections import defaultdict

# --- Configuration ---
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

ATTACK_STIX_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json"

# Defines the specific STIX object types to be imported.
# This is the core of the "technique-centric" approach.
ALLOWED_TYPES = {
    "attack-pattern",       # Techniques and Sub-techniques
    "course-of-action",     # Mitigations
    "x-mitre-tactic",       # ATT&CK Tactics
    "x-mitre-data-source",
    "x-mitre-data-component",
    "relationship"          # The links between objects
}


class AttackMitreImporter:
    """
    A class to import MITRE ATT&CK data into a Neo4j graph database.
    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stix_data = None
        self.stix_objects = {}

    def fetch_stix_data(self):
        """Fetches the latest ATT&CK STIX data from the MITRE CTI repo."""
        print(f"Fetching STIX data from {ATTACK_STIX_URL}...")
        response = requests.get(ATTACK_STIX_URL)
        response.raise_for_status()
        self.stix_data = response.json()
        print("Successfully fetched STIX data.")

    def _load_stix_objects(self):
        """Loads STIX data into a MemoryStore and filters for allowed types."""
        print("Loading and filtering STIX objects...")
        ms = MemoryStore(stix_data=self.stix_data)
        for obj in ms.query():
            if obj.type in ALLOWED_TYPES:
                self.stix_objects[obj.id] = obj
        print(f"Loaded {len(self.stix_objects)} technique-centric STIX objects.")

    def import_to_neo4j(self):
        """Main method to run the full import process."""
        self.fetch_stix_data()
        self._load_stix_objects()
        self._clear_database()
        self._create_constraints()
        self._import_nodes_batched()
        self._import_relationships_batched()
        print("\\nImport process completed successfully!")

    def _clear_database(self):
        """Clears the existing graph from the database."""
        print("Clearing existing database...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared.")

    def _create_constraints(self):
        """Creates unique constraints on nodes for performance and data integrity."""
        print("Creating database constraints...")
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT ON (t:Tactic) ASSERT t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT ON (t:Technique) ASSERT t.id IS UNIQUE")
            session.run("CREATE CONSTRAINT ON (m:Mitigation) ASSERT m.id IS UNIQUE")
            session.run("CREATE CONSTRAINT ON (ds:DataSource) ASSERT ds.id IS UNIQUE")
            session.run("CREATE CONSTRAINT ON (dc:DataComponent) ASSERT dc.id IS UNIQUE")
        print("Constraints created.")

    def _import_nodes_batched(self):
        """Processes all STIX objects and imports them as nodes in batches."""
        print("Importing nodes in batches...")
        nodes_by_type = defaultdict(list)
        for obj in self.stix_objects.values():
            if obj.type != 'relationship':
                nodes_by_type[obj.type].append(obj)

        self._create_nodes_batch(nodes_by_type.get('x-mitre-tactic', []), self._tactic_props, "Tactic")
        self._create_nodes_batch(nodes_by_type.get('attack-pattern', []), self._technique_props, "Technique")
        self._create_nodes_batch(nodes_by_type.get('course-of-action', []), self._mitigation_props, "Mitigation")
        self._create_nodes_batch(nodes_by_type.get('x-mitre-data-source', []), self._data_source_props, "DataSource")
        self._create_nodes_batch(nodes_by_type.get('x-mitre-data-component', []), self._data_component_props, "DataComponent")
        print("Finished importing nodes.")

    def _create_nodes_batch(self, nodes, props_extractor, label):
        """Generic method to create nodes of a specific type in a single batch."""
        if not nodes:
            return
        props_list = [props_extractor(node) for node in nodes]
        
        query = f"""
        UNWIND $props_list AS props
        MERGE (n:{label} {{id: props.id}})
        SET n += props
        """
        with self.driver.session() as session:
            session.run(query, props_list=props_list)
        print(f"  Imported {len(props_list)} {label} nodes.")

    # --- Property Extractor Methods ---
    def _tactic_props(self, tactic):
        return {
            "id": tactic.name,
            "name": tactic.name,
            "shortname": tactic.x_mitre_shortname,
            "description": tactic.description or "",
            "url": tactic.external_references[0].url
        }

    def _technique_props(self, tech):
        external_id = next((e.external_id for e in tech.external_references if e.source_name == 'mitre-attack'), None)
        return {
            "id": external_id,
            "stix_id": tech.id,
            "name": tech.name,
            "description": tech.description or "",
            "url": next((e.url for e in tech.external_references if e.source_name == 'mitre-attack'), ""),
            "is_subtechnique": tech.get('x_mitre_is_subtechnique', False)
        }

    def _mitigation_props(self, mit):
        external_id = next((e.external_id for e in mit.external_references if e.source_name == 'mitre-attack'), None)
        return {
            "id": external_id,
            "stix_id": mit.id,
            "name": mit.name,
            "description": mit.description or ""
        }

    def _data_source_props(self, ds):
        external_id = next((e.external_id for e in ds.external_references if e.source_name == 'mitre-attack'), None)
        return {
            "id": external_id,
            "stix_id": ds.id,
            "name": ds.name,
            "description": ds.description or ""
        }

    def _data_component_props(self, dc):
        return {
            "id": dc.id,
            "name": dc.name,
            "description": dc.description or ""
        }

    def _import_relationships_batched(self):
        """Creates all relationships in batched transactions."""
        print("Importing relationships in batches...")
        relationships = [obj for obj in self.stix_objects.values() if obj.type == 'relationship']
        
        self._create_tactic_technique_rels_batch()
        self._create_detection_rels_batch()
        self._create_generic_rels_batch(relationships, 'mitigates', 'Technique', 'MITIGATED_BY', 'Mitigation')
        self._create_generic_rels_batch(relationships, 'subtechnique-of', 'Technique', 'HAS_SUBTECHNIQUE', 'Technique', reverse=True)
        print("Finished importing relationships.")

    def _create_tactic_technique_rels_batch(self):
        """Batches creation of HAS_TECHNIQUE relationships."""
        rels = []
        for tech in self.stix_objects.values():
            if tech.type == 'attack-pattern':
                tech_id = self._technique_props(tech)['id']
                for phase in tech.kill_chain_phases:
                    if phase.kill_chain_name == 'mitre-attack':
                        rels.append({"tactic_name": phase.phase_name, "tech_id": tech_id})
        
        query = """
        UNWIND $rels AS rel
        MATCH (t:Tactic {name: rel.tactic_name})
        MATCH (tech:Technique {id: rel.tech_id})
        MERGE (t)-[:HAS_TECHNIQUE]->(tech)
        """
        with self.driver.session() as session:
            session.run(query, rels=rels)
        print(f"  Imported {len(rels)} HAS_TECHNIQUE relationships.")

    def _create_detection_rels_batch(self):
        """Batches creation of DETECTED_BY and HAS_COMPONENT relationships."""
        rels = []
        for tech in self.stix_objects.values():
            if tech.type == 'attack-pattern' and tech.get('x_mitre_data_sources'):
                tech_id = self._technique_props(tech)['id']
                for ds_string in tech.get('x_mitre_data_sources'):
                    if ':' not in ds_string:
                        print(f"  [!] Warning: Skipping malformed data source string '{ds_string}' for technique {tech_id}")
                        continue
                    source_name, component_name = [part.strip() for part in ds_string.split(':', 1)]
                    
                    # Find the corresponding Data Source and Component STIX objects
                    ds_obj = next((ds for ds in self.stix_objects.values() if ds.type == 'x-mitre-data-source' and ds.name == source_name), None)
                    dc_obj = next((dc for dc in self.stix_objects.values() if dc.type == 'x-mitre-data-component' and dc.name == component_name), None)

                    if ds_obj and dc_obj:
                        rels.append({
                            "tech_id": tech_id,
                            "ds_id": self._data_source_props(ds_obj)['id'],
                            "dc_id": dc_obj.id
                        })

        query = """
        UNWIND $rels AS rel
        MATCH (tech:Technique {id: rel.tech_id})
        MATCH (ds:DataSource {id: rel.ds_id})
        MATCH (dc:DataComponent {id: rel.dc_id})
        MERGE (tech)-[:DETECTED_BY]->(dc)
        MERGE (ds)-[:HAS_COMPONENT]->(dc)
        """
        with self.driver.session() as session:
            session.run(query, rels=rels)
        print(f"  Imported {len(rels)} detection-related relationships.")

    def _create_generic_rels_batch(self, relationships, rel_type, source_label, rel_name, target_label, reverse=False):
        """Generic method to create relationships of a specific type in a single batch."""
        rels = []
        for rel in relationships:
            if rel.relationship_type == rel_type:
                source_obj = self.stix_objects.get(rel.source_ref)
                target_obj = self.stix_objects.get(rel.target_ref)
                if source_obj and target_obj:
                    source_id = self._get_node_id(source_obj)
                    target_id = self._get_node_id(target_obj)
                    if reverse:
                        source_id, target_id = target_id, source_id
                    rels.append({"source_id": source_id, "target_id": target_id})
        
        if not rels:
            return

        query = f"""
        UNWIND $rels AS rel
        MATCH (source:{source_label} {{id: rel.source_id}})
        MATCH (target:{target_label} {{id: rel.target_id}})
        MERGE (source)-[:{rel_name}]->(target)
        """
        with self.driver.session() as session:
            session.run(query, rels=rels)
        print(f"  Imported {len(rels)} {rel_name} relationships.")

    def _get_node_id(self, obj):
        """Helper to get the correct ID for a node based on its type."""
        if obj.type == 'attack-pattern':
            return self._technique_props(obj)['id']
        if obj.type == 'course-of-action':
            return self._mitigation_props(obj)['id']
        if obj.type == 'x-mitre-tactic':
            return self._tactic_props(obj)['id']
        if obj.type == 'x-mitre-data-source':
            return self._data_source_props(obj)['id']
        if obj.type == 'x-mitre-data-component':
            return self._data_component_props(obj)['id']
        return obj.id

    def close(self):
        """Closes the Neo4j driver connection."""
        self.driver.close()
        print("Neo4j driver connection closed.")


if __name__ == "__main__":
    importer = AttackMitreImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        importer.import_to_neo4j()
    finally:
        importer.close()