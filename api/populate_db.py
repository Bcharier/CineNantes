from http import HTTPStatus
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.populate_db import main


def handler(request):

    # Get secret from environment
    expected_secret = os.environ.get("API_SECRET")
    # Get secret from request (header or query param)
    provided_secret = None
    if request:
        provided_secret = request.headers.get("x-api-secret") or request.args.get("secret")
    if expected_secret is None or provided_secret != expected_secret:
        return (HTTPStatus.FORBIDDEN, "Forbidden: Invalid or missing API secret.")

    try:
        main()
        return (HTTPStatus.OK, "Database populated successfully.")
    except Exception as e:
        return (HTTPStatus.INTERNAL_SERVER_ERROR, f"Error: {e}")