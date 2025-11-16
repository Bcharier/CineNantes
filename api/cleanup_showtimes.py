from http import HTTPStatus
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.cleanup_showtimes import cleanup_deprecated_showtimes

def handler(request):
    expected_secret = os.environ.get("API_SECRET")
    provided_secret = None
    if request:
        provided_secret = request.headers.get("x-api-secret") or request.args.get("secret")
    if expected_secret is None or provided_secret != expected_secret:
        return (HTTPStatus.FORBIDDEN, "Forbidden: Invalid or missing API secret.")

    try:
        deleted_count = cleanup_deprecated_showtimes()
        return (HTTPStatus.OK, f"Deleted {deleted_count} deprecated showtimes.")
    except Exception as e:
        return (HTTPStatus.INTERNAL_SERVER_ERROR, f"Error: {e}")