"""
Cross-Dataset Analysis and Relationship Mapping
Advanced interconnection analysis between Enterprise and ICS MITRE ATT&CK datasets
"""

import json
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from difflib import SequenceMatcher
import re

@dataclass
class CrossReferenceAnalysis:
    """Results of cross-dataset analysis"""
    shared_techniques: List[Dict[str, Any]]
    shared_actors: List[Dict[str, Any]]
    shared_malware: List[Dict[str, Any]]
    technique_similarities: List[Dict[str, Any]]
    actor_overlaps: List[Dict[str, Any]]
    platform_intersections: List[Dict[str, Any]]
    tactic_mappings: List[Dict[str, Any]]

class CrossDatasetAnalyzer:
    """Analyzes relationships and overlaps between Enterprise and ICS datasets"""
    
    def __init__(self):
        self.enterprise_data = None
        self.ics_data = None
        self.analysis_results = None
    
    def load_datasets(self, enterprise_path: str, ics_path: str) -> None:
        """Load both datasets for analysis"""
        with open(enterprise_path) as f:
            self.enterprise_data = json.load(f)
        
        with open(ics_path) as f:
            self.ics_data = json.load(f)
        
        print(f"Loaded Enterprise: {len(self.enterprise_data['objects'])} objects")
        print(f"Loaded ICS: {len(self.ics_data['objects'])} objects")
    
    def analyze_cross_references(self) -> CrossReferenceAnalysis:
        """Perform comprehensive cross-dataset analysis"""
        
        # Extract objects by type from both datasets
        enterprise_objects = self._extract_objects_by_type(self.enterprise_data)
        ics_objects = self._extract_objects_by_type(self.ics_data)
        
        # Find exact matches and similarities
        shared_techniques = self._find_shared_techniques(enterprise_objects, ics_objects)
        shared_actors = self._find_shared_actors(enterprise_objects, ics_objects)
        shared_malware = self._find_shared_malware(enterprise_objects, ics_objects)
        
        # Find semantic similarities
        technique_similarities = self._find_technique_similarities(enterprise_objects, ics_objects)
        actor_overlaps = self._find_actor_overlaps(enterprise_objects, ics_objects)
        
        # Analyze platform and tactic intersections
        platform_intersections = self._analyze_platform_intersections(enterprise_objects, ics_objects)
        tactic_mappings = self._map_tactics_across_datasets(enterprise_objects, ics_objects)
        
        self.analysis_results = CrossReferenceAnalysis(
            shared_techniques=shared_techniques,
            shared_actors=shared_actors,
            shared_malware=shared_malware,
            technique_similarities=technique_similarities,
            actor_overlaps=actor_overlaps,
            platform_intersections=platform_intersections,
            tactic_mappings=tactic_mappings
        )
        
        return self.analysis_results
    
    def _extract_objects_by_type(self, dataset: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract and organize objects by type"""
        objects_by_type = {}
        
        for obj in dataset['objects']:
            obj_type = obj['type']
            if obj_type not in objects_by_type:
                objects_by_type[obj_type] = []
            objects_by_type[obj_type].append(obj)
        
        return objects_by_type
    
    def _find_shared_techniques(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Find techniques that appear in both datasets"""
        shared = []
        
        enterprise_techniques = {self._get_mitre_id(t): t for t in enterprise_objs.get('attack-pattern', [])}
        ics_techniques = {self._get_mitre_id(t): t for t in ics_objs.get('attack-pattern', [])}
        
        # Find exact MITRE ID matches
        common_ids = set(enterprise_techniques.keys()) & set(ics_techniques.keys())
        common_ids.discard(None)  # Remove None values
        
        for mitre_id in common_ids:
            ent_tech = enterprise_techniques[mitre_id]
            ics_tech = ics_techniques[mitre_id]
            
            shared.append({
                'mitre_id': mitre_id,
                'enterprise_technique': {
                    'id': ent_tech['id'],
                    'name': ent_tech.get('name'),
                    'description': ent_tech.get('description', '')[:200] + '...'
                },
                'ics_technique': {
                    'id': ics_tech['id'],
                    'name': ics_tech.get('name'),
                    'description': ics_tech.get('description', '')[:200] + '...'
                },
                'match_type': 'exact_mitre_id'
            })
        
        return shared
    
    def _find_shared_actors(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Find threat actors that appear in both datasets"""
        shared = []
        
        enterprise_actors = enterprise_objs.get('intrusion-set', [])
        ics_actors = ics_objs.get('intrusion-set', [])
        
        # Create name-based mappings
        ent_by_name = {actor.get('name', '').lower(): actor for actor in enterprise_actors}
        ics_by_name = {actor.get('name', '').lower(): actor for actor in ics_actors}
        
        # Find exact name matches
        common_names = set(ent_by_name.keys()) & set(ics_by_name.keys())
        common_names.discard('')  # Remove empty names
        
        for name in common_names:
            ent_actor = ent_by_name[name]
            ics_actor = ics_by_name[name]
            
            shared.append({
                'name': name.title(),
                'enterprise_actor': {
                    'id': ent_actor['id'],
                    'mitre_id': self._get_mitre_id(ent_actor),
                    'aliases': ent_actor.get('aliases', [])
                },
                'ics_actor': {
                    'id': ics_actor['id'],
                    'mitre_id': self._get_mitre_id(ics_actor),
                    'aliases': ics_actor.get('aliases', [])
                },
                'match_type': 'exact_name'
            })
        
        # Find alias-based matches
        alias_matches = self._find_actor_alias_matches(enterprise_actors, ics_actors)
        shared.extend(alias_matches)
        
        return shared
    
    def _find_shared_malware(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Find malware that appears in both datasets"""
        shared = []
        
        enterprise_malware = enterprise_objs.get('malware', [])
        ics_malware = ics_objs.get('malware', [])
        
        # Create name-based mappings
        ent_by_name = {mal.get('name', '').lower(): mal for mal in enterprise_malware}
        ics_by_name = {mal.get('name', '').lower(): mal for mal in ics_malware}
        
        # Find exact name matches
        common_names = set(ent_by_name.keys()) & set(ics_by_name.keys())
        common_names.discard('')
        
        for name in common_names:
            ent_mal = ent_by_name[name]
            ics_mal = ics_by_name[name]
            
            shared.append({
                'name': name.title(),
                'enterprise_malware': {
                    'id': ent_mal['id'],
                    'mitre_id': self._get_mitre_id(ent_mal),
                    'is_family': ent_mal.get('is_family', False),
                    'platforms': ent_mal.get('x_mitre_platforms', [])
                },
                'ics_malware': {
                    'id': ics_mal['id'],
                    'mitre_id': self._get_mitre_id(ics_mal),
                    'is_family': ics_mal.get('is_family', False),
                    'platforms': ics_mal.get('x_mitre_platforms', [])
                },
                'match_type': 'exact_name'
            })
        
        return shared
    
    def _find_technique_similarities(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Find techniques with similar descriptions or names"""
        similarities = []
        
        enterprise_techniques = enterprise_objs.get('attack-pattern', [])
        ics_techniques = ics_objs.get('attack-pattern', [])
        
        # Compare all combinations for similarity
        for ent_tech in enterprise_techniques:
            ent_name = ent_tech.get('name', '')
            ent_desc = ent_tech.get('description', '')
            ent_mitre_id = self._get_mitre_id(ent_tech)
            
            for ics_tech in ics_techniques:
                ics_name = ics_tech.get('name', '')
                ics_desc = ics_tech.get('description', '')
                ics_mitre_id = self._get_mitre_id(ics_tech)
                
                # Skip if already exact matches
                if ent_mitre_id == ics_mitre_id:
                    continue
                
                # Calculate similarity scores
                name_similarity = SequenceMatcher(None, ent_name.lower(), ics_name.lower()).ratio()
                desc_similarity = SequenceMatcher(None, ent_desc.lower(), ics_desc.lower()).ratio()
                
                # Combined similarity with weighting
                combined_similarity = (name_similarity * 0.6) + (desc_similarity * 0.4)
                
                # Only include high-confidence similarities
                if combined_similarity > 0.7:
                    similarities.append({
                        'enterprise_technique': {
                            'id': ent_tech['id'],
                            'mitre_id': ent_mitre_id,
                            'name': ent_name
                        },
                        'ics_technique': {
                            'id': ics_tech['id'],
                            'mitre_id': ics_mitre_id,
                            'name': ics_name
                        },
                        'similarity_score': round(combined_similarity, 3),
                        'name_similarity': round(name_similarity, 3),
                        'description_similarity': round(desc_similarity, 3),
                        'match_type': 'semantic_similarity'
                    })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similarities[:50]  # Top 50 most similar
    
    def _find_actor_overlaps(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Find potential actor overlaps based on aliases and descriptions"""
        overlaps = []
        
        enterprise_actors = enterprise_objs.get('intrusion-set', [])
        ics_actors = ics_objs.get('intrusion-set', [])
        
        for ent_actor in enterprise_actors:
            ent_aliases = set(alias.lower() for alias in ent_actor.get('aliases', []))
            ent_name = ent_actor.get('name', '').lower()
            
            for ics_actor in ics_actors:
                ics_aliases = set(alias.lower() for alias in ics_actor.get('aliases', []))
                ics_name = ics_actor.get('name', '').lower()
                
                # Skip exact name matches (already found)
                if ent_name == ics_name:
                    continue
                
                # Check for alias overlaps
                common_aliases = ent_aliases & ics_aliases
                
                if common_aliases:
                    overlaps.append({
                        'enterprise_actor': {
                            'id': ent_actor['id'],
                            'name': ent_actor.get('name'),
                            'mitre_id': self._get_mitre_id(ent_actor)
                        },
                        'ics_actor': {
                            'id': ics_actor['id'],
                            'name': ics_actor.get('name'),
                            'mitre_id': self._get_mitre_id(ics_actor)
                        },
                        'common_aliases': list(common_aliases),
                        'match_type': 'alias_overlap'
                    })
        
        return overlaps
    
    def _analyze_platform_intersections(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Analyze platform coverage intersections"""
        intersections = []
        
        # Get platforms from techniques
        ent_platforms = set()
        ics_platforms = set()
        
        for tech in enterprise_objs.get('attack-pattern', []):
            platforms = tech.get('x_mitre_platforms', [])
            ent_platforms.update(platform.lower() for platform in platforms)
        
        for tech in ics_objs.get('attack-pattern', []):
            platforms = tech.get('x_mitre_platforms', [])
            ics_platforms.update(platform.lower() for platform in platforms)
        
        # Find common platforms
        common_platforms = ent_platforms & ics_platforms
        enterprise_only = ent_platforms - ics_platforms
        ics_only = ics_platforms - ent_platforms
        
        intersections.append({
            'analysis_type': 'platform_coverage',
            'common_platforms': sorted(list(common_platforms)),
            'enterprise_only_platforms': sorted(list(enterprise_only)),
            'ics_only_platforms': sorted(list(ics_only)),
            'overlap_percentage': len(common_platforms) / len(ent_platforms | ics_platforms) * 100
        })
        
        return intersections
    
    def _map_tactics_across_datasets(self, enterprise_objs: Dict, ics_objs: Dict) -> List[Dict[str, Any]]:
        """Map tactics between Enterprise and ICS frameworks"""
        mappings = []
        
        enterprise_tactics = {t.get('name', '').lower(): t for t in enterprise_objs.get('x-mitre-tactic', [])}
        ics_tactics = {t.get('name', '').lower(): t for t in ics_objs.get('x-mitre-tactic', [])}
        
        # Find exact tactic name matches
        common_tactics = set(enterprise_tactics.keys()) & set(ics_tactics.keys())
        common_tactics.discard('')
        
        for tactic_name in common_tactics:
            ent_tactic = enterprise_tactics[tactic_name]
            ics_tactic = ics_tactics[tactic_name]
            
            mappings.append({
                'tactic_name': tactic_name.title(),
                'enterprise_tactic': {
                    'id': ent_tactic['id'],
                    'mitre_id': self._get_mitre_id(ent_tactic),
                    'shortname': ent_tactic.get('x_mitre_shortname')
                },
                'ics_tactic': {
                    'id': ics_tactic['id'],
                    'mitre_id': self._get_mitre_id(ics_tactic),
                    'shortname': ics_tactic.get('x_mitre_shortname')
                },
                'match_type': 'exact_name'
            })
        
        # Find similar tactics by description
        similarity_mappings = self._find_similar_tactics(enterprise_tactics, ics_tactics)
        mappings.extend(similarity_mappings)
        
        return mappings
    
    def _find_similar_tactics(self, enterprise_tactics: Dict, ics_tactics: Dict) -> List[Dict[str, Any]]:
        """Find tactics with similar descriptions"""
        similar = []
        
        for ent_name, ent_tactic in enterprise_tactics.items():
            ent_desc = ent_tactic.get('description', '')
            
            for ics_name, ics_tactic in ics_tactics.items():
                # Skip if exact name match
                if ent_name == ics_name:
                    continue
                
                ics_desc = ics_tactic.get('description', '')
                
                # Calculate description similarity
                desc_similarity = SequenceMatcher(None, ent_desc.lower(), ics_desc.lower()).ratio()
                
                if desc_similarity > 0.5:  # Moderate similarity threshold
                    similar.append({
                        'enterprise_tactic': {
                            'id': ent_tactic['id'],
                            'name': ent_tactic.get('name'),
                            'shortname': ent_tactic.get('x_mitre_shortname')
                        },
                        'ics_tactic': {
                            'id': ics_tactic['id'],
                            'name': ics_tactic.get('name'),
                            'shortname': ics_tactic.get('x_mitre_shortname')
                        },
                        'similarity_score': round(desc_similarity, 3),
                        'match_type': 'description_similarity'
                    })
        
        return similar
    
    def _find_actor_alias_matches(self, enterprise_actors: List, ics_actors: List) -> List[Dict[str, Any]]:
        """Find actors that share aliases"""
        matches = []
        
        for ent_actor in enterprise_actors:
            ent_aliases = set(alias.lower() for alias in ent_actor.get('aliases', []))
            ent_name = ent_actor.get('name', '').lower()
            
            for ics_actor in ics_actors:
                ics_aliases = set(alias.lower() for alias in ics_actor.get('aliases', []))
                ics_name = ics_actor.get('name', '').lower()
                
                # Check if enterprise actor name appears in ICS aliases
                if ent_name in ics_aliases and ent_name != ics_name:
                    matches.append({
                        'enterprise_actor': {
                            'id': ent_actor['id'],
                            'name': ent_actor.get('name'),
                            'mitre_id': self._get_mitre_id(ent_actor)
                        },
                        'ics_actor': {
                            'id': ics_actor['id'],
                            'name': ics_actor.get('name'),
                            'mitre_id': self._get_mitre_id(ics_actor)
                        },
                        'match_basis': f"Enterprise name '{ent_name}' found in ICS aliases",
                        'match_type': 'name_in_aliases'
                    })
                
                # Check if ICS actor name appears in enterprise aliases
                elif ics_name in ent_aliases and ent_name != ics_name:
                    matches.append({
                        'enterprise_actor': {
                            'id': ent_actor['id'],
                            'name': ent_actor.get('name'),
                            'mitre_id': self._get_mitre_id(ent_actor)
                        },
                        'ics_actor': {
                            'id': ics_actor['id'],
                            'name': ics_actor.get('name'),
                            'mitre_id': self._get_mitre_id(ics_actor)
                        },
                        'match_basis': f"ICS name '{ics_name}' found in Enterprise aliases",
                        'match_type': 'name_in_aliases'
                    })
        
        return matches
    
    def _get_mitre_id(self, obj: Dict[str, Any]) -> str:
        """Extract MITRE ID from object's external references"""
        for ref in obj.get('external_references', []):
            if ref.get('source_name') == 'mitre-attack':
                return ref.get('external_id')
        return None
    
    def generate_cross_reference_report(self) -> str:
        """Generate a comprehensive cross-reference report"""
        if not self.analysis_results:
            raise ValueError("Must run analyze_cross_references() first")
        
        report = []
        report.append("# MITRE ATT&CK Cross-Dataset Analysis Report\n")
        
        # Shared Techniques
        report.append(f"## Shared Techniques ({len(self.analysis_results.shared_techniques)})")
        for tech in self.analysis_results.shared_techniques[:10]:  # Top 10
            report.append(f"- **{tech['mitre_id']}**: {tech['enterprise_technique']['name']}")
        
        # Shared Actors
        report.append(f"\n## Shared Threat Actors ({len(self.analysis_results.shared_actors)})")
        for actor in self.analysis_results.shared_actors:
            report.append(f"- **{actor['name']}** ({actor['match_type']})")
        
        # Shared Malware
        report.append(f"\n## Shared Malware ({len(self.analysis_results.shared_malware)})")
        for malware in self.analysis_results.shared_malware:
            report.append(f"- **{malware['name']}** ({malware['match_type']})")
        
        # Similar Techniques
        report.append(f"\n## Similar Techniques ({len(self.analysis_results.technique_similarities)})")
        for sim in self.analysis_results.technique_similarities[:5]:  # Top 5
            report.append(f"- **Enterprise**: {sim['enterprise_technique']['name']} ({sim['enterprise_technique']['mitre_id']})")
            report.append(f"  **ICS**: {sim['ics_technique']['name']} ({sim['ics_technique']['mitre_id']})")
            report.append(f"  **Similarity**: {sim['similarity_score']}")
        
        # Platform Analysis
        if self.analysis_results.platform_intersections:
            platform_analysis = self.analysis_results.platform_intersections[0]
            report.append(f"\n## Platform Coverage Analysis")
            report.append(f"- **Common Platforms**: {', '.join(platform_analysis['common_platforms'])}")
            report.append(f"- **Overlap Percentage**: {platform_analysis['overlap_percentage']:.1f}%")
        
        # Tactic Mappings
        report.append(f"\n## Tactic Mappings ({len(self.analysis_results.tactic_mappings)})")
        for mapping in self.analysis_results.tactic_mappings:
            report.append(f"- **{mapping['tactic_name']}** ({mapping['match_type']})")
        
        return "\n".join(report)

def main():
    """Main execution for cross-dataset analysis"""
    
    analyzer = CrossDatasetAnalyzer()
    analyzer.load_datasets('enterprise-attack-17.1.json', 'ics-attack-17.1.json')
    
    print("Performing cross-dataset analysis...")
    results = analyzer.analyze_cross_references()
    
    print(f"\n=== Cross-Dataset Analysis Results ===")
    print(f"Shared Techniques: {len(results.shared_techniques)}")
    print(f"Shared Threat Actors: {len(results.shared_actors)}")
    print(f"Shared Malware: {len(results.shared_malware)}")
    print(f"Similar Techniques: {len(results.technique_similarities)}")
    print(f"Actor Overlaps: {len(results.actor_overlaps)}")
    print(f"Platform Intersections: {len(results.platform_intersections)}")
    print(f"Tactic Mappings: {len(results.tactic_mappings)}")
    
    # Show some examples
    if results.shared_techniques:
        print(f"\nExample Shared Techniques:")
        for tech in results.shared_techniques[:3]:
            print(f"  {tech['mitre_id']}: {tech['enterprise_technique']['name']}")
    
    if results.shared_actors:
        print(f"\nExample Shared Actors:")
        for actor in results.shared_actors[:3]:
            print(f"  {actor['name']} ({actor['match_type']})")
    
    if results.technique_similarities:
        print(f"\nTop Similar Techniques:")
        for sim in results.technique_similarities[:3]:
            print(f"  {sim['enterprise_technique']['name']} <-> {sim['ics_technique']['name']} (similarity: {sim['similarity_score']})")
    
    # Generate report
    report = analyzer.generate_cross_reference_report()
    with open('cross_dataset_analysis_report.md', 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: cross_dataset_analysis_report.md")

if __name__ == "__main__":
    main()