from http import HTTPStatus
from datetime import datetime
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.SupabaseManager import SupabaseManager

def handler(request):
    supabase = SupabaseManager()
    today = datetime.now().date().isoformat()
    try:
        # Delete showtimes before today
        response = supabase.supabase.table('showtimes').delete().lt('starts_at', today).execute()
        deleted_count = len(response.data) if hasattr(response, 'data') else 0
        return (HTTPStatus.OK, f"Deleted {deleted_count} deprecated showtimes.")
    except Exception as e:
        return (HTTPStatus.INTERNAL_SERVER_ERROR, f"Error: {e}")