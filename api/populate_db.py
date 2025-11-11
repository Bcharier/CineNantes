from http import HTTPStatus

def handler(request):
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.populate_db import main

    try:
        main()
        return (HTTPStatus.OK, "Database populated successfully.")
    except Exception as e:
        return (HTTPStatus.INTERNAL_SERVER_ERROR, f"Error: {e}")