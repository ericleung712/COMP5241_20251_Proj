from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_service_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables must be set")

supabase: Client = create_client(supabase_url, supabase_service_key)

# Bucket name for course documents
BUCKET_NAME = 'course-documents'