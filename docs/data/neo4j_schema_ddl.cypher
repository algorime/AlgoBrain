/* 
 * Comprehensive Neo4j Schema for MITRE ATT&CK Enterprise & ICS 
 * UCO-Compliant Knowledge Graph Implementation
 * 
 * This schema implements the Unified Cyber Ontology (UCO) as the upper ontology
 * with MITRE ATT&CK as the domain ontology, supporting both Enterprise and ICS datasets
 */

-- =============================================================================
-- UCO CORE CONSTRAINTS & INDEXES
-- =============================================================================

-- Core UCO Object constraints
CREATE CONSTRAINT uco_object_id FOR (o:`uco-core:UcoObject`) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT uco_action_id FOR (a:`uco-action:Action`) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT uco_identity_id FOR (i:`uco-identity:Identity`) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT uco_tool_id FOR (t:`uco-tool:Tool`) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT uco_observable_id FOR (obs:`uco-observable:ObservableObject`) REQUIRE obs.id IS UNIQUE;
CREATE CONSTRAINT uco_relationship_id FOR (r:`uco-core:Relationship`) REQUIRE r.id IS UNIQUE;

-- Core UCO indexes for performance
CREATE INDEX uco_object_name FOR (o:`uco-core:UcoObject`) ON (o.name);
CREATE INDEX uco_object_type FOR (o:`uco-core:UcoObject`) ON (o.mitre_type);
CREATE INDEX uco_object_dataset FOR (o:`uco-core:UcoObject`) ON (o.source_dataset);

-- =============================================================================
-- MITRE ATT&CK SPECIFIC CONSTRAINTS
-- =============================================================================

-- Attack Patterns (Techniques & Sub-techniques)
CREATE CONSTRAINT attack_pattern_id FOR (ap:AttackPattern) REQUIRE ap.id IS UNIQUE;
CREATE CONSTRAINT attack_pattern_mitre_id FOR (ap:AttackPattern) REQUIRE ap.mitre_id IS UNIQUE;

-- Tactics  
CREATE CONSTRAINT tactic_id FOR (t:Tactic) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT tactic_mitre_id FOR (t:Tactic) REQUIRE t.mitre_id IS UNIQUE;

-- Threat Actors / Intrusion Sets
CREATE CONSTRAINT threat_actor_id FOR (ta:ThreatActor) REQUIRE ta.id IS UNIQUE;
CREATE CONSTRAINT threat_actor_mitre_id FOR (ta:ThreatActor) REQUIRE ta.mitre_id IS UNIQUE;

-- Malware
CREATE CONSTRAINT malware_id FOR (m:Malware) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT malware_mitre_id FOR (m:Malware) REQUIRE m.mitre_id IS UNIQUE;

-- Tools
CREATE CONSTRAINT tool_mitre_id FOR (t:Tool) REQUIRE t.mitre_id IS UNIQUE;

-- Mitigations (Course of Action)
CREATE CONSTRAINT mitigation_id FOR (m:Mitigation) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT mitigation_mitre_id FOR (m:Mitigation) REQUIRE m.mitre_id IS UNIQUE;

-- Campaigns
CREATE CONSTRAINT campaign_id FOR (c:Campaign) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT campaign_mitre_id FOR (c:Campaign) REQUIRE c.mitre_id IS UNIQUE;

-- Data Sources & Components
CREATE CONSTRAINT data_source_id FOR (ds:DataSource) REQUIRE ds.id IS UNIQUE;
CREATE CONSTRAINT data_component_id FOR (dc:DataComponent) REQUIRE dc.id IS UNIQUE;

