#!/usr/bin/env python3
"""
Schema analysis script to verify hierarchical subdomain support
in the bigshot reconnaissance application database.

This script analyzes the database schema to ensure it properly
supports hierarchical/collapsible subdomain data structures.
"""

import sqlite3
import psycopg2
import argparse
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubdomainHierarchyAnalyzer:
    """Analyzes and verifies hierarchical subdomain support."""
    
    def __init__(self, db_path: str, db_type: str = 'sqlite'):
        """
        Initialize the analyzer.
        
        Args:
            db_path: Path to database file (SQLite) or connection string (PostgreSQL)
            db_type: Database type ('sqlite' or 'postgresql')
        """
        self.db_path = db_path
        self.db_type = db_type
        self.conn = None
    
    def connect_database(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.db_type == 'sqlite':
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
            else:
                # PostgreSQL connection would be implemented here
                logger.error("PostgreSQL connection not implemented in this version")
                return False
                
            logger.info(f"Connected to {self.db_type} database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Closed database connection")
    
    def analyze_schema_structure(self) -> Dict[str, Any]:
        """
        Analyze the database schema structure for hierarchical support.
        
        Returns:
            Dictionary containing schema analysis results
        """
        try:
            cursor = self.conn.cursor()
            
            # Get table schema
            cursor.execute("PRAGMA table_info(domains)")
            columns = cursor.fetchall()
            
            # Get indexes
            cursor.execute("PRAGMA index_list(domains)")
            indexes = cursor.fetchall()
            
            # Get index details
            index_details = {}
            for index in indexes:
                index_name = index[1]
                cursor.execute(f"PRAGMA index_info({index_name})")
                index_details[index_name] = cursor.fetchall()
            
            schema_analysis = {
                'table_name': 'domains',
                'columns': {col[1]: {'type': col[2], 'nullable': not col[3], 'default': col[4]} for col in columns},
                'indexes': index_details,
                'hierarchical_support': self._evaluate_hierarchical_support(columns, index_details)
            }
            
            return schema_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze schema: {e}")
            return {}
    
    def _evaluate_hierarchical_support(self, columns: List, indexes: Dict) -> Dict[str, Any]:
        """
        Evaluate how well the schema supports hierarchical subdomain structures.
        
        Args:
            columns: List of column information
            indexes: Dictionary of index information
            
        Returns:
            Dictionary containing hierarchical support analysis
        """
        column_names = [col[1] for col in columns]
        
        # Check for required columns
        required_columns = ['root_domain', 'subdomain', 'source']
        has_required = all(col in column_names for col in required_columns)
        
        # Check for helpful columns
        helpful_columns = ['tags', 'fetched_at', 'created_at']
        has_helpful = {col: col in column_names for col in helpful_columns}
        
        # Check for performance indexes
        has_root_index = any('root' in idx_name.lower() for idx_name in indexes.keys())
        has_subdomain_index = any('subdomain' in idx_name.lower() for idx_name in indexes.keys())
        has_hierarchical_index = any('hierarchical' in idx_name.lower() for idx_name in indexes.keys())
        
        # Check for unique constraints that support deduplication
        has_unique_constraint = any(
            any(col[1] == 'subdomain' for col in idx_cols) and 
            any(col[1] == 'source' for col in idx_cols)
            for idx_cols in indexes.values()
        )
        
        return {
            'has_required_columns': has_required,
            'missing_required_columns': [col for col in required_columns if col not in column_names],
            'has_helpful_columns': has_helpful,
            'has_root_domain_index': has_root_index,
            'has_subdomain_index': has_subdomain_index,
            'has_hierarchical_index': has_hierarchical_index,
            'has_unique_constraint': has_unique_constraint,
            'recommendations': self._generate_recommendations(has_required, has_helpful, has_root_index, has_subdomain_index, has_hierarchical_index)
        }
    
    def _generate_recommendations(self, has_required: bool, has_helpful: Dict, has_root_index: bool, has_subdomain_index: bool, has_hierarchical_index: bool) -> List[str]:
        """
        Generate recommendations for improving hierarchical support.
        
        Args:
            has_required: Whether all required columns are present
            has_helpful: Dictionary of helpful column availability
            has_root_index: Whether root domain index exists
            has_subdomain_index: Whether subdomain index exists
            has_hierarchical_index: Whether hierarchical index exists
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not has_required:
            recommendations.append("Add missing required columns: root_domain, subdomain, source")
        
        if not has_helpful.get('tags', False):
            recommendations.append("Add 'tags' column for user categorization")
        
        if not has_helpful.get('created_at', False):
            recommendations.append("Add 'created_at' column for temporal analysis")
        
        if not has_root_index:
            recommendations.append("Add index on root_domain for performance")
        
        if not has_subdomain_index:
            recommendations.append("Add index on subdomain for performance")
        
        if not has_hierarchical_index:
            recommendations.append("Add composite index on (root_domain, subdomain) for hierarchical queries")
        
        return recommendations
    
    def analyze_sample_data(self) -> Dict[str, Any]:
        """
        Analyze sample data to understand hierarchical patterns.
        
        Returns:
            Dictionary containing data analysis results
        """
        try:
            cursor = self.conn.cursor()
            
            # Get sample data
            cursor.execute("SELECT root_domain, subdomain, source FROM domains LIMIT 100")
            sample_data = cursor.fetchall()
            
            if not sample_data:
                return {'error': 'No sample data available'}
            
            # Analyze hierarchical patterns
            hierarchy_analysis = self._analyze_hierarchy_patterns(sample_data)
            
            return {
                'sample_size': len(sample_data),
                'hierarchy_analysis': hierarchy_analysis,
                'data_quality': self._assess_data_quality(sample_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze sample data: {e}")
            return {'error': str(e)}
    
    def _analyze_hierarchy_patterns(self, sample_data: List) -> Dict[str, Any]:
        """
        Analyze hierarchical patterns in the sample data.
        
        Args:
            sample_data: List of sample rows
            
        Returns:
            Dictionary containing hierarchy analysis
        """
        root_domains = defaultdict(set)
        subdomain_levels = defaultdict(int)
        
        for row in sample_data:
            root_domain = row[0]
            subdomain = row[1]
            source = row[2]
            
            root_domains[root_domain].add(subdomain)
            
            # Count subdomain levels
            if subdomain and root_domain:
                # Remove root domain from subdomain to count levels
                subdomain_part = subdomain.replace(f".{root_domain}", "")
                levels = len(subdomain_part.split('.')) if subdomain_part else 0
                subdomain_levels[levels] += 1
        
        return {
            'unique_root_domains': len(root_domains),
            'avg_subdomains_per_root': sum(len(subs) for subs in root_domains.values()) / len(root_domains) if root_domains else 0,
            'subdomain_level_distribution': dict(subdomain_levels),
            'max_subdomain_levels': max(subdomain_levels.keys()) if subdomain_levels else 0,
            'hierarchical_complexity': self._calculate_hierarchical_complexity(root_domains)
        }
    
    def _calculate_hierarchical_complexity(self, root_domains: Dict) -> float:
        """
        Calculate a complexity score for the hierarchical structure.
        
        Args:
            root_domains: Dictionary mapping root domains to their subdomains
            
        Returns:
            Complexity score (0-1, where 1 is most complex)
        """
        if not root_domains:
            return 0.0
        
        total_complexity = 0
        
        for root_domain, subdomains in root_domains.items():
            # Count subdomain levels for this root domain
            level_counts = defaultdict(int)
            
            for subdomain in subdomains:
                subdomain_part = subdomain.replace(f".{root_domain}", "")
                levels = len(subdomain_part.split('.')) if subdomain_part else 0
                level_counts[levels] += 1
            
            # Calculate complexity for this root domain
            domain_complexity = sum(level * count for level, count in level_counts.items())
            total_complexity += domain_complexity
        
        # Normalize by total number of subdomains
        total_subdomains = sum(len(subs) for subs in root_domains.values())
        return min(total_complexity / total_subdomains / 5, 1.0) if total_subdomains > 0 else 0.0
    
    def _assess_data_quality(self, sample_data: List) -> Dict[str, Any]:
        """
        Assess the quality of data for hierarchical analysis.
        
        Args:
            sample_data: List of sample rows
            
        Returns:
            Dictionary containing data quality assessment
        """
        quality_issues = []
        
        empty_root_domains = sum(1 for row in sample_data if not row[0])
        empty_subdomains = sum(1 for row in sample_data if not row[1])
        empty_sources = sum(1 for row in sample_data if not row[2])
        
        if empty_root_domains > 0:
            quality_issues.append(f"{empty_root_domains} rows with empty root_domain")
        
        if empty_subdomains > 0:
            quality_issues.append(f"{empty_subdomains} rows with empty subdomain")
        
        if empty_sources > 0:
            quality_issues.append(f"{empty_sources} rows with empty source")
        
        # Check for potential data inconsistencies
        inconsistent_domains = 0
        for row in sample_data:
            root_domain = row[0]
            subdomain = row[1]
            
            if root_domain and subdomain and not subdomain.endswith(root_domain):
                inconsistent_domains += 1
        
        if inconsistent_domains > 0:
            quality_issues.append(f"{inconsistent_domains} rows with subdomain not ending with root_domain")
        
        return {
            'total_rows': len(sample_data),
            'quality_issues': quality_issues,
            'data_completeness': (len(sample_data) - empty_root_domains - empty_subdomains - empty_sources) / (len(sample_data) * 3) if sample_data else 0,
            'consistency_score': (len(sample_data) - inconsistent_domains) / len(sample_data) if sample_data else 0
        }
    
    def generate_test_data(self, num_domains: int = 10) -> List[Tuple[str, str, str]]:
        """
        Generate test data for hierarchical subdomain analysis.
        
        Args:
            num_domains: Number of test domains to generate
            
        Returns:
            List of (root_domain, subdomain, source) tuples
        """
        test_data = []
        sources = ['crt.sh', 'virustotal', 'shodan', 'subfinder']
        
        for i in range(num_domains):
            root_domain = f"example{i}.com"
            
            # Generate hierarchical subdomains
            subdomains = [
                root_domain,
                f"www.{root_domain}",
                f"api.{root_domain}",
                f"mail.{root_domain}",
                f"dev.api.{root_domain}",
                f"stage.api.{root_domain}",
                f"admin.www.{root_domain}",
                f"test.dev.api.{root_domain}"
            ]
            
            for subdomain in subdomains:
                for source in sources[:2]:  # Use first 2 sources
                    test_data.append((root_domain, subdomain, source))
        
        return test_data
    
    def run_analysis(self) -> Dict[str, Any]:
        """
        Run the complete hierarchical subdomain analysis.
        
        Returns:
            Dictionary containing complete analysis results
        """
        try:
            if not self.connect_database():
                return {'error': 'Failed to connect to database'}
            
            # Analyze schema
            schema_analysis = self.analyze_schema_structure()
            
            # Analyze sample data
            data_analysis = self.analyze_sample_data()
            
            # Generate overall assessment
            overall_assessment = self._generate_overall_assessment(schema_analysis, data_analysis)
            
            return {
                'schema_analysis': schema_analysis,
                'data_analysis': data_analysis,
                'overall_assessment': overall_assessment,
                'timestamp': str(datetime.now())
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {'error': str(e)}
        
        finally:
            self.close_connection()
    
    def _generate_overall_assessment(self, schema_analysis: Dict, data_analysis: Dict) -> Dict[str, Any]:
        """
        Generate overall assessment of hierarchical subdomain support.
        
        Args:
            schema_analysis: Results from schema analysis
            data_analysis: Results from data analysis
            
        Returns:
            Dictionary containing overall assessment
        """
        hierarchical_support = schema_analysis.get('hierarchical_support', {})
        
        # Calculate overall score
        schema_score = 0
        if hierarchical_support.get('has_required_columns', False):
            schema_score += 40
        if hierarchical_support.get('has_root_domain_index', False):
            schema_score += 20
        if hierarchical_support.get('has_subdomain_index', False):
            schema_score += 20
        if hierarchical_support.get('has_hierarchical_index', False):
            schema_score += 20
        
        data_score = 0
        if 'data_quality' in data_analysis:
            data_quality = data_analysis['data_quality']
            data_score = (data_quality.get('data_completeness', 0) * 50 + 
                         data_quality.get('consistency_score', 0) * 50)
        
        overall_score = (schema_score + data_score) / 2
        
        # Determine readiness level
        if overall_score >= 90:
            readiness = 'Excellent'
        elif overall_score >= 70:
            readiness = 'Good'
        elif overall_score >= 50:
            readiness = 'Fair'
        else:
            readiness = 'Poor'
        
        return {
            'overall_score': overall_score,
            'readiness_level': readiness,
            'schema_score': schema_score,
            'data_score': data_score,
            'key_recommendations': hierarchical_support.get('recommendations', []),
            'supports_hierarchical_display': hierarchical_support.get('has_required_columns', False) and hierarchical_support.get('has_root_domain_index', False)
        }

def main():
    """Main function to run the hierarchical subdomain analysis."""
    parser = argparse.ArgumentParser(description='Analyze hierarchical subdomain support in database')
    parser.add_argument('--db-path', required=True, help='Path to database file')
    parser.add_argument('--db-type', default='sqlite', choices=['sqlite', 'postgresql'], help='Database type')
    parser.add_argument('--output-file', help='Output file for analysis results (JSON)')
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = SubdomainHierarchyAnalyzer(args.db_path, args.db_type)
    
    # Run analysis
    results = analyzer.run_analysis()
    
    # Output results
    if args.output_file:
        import json
        with open(args.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results saved to {args.output_file}")
    else:
        import json
        print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()