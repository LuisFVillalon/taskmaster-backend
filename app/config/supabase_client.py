import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url:
    raise RuntimeError("SUPABASE_URL is not set. Add it to .env.")
if not key:
    raise RuntimeError("SUPABASE_KEY is not set. Add it to .env.")

supabase = create_client(url, key)