-- ICS-Specific Assets
CREATE CONSTRAINT ics_asset_id FOR (a:ICSAsset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT ics_asset_mitre_id FOR (a:ICSAsset) REQUIRE a.mitre_id IS UNIQUE;

-- Matrices & Collections
CREATE CONSTRAINT matrix_id FOR (mx:Matrix) REQUIRE mx.id IS UNIQUE;
CREATE CONSTRAINT collection_id FOR (col:Collection) REQUIRE col.id IS UNIQUE;

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Attack Pattern indexes
CREATE INDEX attack_pattern_name FOR (ap:AttackPattern) ON (ap.name);
CREATE INDEX attack_pattern_platforms FOR (ap:AttackPattern) ON (ap.platforms);
CREATE INDEX attack_pattern_is_subtechnique FOR (ap:AttackPattern) ON (ap.is_subtechnique);
CREATE INDEX attack_pattern_dataset FOR (ap:AttackPattern) ON (ap.source_dataset);

-- Tactic indexes
CREATE INDEX tactic_name FOR (t:Tactic) ON (t.name);
CREATE INDEX tactic_shortname FOR (t:Tactic) ON (t.shortname);
CREATE INDEX tactic_dataset FOR (t:Tactic) ON (t.source_dataset);

-- Threat Actor indexes
CREATE INDEX threat_actor_name FOR (ta:ThreatActor) ON (ta.name);
CREATE INDEX threat_actor_aliases FOR (ta:ThreatActor) ON (ta.aliases);
CREATE INDEX threat_actor_dataset FOR (ta:ThreatActor) ON (ta.source_dataset);

-- Malware indexes
CREATE INDEX malware_name FOR (m:Malware) ON (m.name);
CREATE INDEX malware_platforms FOR (m:Malware) ON (m.platforms);
CREATE INDEX malware_is_family FOR (m:Malware) ON (m.is_family);
CREATE INDEX malware_dataset FOR (m:Malware) ON (m.source_dataset);

-- Tool indexes
CREATE INDEX tool_name FOR (t:Tool) ON (t.name);
CREATE INDEX tool_platforms FOR (t:Tool) ON (t.platforms);
CREATE INDEX tool_dataset FOR (t:Tool) ON (t.source_dataset);

-- Mitigation indexes
CREATE INDEX mitigation_name FOR (m:Mitigation) ON (m.name);
CREATE INDEX mitigation_dataset FOR (m:Mitigation) ON (m.source_dataset);

-- Campaign indexes
CREATE INDEX campaign_name FOR (c:Campaign) ON (c.name);
CREATE INDEX campaign_first_seen FOR (c:Campaign) ON (c.first_seen);
CREATE INDEX campaign_last_seen FOR (c:Campaign) ON (c.last_seen);
CREATE INDEX campaign_dataset FOR (c:Campaign) ON (c.source_dataset);

-- ICS Asset indexes
CREATE INDEX ics_asset_name FOR (a:ICSAsset) ON (a.name);
CREATE INDEX ics_asset_platforms FOR (a:ICSAsset) ON (a.platforms);
CREATE INDEX ics_asset_sectors FOR (a:ICSAsset) ON (a.sectors);

-- Data Source/Component indexes
CREATE INDEX data_source_name FOR (ds:DataSource) ON (ds.name);
CREATE INDEX data_source_platforms FOR (ds:DataSource) ON (ds.platforms);
CREATE INDEX data_component_name FOR (dc:DataComponent) ON (dc.name);

-- =============================================================================
-- FULL-TEXT SEARCH INDEXES FOR RAG
-- =============================================================================

-- Primary content search indexes
CREATE FULLTEXT INDEX attack_pattern_search FOR (ap:AttackPattern) ON EACH [ap.name, ap.description];
CREATE FULLTEXT INDEX tactic_search FOR (t:Tactic) ON EACH [t.name, t.description];
CREATE FULLTEXT INDEX threat_actor_search FOR (ta:ThreatActor) ON EACH [ta.name, ta.description, ta.aliases];
CREATE FULLTEXT INDEX malware_search FOR (m:Malware) ON EACH [m.name, m.description];
CREATE FULLTEXT INDEX tool_search FOR (t:Tool) ON EACH [t.name, t.description];
CREATE FULLTEXT INDEX mitigation_search FOR (m:Mitigation) ON EACH [m.name, m.description];
CREATE FULLTEXT INDEX campaign_search FOR (c:Campaign) ON EACH [c.name, c.description];
CREATE FULLTEXT INDEX ics_asset_search FOR (a:ICSAsset) ON EACH [a.name, a.description];

-- Universal search across all MITRE objects
CREATE FULLTEXT INDEX mitre_universal_search FOR (
    ap:AttackPattern|t:Tactic|ta:ThreatActor|m:Malware|tool:Tool|mit:Mitigation|c:Campaign|a:ICSAsset
) ON EACH [name, description];

-- =============================================================================
-- NODE LABEL HIERARCHY & INHERITANCE
-- =============================================================================

-- Set up label inheritance following UCO structure
-- All MITRE objects inherit from UcoObject
-- Actions inherit from both UcoObject and Action
-- Tools inherit from both UcoObject and Tool
-- Identities inherit from both UcoObject and Identity

-- Add secondary labels for UCO compliance
MATCH (ap:AttackPattern) SET ap:`uco-action:Action`, ap:`uco-core:UcoObject`;
MATCH (t:Tactic) SET t:`uco-action:ActionPattern`, t:`uco-core:UcoObject`;
MATCH (ta:ThreatActor) SET ta:`uco-identity:Identity`, ta:`uco-core:UcoObject`;
MATCH (m:Malware) SET m:`uco-tool:Tool`, m:`uco-core:UcoObject`;
MATCH (tool:Tool) SET tool:`uco-tool:Tool`, tool:`uco-core:UcoObject`;
MATCH (mit:Mitigation) SET mit:`uco-action:Action`, mit:`uco-core:UcoObject`;
MATCH (c:Campaign) SET c:`uco-action:Action`, c:`uco-core:UcoObject`;
MATCH (a:ICSAsset) SET a:`uco-core:UcoObject`;
MATCH (ds:DataSource) SET ds:`uco-observable:ObservablePattern`, ds:`uco-core:UcoObject`;
MATCH (dc:DataComponent) SET dc:`uco-observable:ObservableObject`, dc:`uco-core:UcoObject`;

-- =============================================================================
-- RELATIONSHIP TYPE CONSTRAINTS & INDEXES
-- =============================================================================

-- Ensure relationship consistency
CREATE INDEX relationship_type FOR ()-[r]-() ON (type(r));
CREATE INDEX relationship_source_dataset FOR ()-[r]-() ON (r.source_dataset);

-- =============================================================================
-- VALIDATION CONSTRAINTS FOR DATA QUALITY
-- =============================================================================

-- Ensure required properties exist
CREATE CONSTRAINT attack_pattern_name_required FOR (ap:AttackPattern) REQUIRE ap.name IS NOT NULL;
CREATE CONSTRAINT tactic_name_required FOR (t:Tactic) REQUIRE t.name IS NOT NULL;
CREATE CONSTRAINT threat_actor_name_required FOR (ta:ThreatActor) REQUIRE ta.name IS NOT NULL;
CREATE CONSTRAINT malware_name_required FOR (m:Malware) REQUIRE m.name IS NOT NULL;
CREATE CONSTRAINT tool_name_required FOR (t:Tool) REQUIRE t.name IS NOT NULL;
CREATE CONSTRAINT mitigation_name_required FOR (m:Mitigation) REQUIRE m.name IS NOT NULL;

-- Ensure source_dataset is valid
CREATE CONSTRAINT valid_source_dataset FOR (o:`uco-core:UcoObject`) 
REQUIRE o.source_dataset IN ['enterprise', 'ics', 'cross-reference'];

-- =============================================================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- =============================================================================

-- Multi-property indexes for common query patterns
CREATE INDEX attack_pattern_composite FOR (ap:AttackPattern) ON (ap.source_dataset, ap.is_subtechnique);
CREATE INDEX threat_actor_composite FOR (ta:ThreatActor) ON (ta.source_dataset, ta.name);
CREATE INDEX malware_composite FOR (m:Malware) ON (m.source_dataset, m.is_family);
CREATE INDEX campaign_composite FOR (c:Campaign) ON (c.source_dataset, c.first_seen);

-- =============================================================================
-- STATISTICS & MONITORING SETUP
-- =============================================================================

-- Enable automatic statistics collection for query optimization
CALL db.schema.sampling.sampleIndex('attack_pattern_name');
CALL db.schema.sampling.sampleIndex('tactic_name'); 
CALL db.schema.sampling.sampleIndex('threat_actor_name');
CALL db.schema.sampling.sampleIndex('malware_name');

-- =============================================================================
-- CROSS-DATASET RELATIONSHIP PATTERNS
-- =============================================================================

-- Create indexes for cross-dataset analysis
CREATE INDEX cross_dataset_similarity FOR ()-[r:SIMILAR_TO]-() ON (r.confidence);
CREATE INDEX cross_dataset_same_as FOR ()-[r:SAME_AS]-() ON (r.identity_basis);
CREATE INDEX cross_dataset_related FOR ()-[r:RELATED_TO]-() ON (r.similarity_basis);

-- =============================================================================
-- TEMPORAL INDEXES FOR CAMPAIGN ANALYSIS
-- =============================================================================

-- Time-based analysis support
CREATE INDEX campaign_temporal FOR (c:Campaign) ON (c.first_seen, c.last_seen);
CREATE INDEX object_temporal FOR (o:`uco-core:UcoObject`) ON (o.created, o.modified);

-- =============================================================================
-- GEOSPATIAL PREPARATION (for future geographic analysis)
-- =============================================================================

-- Prepare for geographic threat actor analysis
CREATE INDEX threat_actor_geographic FOR (ta:ThreatActor) ON (ta.country);

-- =============================================================================
-- SCHEMA VALIDATION QUERIES
-- =============================================================================

-- Verify schema completeness
-- CALL db.schema.visualization() - Use to visualize the schema
-- CALL db.constraints() - List all constraints
-- CALL db.indexes() - List all indexes

-- Performance monitoring queries for optimization
-- CALL db.stats.retrieve('GRAPH COUNTS') - Get node/relationship counts
-- CALL db.stats.clear() - Clear cached statistics when needed

-- =============================================================================
-- FUTURE EXTENSION POINTS
-- =============================================================================

-- Prepared for additional ontologies
-- CREATE CONSTRAINT cve_id FOR (v:Vulnerability) REQUIRE v.cve_id IS UNIQUE;
-- CREATE CONSTRAINT cpe_id FOR (c:CommonPlatformEnumeration) REQUIRE c.cpe_id IS UNIQUE;
-- CREATE CONSTRAINT ioc_hash FOR (i:IndicatorOfCompromise) REQUIRE i.hash IS UNIQUE;

-- Prepared for payload analysis integration  
-- CREATE CONSTRAINT payload_id FOR (p:Payload) REQUIRE p.id IS UNIQUE;
-- CREATE INDEX payload_search FOR (p:Payload) ON (p.code_snippet);

-- =============================================================================
-- MAINTENANCE & CLEANUP PROCEDURES
-- =============================================================================

-- Cleanup procedure for orphaned nodes
-- MATCH (n) WHERE NOT (n)--() DELETE n;

-- Procedure to update modified timestamps
-- MATCH (n:`uco-core:UcoObject`) SET n.last_updated = datetime();

-- Reindex procedure for performance optimization
-- CALL db.index.fulltext.drop('mitre_universal_search');
-- CREATE FULLTEXT INDEX mitre_universal_search FOR (...) ON EACH [...];

COMMIT;