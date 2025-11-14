from http import HTTPStatus
from datetime import datetime
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.SupabaseManager import SupabaseManager

def handler(request):
    # Get secret from environment
    expected_secret = os.environ.get("API_SECRET")
    # Get secret from request (header or query param)
    provided_secret = None
    if request:
        provided_secret = request.headers.get("x-api-secret") or request.args.get("secret")
    if expected_secret is None or provided_secret != expected_secret:
        return (HTTPStatus.FORBIDDEN, "Forbidden: Invalid or missing API secret.")

    supabase = SupabaseManager()
    today = datetime.now().date().isoformat()
    try:
        # Delete showtimes before today
        response = supabase.supabase.table('showtimes').delete().lt('starts_at', today).execute()
        deleted_count = len(response.data) if hasattr(response, 'data') else 0
        return (HTTPStatus.OK, f"Deleted {deleted_count} deprecated showtimes.")
    except Exception as e:
        return (HTTPStatus.INTERNAL_SERVER_ERROR, f"Error: {e}")
