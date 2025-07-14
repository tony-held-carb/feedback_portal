#!/usr/bin/env python3
"""
PostgreSQL diagnostics script to examine table structures and identify export issues.
"""

import os
import sys
import logging
from datetime import datetime

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'source', 'production'))

from arb.portal.extensions import db
from arb.portal.app import create_app


def examine_postgres_table_structure():
    """Examine the actual PostgreSQL table structure to identify export issues."""
    logger = logging.getLogger(__name__)
    
    try:
        # Create Flask app context
        app = create_app()
        with app.app_context():
            # Get the engine
            engine = db.engine
            logger.info("Connected to PostgreSQL database")
        
        # Examine the incidences table structure
        logger.info("Examining incidences table structure...")
        
        with engine.connect() as conn:
            # Get table information
            result = conn.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns 
                WHERE table_name = 'incidences' 
                ORDER BY ordinal_position
            """)
            
            columns = result.fetchall()
            
            logger.info("Incidences table columns:")
            logger.info("-" * 80)
            
            potential_issues = []
            
            for col in columns:
                col_name = col[0]
                data_type = col[1]
                is_nullable = col[2]
                default_value = col[3]
                
                logger.info(f"{col_name:<25} | {data_type:<15} | {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
                
                # Check for potential issues
                if data_type in ['jsonb', 'json']:
                    potential_issues.append(f"Column '{col_name}' has JSONB/JSON type - needs conversion to TEXT")
                
                if default_value and any(keyword in default_value.lower() for keyword in ['nextval', 'currval', 'now()', 'uuid_generate']):
                    potential_issues.append(f"Column '{col_name}' has PostgreSQL-specific default: {default_value}")
                
                if ':' in col_name or ' ' in col_name:
                    potential_issues.append(f"Column '{col_name}' has invalid characters for SQLite")
            
            # Check foreign key constraints
            logger.info("\nForeign key constraints:")
            logger.info("-" * 80)
            
            result = conn.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'incidences'
            """)
            
            fks = result.fetchall()
            for fk in fks:
                logger.info(f"{fk[0]:<30} | {fk[1]:<20} -> {fk[2]}.{fk[3]}")
            
            # Check if table has data
            result = conn.execute("SELECT COUNT(*) as count FROM incidences")
            row_count = result.fetchone()[0]
            logger.info(f"\nRow count in incidences table: {row_count:,}")
            
            if row_count > 0:
                # Get sample data
                result = conn.execute("SELECT * FROM incidences LIMIT 1")
                sample = result.fetchone()
                if sample:
                    logger.info("Sample row data types:")
                    for i, col in enumerate(columns):
                        if i < len(sample):
                            value = sample[i]
                            value_type = type(value).__name__
                            logger.info(f"  {col[0]}: {value_type} = {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            
            # Check for any PostgreSQL-specific features
            logger.info("\nChecking for PostgreSQL-specific features...")
            
            # Check for sequences
            result = conn.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_name LIKE '%incidence%'
            """)
            sequences = result.fetchall()
            if sequences:
                logger.info("Sequences related to incidences:")
                for seq in sequences:
                    logger.info(f"  - {seq[0]}")
                    potential_issues.append(f"Sequence dependency: {seq[0]}")
            
            # Check for triggers
            result = conn.execute("""
                SELECT trigger_name, event_manipulation, action_statement
                FROM information_schema.triggers 
                WHERE event_object_table = 'incidences'
            """)
            triggers = result.fetchall()
            if triggers:
                logger.info("Triggers on incidences table:")
                for trigger in triggers:
                    logger.info(f"  - {trigger[0]} ({trigger[1]})")
                    potential_issues.append(f"Trigger: {trigger[0]} - {trigger[2][:50]}...")
            
            # Report potential issues
            if potential_issues:
                logger.warning("\nPOTENTIAL EXPORT ISSUES:")
                logger.warning("-" * 80)
                for issue in potential_issues:
                    logger.warning(f"  - {issue}")
            else:
                logger.info("\nNo obvious export issues detected in table structure")
            
            return potential_issues
            
    except Exception as e:
        logger.error(f"Error examining PostgreSQL table: {e}")
        return [f"Error: {e}"]


def main():
    """Main function."""
    # Set up logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"postgres_diagnostics_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting PostgreSQL diagnostics - log file: {log_filename}")
    
    issues = examine_postgres_table_structure()
    
    logger.info("\n" + "=" * 80)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total potential issues found: {len(issues)}")
    
    if issues:
        logger.info("\nRecommended fixes:")
        for i, issue in enumerate(issues, 1):
            logger.info(f"{i}. {issue}")
    
    logger.info("PostgreSQL diagnostics completed")


if __name__ == "__main__":
    main() 