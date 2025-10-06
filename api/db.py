import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.supabase = create_client(self.url, self.key)
    
    # Copy all the same methods from your existing db.py, but remove st.error calls
    def get_user_profile(self, user_id):
        try:
            response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None
    
    # Add all other methods here, replacing st.error with print...