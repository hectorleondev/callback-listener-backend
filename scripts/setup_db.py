#!/usr/bin/env python3
"""
Initial database setup script.
Creates the database schema and initial data.
"""

import os
import sys
from app import create_app, db


def setup_database():
    """Setup database with initial schema."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['paths', 'requests']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' created")
                else:
                    print(f"❌ Table '{table}' not found")
                    return False
            
            print("🎉 Database setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            return False


if __name__ == '__main__':
    if setup_database():
        sys.exit(0)
    else:
        sys.exit(1)
