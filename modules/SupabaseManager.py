from datetime import datetime
import os
from supabase import create_client, Client
from typing import List, Dict, Any

class SupabaseManager:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("PUBLIC_SUPABASE_ANON_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or PUBLIC_SUPABASE_ANON_KEY environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def upsert_theater(self, theater_data: dict) -> dict:
        """Insert or update theater data using internal_id as unique constraint"""
        theater_insert = {
            'internal_id': str(theater_data['id']),
            'name': theater_data['name'],
            'latitude': theater_data.get('latitude'),
            'longitude': theater_data.get('longitude'),
            'url': theater_data.get('url')
        }
        
        return self.supabase.table('theaters').upsert(
            theater_insert,
            on_conflict='internal_id'
        ).execute()

    def upsert_movie(self, movie_data: dict) -> dict:
        """Insert or update movie data using allocine_id as unique constraint"""
        movie_insert = {
            'allocine_id': str(movie_data['id']),
            'title': movie_data['title'],
            'runtime': movie_data.get('runtime'),
            'synopsis': movie_data.get('synopsis'),
            'genres': ','.join(movie_data.get('genres', [])),
            'actors': ','.join(movie_data.get('actors', [])),
            'director': movie_data.get('director'),
            'affiche': movie_data.get('poster_url'),
            'url': f"https://www.allocine.fr/film/fichefilm_gen_cfilm={movie_data['id']}.html",
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('movies').upsert(
                movie_insert,
                on_conflict='allocine_id'
            ).execute()
            return result
        except Exception as e:
            print(f"Error upserting movie {movie_data['title']}: {str(e)}")
            return {}

    def insert_showtimes(self, showtime_data: list) -> dict:
        """Insert or update multiple showtimes"""
        formatted_showtimes = []
        for show in showtime_data:
            formatted_show = {
                'movie_id': show['movie_id'],
                'theater_id': show['theater_id'],
                'starts_at': show['starts_at'],
                'diffusion_version': show.get('version', ''),
                'services': ','.join(show.get('services', [])) if isinstance(show.get('services'), list) else ''
            }
            formatted_showtimes.append(formatted_show)

        if not formatted_showtimes:
            return {'data': []}

        return self.supabase.table('showtimes').upsert(
            formatted_showtimes,
            on_conflict='movie_id,theater_id,starts_at'  # Prevent duplicate showtimes
        ).execute()
    
    def get_showtimes_for_date(self, start_date: str, end_date: str) -> list:
        """Get all showtimes between start_date and end_date with movie and theater data"""
        return self.supabase.rpc(
            'get_showtimes_with_details',
                {
                    'start_timestamp': start_date,
                    'end_timestamp': end_date
                }
            ).execute().data
    
    def get_theaters(self) -> list:
        """Get all theaters from the database."""
        response = self.supabase.table('theaters').select('*').execute()
        return response.data if hasattr(response, 'data') else []