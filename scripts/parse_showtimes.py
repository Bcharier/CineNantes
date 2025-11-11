import json
import os
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.SupabaseManager import SupabaseManager

def parse_movie_data(movie_data: dict) -> dict:
    """Extract only needed fields from movie data"""
    
    # Return empty dict if movie_data is None
    if movie_data is None:
        return {
            "id": None,
            "title": "Unknown",
            "runtime": "",
            "synopsis": "",
            "genres": [],
            "poster_url": "",
            "director": "",
            "actors": [],
        }

    # Helper function to safely get actor name
    def get_actor_name(node):
        if not node or not node.get('actor'):
            return ''
        actor = node.get('actor', {})
        first = actor.get('firstName', '')
        last = actor.get('lastName', '')
        return f"{first} {last}".strip()

    # Helper function to safely get nested dict values
    def safe_get_nested(d: dict, *keys, default=None):
        if not isinstance(d, dict):
            return default
        for key in keys:
            d = d.get(key)
            if d is None:
                return default
        return d

    return {
        "id": safe_get_nested(movie_data, "internalId"),
        "title": safe_get_nested(movie_data, "title", default="Unknown"),
        "runtime": safe_get_nested(movie_data, "runtime", default=""),
        "synopsis": safe_get_nested(movie_data, "synopsis", default=""),
        "genres": [g.get("translate", "") for g in movie_data.get("genres", []) if g],
        "poster_url": safe_get_nested(movie_data, "poster", "url", default=""),
        "director": next((
            f"{safe_get_nested(c, 'person', 'firstName', default='')} {safe_get_nested(c, 'person', 'lastName', default='')}".strip()
            for c in movie_data.get("credits", [])
            if safe_get_nested(c, "position", "name") == "DIRECTOR"
        ), ""),
        "actors": [
            name for name in (get_actor_name(node) 
            for node in movie_data.get("cast", {}).get("nodes", []))
            if name
        ],
    }
def parse_showtime_data(showtime_data: dict) -> list[dict]:
    """Extract showtime information from all versions (original, dubbed, etc)"""
    showtimes = []
    for version in ["original", "multiple"]:
        for show in showtime_data.get(version, []):
            showtimes.append({
                "starts_at": show.get("startsAt"),
                "version": show.get("diffusionVersion"),
                "services": show.get("service", [])
            })
    return showtimes

def process_raw_files(raw_dir: str = "data/raw_showtimes"):
    """Process all raw JSON files and save to Supabase"""

    load_dotenv('.env')
    load_dotenv('.env.sample')

    supabase = SupabaseManager()

    for filename in os.listdir(raw_dir):
        if not filename.endswith(".json"):
            continue
            
        # Get theater_id from filename (e.g., P0052_2025-11-05.json)
        theater_internal_id = filename.split('_')[0]
        
        # Add encoding='utf-8' when opening the file
        with open(os.path.join(raw_dir, filename), encoding='utf-8') as f:
            try:
                raw_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing {filename}: {e}")
                continue
        
        # First ensure theater exists
        theater_data = next(
            t for t in json.loads(os.environ.get("THEATERS", "[]"))
            if t["id"] == theater_internal_id
        )
        theater_result = supabase.upsert_theater(theater_data)
        theater_id = theater_result.data[0]['id']
        
        # Process each movie and its showtimes
        for result in raw_data.get("results", []):
            try:
                # Parse and store movie
                movie_data = parse_movie_data(result.get("movie", {}))
                movie_result = supabase.upsert_movie(movie_data)
                movie_id = movie_result.data[0]['id']
                
                # Parse and store showtimes
                showtimes_data = parse_showtime_data(result.get("showtimes", {}))
                if showtimes_data:
                    # Add movie_id and theater_id to each showtime dict
                    for show in showtimes_data:
                        show['movie_id'] = movie_id
                        show['theater_id'] = theater_id
                    supabase.insert_showtimes(showtimes_data)
                    
                print(f"Processed movie {movie_data['title']} with {len(showtimes_data)} showtimes")
                
            except Exception as e:
                print(f"Error processing movie: {str(e)}")
                continue

if __name__ == "__main__":
    process_raw_files()