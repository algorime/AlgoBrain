"""
Comprehensive UCO Mapping for MITRE ATT&CK Enterprise and ICS Datasets
Implements unified schema based on Unified Cyber Ontology (UCO) specifications
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class UCOMapping:
    """Complete UCO mapping for all MITRE ATT&CK object types"""
    
    # Core UCO to MITRE mappings
    MITRE_TO_UCO_BASE_MAPPING = {
        # Core STIX Domain Objects
        'attack-pattern': 'uco-action:Action',
        'malware': 'uco-tool:Tool', 
        'intrusion-set': 'uco-identity:Identity',
        'course-of-action': 'uco-action:Action',  # Defensive action
        'campaign': 'uco-action:Action',          # Coordinated action
        'tool': 'uco-tool:Tool',
        'identity': 'uco-identity:Identity',
        'relationship': 'uco-core:Relationship',
        'marking-definition': 'uco-core:MarkingDefinition',
        
        # MITRE-specific objects
        'x-mitre-tactic': 'uco-action:ActionPattern',
        'x-mitre-matrix': 'uco-core:Collection',
        'x-mitre-collection': 'uco-core:Collection',
        'x-mitre-data-source': 'uco-observable:ObservablePattern',
        'x-mitre-data-component': 'uco-observable:ObservableObject',
        'x-mitre-asset': 'uco-core:UcoObject',  # ICS-specific asset
    }
    
    # UCO property mappings for each MITRE type
    PROPERTY_MAPPINGS = {
        'attack-pattern': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'external_references': 'uco-core:externalReference',
            'kill_chain_phases': 'uco-action:phase',
            'x_mitre_platforms': 'uco-action:environment',
            'x_mitre_data_sources': 'uco-action:instrument',
            'x_mitre_detection': 'uco-action:result',
            'x_mitre_is_subtechnique': 'uco-core:tag'
        },
        'malware': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'is_family': 'uco-tool:toolType',
            'x_mitre_platforms': 'uco-tool:environment',
            'x_mitre_aliases': 'uco-identity:alias'
        },
        'intrusion-set': {
            'id': 'uco-core:hasFacet.uco-core:identifier', 
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'aliases': 'uco-identity:alias'
        },
        'course-of-action': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name', 
            'description': 'uco-core:description',
            'labels': 'uco-core:tag'
        },
        'tool': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'x_mitre_platforms': 'uco-tool:environment',
            'x_mitre_aliases': 'uco-identity:alias'
        },
        'campaign': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'first_seen': 'uco-action:startTime',
            'last_seen': 'uco-action:endTime',
            'aliases': 'uco-identity:alias'
        },
        'x-mitre-tactic': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'x_mitre_shortname': 'uco-core:tag'
        },
        'x-mitre-asset': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'x_mitre_platforms': 'uco-core:environment',
            'x_mitre_sectors': 'uco-core:tag',
            'x_mitre_related_assets': 'uco-core:relationship'
        },
        'x-mitre-data-source': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'x_mitre_platforms': 'uco-observable:environment',
            'x_mitre_collection_layers': 'uco-observable:observableForm'
        },
        'x-mitre-data-component': {
            'id': 'uco-core:hasFacet.uco-core:identifier',
            'name': 'uco-core:name',
            'description': 'uco-core:description',
            'x_mitre_data_source_ref': 'uco-core:relationship'
        }
    }
    
    # Relationship type mappings to UCO
    RELATIONSHIP_MAPPINGS = {
        'uses': 'uco-action:instrument',
        'mitigates': 'uco-action:result',  # Mitigation is result of defensive action
        'detects': 'uco-observable:observes',
        'targets': 'uco-action:object',
        'attributed-to': 'uco-core:attribution',
        'subtechnique-of': 'uco-core:hasSubClass',
        'revoked-by': 'uco-core:hasState'
    }

@dataclass
class UCONode:
    """Represents a UCO-compliant node in the knowledge graph"""
    id: str
    uco_type: str
    mitre_type: str
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Dict[str, Any] = None
    source_dataset: str = None  # 'enterprise' or 'ics'
    mitre_id: Optional[str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class UCORelationship:
    """Represents a UCO-compliant relationship in the knowledge graph"""
    id: str
    source_ref: str
    target_ref: str
    relationship_type: str
    uco_relationship_type: str
    properties: Dict[str, Any] = None
    source_dataset: str = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

class MitreUCOConverter:
    """Converts MITRE ATT&CK objects to UCO-compliant format"""
    
    def __init__(self):
        self.mapping = UCOMapping()
        self.converted_nodes: Dict[str, UCONode] = {}
        self.converted_relationships: List[UCORelationship] = []
        
    def convert_mitre_object(self, mitre_obj: Dict[str, Any], source_dataset: str) -> Optional[UCONode]:
        """Convert a MITRE object to UCO format"""
        
        mitre_type = mitre_obj['type']
        
        if mitre_type not in self.mapping.MITRE_TO_UCO_BASE_MAPPING:
            print(f"Warning: No UCO mapping for type {mitre_type}")
            return None
        
        uco_type = self.mapping.MITRE_TO_UCO_BASE_MAPPING[mitre_type]
        
        # Extract MITRE ID from external references if available
        mitre_id = None
        if 'external_references' in mitre_obj:
            for ref in mitre_obj['external_references']:
                if ref.get('source_name') == 'mitre-attack':
                    mitre_id = ref.get('external_id')
                    break
        
        # Map properties
        mapped_properties = {}
        if mitre_type in self.mapping.PROPERTY_MAPPINGS:
            for mitre_prop, uco_prop in self.mapping.PROPERTY_MAPPINGS[mitre_type].items():
                if mitre_prop in mitre_obj:
                    mapped_properties[uco_prop] = mitre_obj[mitre_prop]
        
        # Add all original MITRE properties with mitre: prefix
        for key, value in mitre_obj.items():
            if key not in ['id', 'type', 'name', 'description']:
                mapped_properties[f'mitre:{key}'] = value
        
        node = UCONode(
            id=mitre_obj['id'],
            uco_type=uco_type,
            mitre_type=mitre_type,
            name=mitre_obj.get('name'),
            description=mitre_obj.get('description'),
            properties=mapped_properties,
            source_dataset=source_dataset,
            mitre_id=mitre_id
        )
        
        self.converted_nodes[node.id] = node
        return node
    
    def convert_mitre_relationship(self, mitre_rel: Dict[str, Any], source_dataset: str) -> Optional[UCORelationship]:
        """Convert a MITRE relationship to UCO format"""
        
        rel_type = mitre_rel['relationship_type']
        uco_rel_type = self.mapping.RELATIONSHIP_MAPPINGS.get(rel_type, 'uco-core:relationship')
        
        # Map relationship properties  
        mapped_properties = {}
        for key, value in mitre_rel.items():
            if key not in ['id', 'type', 'source_ref', 'target_ref', 'relationship_type']:
                mapped_properties[f'mitre:{key}'] = value
        
        relationship = UCORelationship(
            id=mitre_rel['id'],
            source_ref=mitre_rel['source_ref'],
            target_ref=mitre_rel['target_ref'],
            relationship_type=rel_type,
            uco_relationship_type=uco_rel_type,
            properties=mapped_properties,
            source_dataset=source_dataset
        )
        
        self.converted_relationships.append(relationship)
        return relationship
    
    def process_dataset(self, dataset_path: str, dataset_name: str) -> None:
        """Process entire MITRE dataset and convert to UCO"""
        
        import json
        with open(dataset_path) as f:
            data = json.load(f)
        
        print(f"Processing {dataset_name} dataset: {len(data['objects'])} objects")
        
        # First pass: convert all nodes
        for obj in data['objects']:
            if obj['type'] != 'relationship':
                self.convert_mitre_object(obj, dataset_name)
        
        # Second pass: convert all relationships
        for obj in data['objects']:
            if obj['type'] == 'relationship':
                self.convert_mitre_relationship(obj, dataset_name)
        
        print(f"Converted {len(self.converted_nodes)} nodes and {len(self.converted_relationships)} relationships")

    def get_cross_dataset_connections(self) -> List[UCORelationship]:
        """Identify potential connections between Enterprise and ICS datasets"""
        
        connections = []
        
        # Find common techniques by name/description similarity
        enterprise_techniques = {node.mitre_id: node for node in self.converted_nodes.values() 
                               if node.mitre_type == 'attack-pattern' and node.source_dataset == 'enterprise'}
        
        ics_techniques = {node.mitre_id: node for node in self.converted_nodes.values()
                         if node.mitre_type == 'attack-pattern' and node.source_dataset == 'ics'}
        
        # Create cross-references for similar techniques
        for ent_id, ent_node in enterprise_techniques.items():
            for ics_id, ics_node in ics_techniques.items():
                if ent_node.name and ics_node.name:
                    # Simple name similarity check
                    if ent_node.name.lower() in ics_node.name.lower() or ics_node.name.lower() in ent_node.name.lower():
                        connection = UCORelationship(
                            id=f"cross-ref-{ent_id}-{ics_id}",
                            source_ref=ent_node.id,
                            target_ref=ics_node.id,
                            relationship_type='related-to',
                            uco_relationship_type='uco-core:similarity',
                            properties={'similarity_basis': 'technique_name', 'confidence': 0.8},
                            source_dataset='cross-reference'
                        )
                        connections.append(connection)
        
        # Find common actors/groups between datasets
        enterprise_groups = {node.name: node for node in self.converted_nodes.values() 
                           if node.mitre_type == 'intrusion-set' and node.source_dataset == 'enterprise'}
        
        ics_groups = {node.name: node for node in self.converted_nodes.values()
                     if node.mitre_type == 'intrusion-set' and node.source_dataset == 'ics'}
        
        # Create connections for groups that appear in both datasets
        for group_name in set(enterprise_groups.keys()) & set(ics_groups.keys()):
            if group_name:
                connection = UCORelationship(
                    id=f"group-cross-ref-{group_name.replace(' ', '-')}",
                    source_ref=enterprise_groups[group_name].id,
                    target_ref=ics_groups[group_name].id,
                    relationship_type='same-as',
                    uco_relationship_type='uco-core:identity',
                    properties={'identity_basis': 'same_actor_group'},
                    source_dataset='cross-reference'
                )
                connections.append(connection)
        
        print(f"Generated {len(connections)} cross-dataset connections")
        return connections

if __name__ == "__main__":
    converter = MitreUCOConverter()
    
    # Process both datasets
    converter.process_dataset('enterprise-attack-17.1.json', 'enterprise')
    converter.process_dataset('ics-attack-17.1.json', 'ics')
    
    # Generate cross-dataset connections
    cross_connections = converter.get_cross_dataset_connections()
    converter.converted_relationships.extend(cross_connections)
    
    print(f"\nFinal Statistics:")
    print(f"Total UCO Nodes: {len(converter.converted_nodes)}")
    print(f"Total UCO Relationships: {len(converter.converted_relationships)}")
    
    # Show statistics by type
    node_types = {}
    for node in converter.converted_nodes.values():
        key = f"{node.uco_type} ({node.source_dataset})"
        node_types[key] = node_types.get(key, 0) + 1
    
    print("\nNode Distribution:")
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {node_type}: {count}")