from datetime import datetime, timedelta
import json
import os
import sys
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.Classes import RateLimitedSession, DEFAULT_HEADERS

def fetch_theater_showtimes(theater_id: str, date: datetime, session: RateLimitedSession) -> dict:
    """Fetch raw JSON response for a theater's showtimes on a specific date."""
    datestr = date.strftime("%Y-%m-%d")
    url = f"https://www.allocine.fr/_/showtimes/theater-{theater_id}/d-{datestr}/"
    
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return {}
    
def fetch_all_showtimes_paginated(theater_id: str, date: datetime, session: RateLimitedSession) -> dict:
    """Fetch all paginated showtimes for a theater and date, returns a combined raw_data dict."""
    datestr = date.strftime("%Y-%m-%d")
    all_results = []
    page = 1
    first_response = None

    while True:
        url = f"https://www.allocine.fr/_/showtimes/theater-{theater_id}/d-{datestr}/p-{page}/"
        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            break

        if first_response is None:
            first_response = data  # Save the first response for metadata

        results = data.get("results", [])
        all_results.extend(results)

        pagination = data.get("pagination", {})
        current_page = int(pagination.get("page", page))
        total_pages = int(pagination.get("totalPages", page))
        if current_page >= total_pages:
            break
        page += 1

    # Return a raw_data dict similar to the original API response, but with all results
    if first_response is None:
        return {}
    first_response["results"] = all_results
    return first_response

def main():
    # Create output directory
    os.makedirs("data/raw_showtimes", exist_ok=True)
    for file in glob.glob("data/raw_showtimes/*"):
        os.remove(file)
    
    # Load theater IDs from .env.sample
    with open(".env.sample") as f:
        theaters_json = json.loads(f.read().split("THEATERS=")[1])
    
    # Initialize rate-limited session
    session = RateLimitedSession(requests_per_second=0.5)  # 2 second delay between requests
    
    # Fetch next 7 days for each theater
    for theater in theaters_json:
        theater_id = theater["id"]
        theater_name = theater["name"]
        
        print(f"\nFetching showtimes for {theater_name} ({theater_id})")
        
        for i in range(7):
            date = datetime.today() + timedelta(days=i)
            datestr = date.strftime("%Y-%m-%d")
            
            print(f"  Fetching {datestr}...", end="", flush=True)
            
            # Fetch data
            raw_results = fetch_all_showtimes_paginated(theater_id, date, session)
            if not raw_results:
                print(" ERROR")
                continue
            
            # Save raw JSON
            filename = f"data/raw_showtimes/{theater_id}_{datestr}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(raw_results, f, ensure_ascii=False, indent=2)
            
            print(f" Saved to {filename}")

if __name__ == "__main__":
    main()