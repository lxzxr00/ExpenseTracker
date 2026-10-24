import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"],
)

print(supabase.auth.get_session())