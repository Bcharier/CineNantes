from flask import Flask, render_template, request
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
from modules.SupabaseManager import SupabaseManager

# Debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv(".env")
load_dotenv(".env.sample")

WEBSITE_TITLE = os.environ.get("WEBSITE_TITLE", "Ciné Nantes")

# Initialize Flask and Supabase
app = Flask(__name__)
supabase = SupabaseManager()


def translate_day(day: int) -> str:
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    return days[day]

def translate_month(month: int) -> str:
    months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    return months[month - 1]

@app.route('/')
def home():
    delta = request.args.get("delta", default=0, type=int)
    if delta > 6: delta = 6
    if delta < 0: delta = 0

    # Build dates for navigation
    dates = []
    for i in range(0,7):
        day = datetime.today() + timedelta(i)
        dates.append({
            "jour": translate_day(day.weekday()),
            "chiffre": day.day,
            "mois": translate_month(day.month),
            "choisi": i==delta,
            "index": i
        })

    # Get date range for query
    target_date = datetime.today() + timedelta(days=delta)
    start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    # Get showtimes from Supabase
    showtimes = supabase.get_showtimes_for_date(start_date.isoformat(), end_date.isoformat())
    

    # Process into template-friendly format
    movies_dict = {}
    for show in showtimes:
        movie = show['movie']
        theater = show['theater']
        
        if movie['title'] not in movies_dict:
            movies_dict[movie['title']] = {
                "id": movie['id'],
                "title": movie['title'],
                "duree": movie['runtime'],
                "genres": movie['genres'],
                "casting": movie['actors'], 
                "realisateur": movie['director'],
                "synopsis": movie['synopsis'],
                "affiche": movie['affiche'],
                "director": movie['director'],
                "url": movie['url'],
                "seances": {}
            }
        
        if theater['name'] not in movies_dict[movie['title']]["seances"]:
            movies_dict[movie['title']]["seances"][theater['name']] = []
        
        movies_dict[movie['title']]["seances"][theater['name']].append(
            datetime.fromisoformat(show['starts_at']).strftime("%H:%M")
        )

    # Sort showtimes for each theater by time
    for movie in movies_dict.values():
        for theater_name, seances in movie["seances"].items():
            seances.sort()    

    # Sort movies by title
    films = sorted(
        movies_dict.values(), 
        key=lambda x: x["title"], 
    )

    theaters = supabase.get_theaters()

    return render_template(
        'index.html',
        page_actuelle='home',
        films=films,
        dates=dates,
        theaters=theaters,
        theater_urls={t['name']: t['url'] for t in theaters},
        website_title=WEBSITE_TITLE,
    )

if __name__ == "__main__":
    app.run(debug=True)