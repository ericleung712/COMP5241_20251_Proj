#!/usr/bin/env python3
"""
Migration script to upload existing local documents to Supabase storage
and update database records.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.database import db
from src.models.document import Document
from src.utils.supabase_storage import supabase, BUCKET_NAME
from main import create_app

def migrate_documents():
    """Migrate existing documents from local storage to Supabase"""
    app = create_app()
    
    with app.app_context():
        documents = Document.query.all()
        bucket = supabase.storage.from_(BUCKET_NAME)
        
        migrated_count = 0
        failed_count = 0
        
        for doc in documents:
            # Skip if already migrated (file_path starts with course_id/)
            if '/' in doc.file_path and not doc.file_path.startswith('/'):
                print(f"Already migrated: {doc.filename}")
                continue
            
            # Check if local file exists
            if not os.path.exists(doc.file_path):
                print(f"Local file not found: {doc.file_path}")
                failed_count += 1
                continue
            
            try:
                # Read file data
                with open(doc.file_path, 'rb') as f:
                    file_data = f.read()
                
                # Upload to Supabase
                supabase_path = f"{doc.course_id}/{doc.stored_filename}"
                bucket.upload(
                    supabase_path, 
                    file_data, 
                    file_options={"content-type": f"application/{doc.file_type}"}
                )
                
                # Update database
                doc.file_path = supabase_path
                db.session.commit()
                
                # Optionally delete local file
                os.remove(doc.file_path)
                
                migrated_count += 1
                print(f"Migrated: {doc.filename} -> {supabase_path}")
                
            except Exception as e:
                print(f"Failed to migrate {doc.filename}: {str(e)}")
                failed_count += 1
                db.session.rollback()
        
        print(f"\nMigration complete: {migrated_count} migrated, {failed_count} failed")

if __name__ == '__main__':
    migrate_documents()