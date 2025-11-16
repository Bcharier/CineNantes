import sys
import os
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.SupabaseManager import SupabaseManager

def cleanup_deprecated_showtimes():
    supabase = SupabaseManager()
    today = datetime.now().date().isoformat()
    response = supabase.supabase.table('showtimes').delete().lt('starts_at', today).execute()
    deleted_count = len(response.data) if hasattr(response, 'data') else 0
    return deleted_count

def main():
    try:
        deleted = cleanup_deprecated_showtimes()
        print(f"Deleted {deleted} deprecated showtimes.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()