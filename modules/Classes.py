from dataclasses import dataclass
from datetime import datetime
import requests
import time
from random import uniform
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.allocine.fr/',
    'DNT': '1',
}

class RateLimitedSession:
    def __init__(self, requests_per_second=1):
        self.session = requests.Session()
        self.last_request = 0
        self.min_delay = 1.0 / requests_per_second
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1.5,  # exponential backoff
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Add retry adapter to session
        self.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        self.session.headers.update(DEFAULT_HEADERS)
    
    def get(self, url, **kwargs):
        # Ensure minimum delay between requests
        now = time.time()
        delta = now - self.last_request
        if delta < self.min_delay:
            # Add small random delay
            time.sleep(self.min_delay - delta + uniform(0.1, 0.5))
        
        response = self.session.get(url, **kwargs)
        self.last_request = time.time()
        return response

@dataclass
class Cinema:
    id: str
    name: str
    latitude: float
    longitude: float

class Movie:
    def __init__(self, data) -> None:
        if not data:
            raise ValueError("Movie data is None")
            
        self.id = data.get("internalId", "")
        self.title = data.get("title", "Unknown Title")
        self.runtime = data.get("runtime", "")
        self.synopsis = data.get("synopsis", "")
        self.genres = data.get("genres", [])
        self.cast = data.get("cast", [])
        self.director = data.get("directors", "")
        self.affiche = data.get("poster", {}).get("url", "")
        
        try:
            self.affiche = data["poster"]["url"]
        except:
            self.affiche = "/static/images/nocontent.png"
            
        self.cast = []

        # Noms des acteurs
        for actor in data["cast"]["edges"]:
            if actor["node"]["actor"] == None: continue

            if actor["node"]["actor"]["lastName"] == None:
                actor["node"]["actor"]["lastName"] = ""
                
            if actor["node"]["actor"]["firstName"] == None:
                actor["node"]["actor"]["firstName"] = ""

            name = f'{actor["node"]["actor"]["firstName"]} {actor["node"]["actor"]["lastName"]}'
            name = name.lstrip()
            self.cast.append(name)

        # Nom du réalisateur
        if len(data["credits"]) == 0:
            self.director = "Inconnu"
        else:
            if data["credits"][0]["person"]["lastName"] == None:
                data["credits"][0]["person"]["lastName"] = ""
                
            if data["credits"][0]["person"]["firstName"] == None:
                data["credits"][0]["person"]["firstName"] = ""

            self.director = f'{data["credits"][0]["person"]["firstName"]} {data["credits"][0]["person"]["lastName"]}'
            self.director = self.director.lstrip()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.title}>"

class Showtime:
    def __init__(self, data, theather, movie:Movie) -> None:
        self.startsAt = datetime.fromisoformat(data['startsAt'])
        self.diffusionVersion = data['diffusionVersion']
        self.services = data["service"]
        self.theater:Theater = theather
        self.movie = movie

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.movie.title} startsAt={self.startsAt}>"

class Theater:
    _session = RateLimitedSession(requests_per_second=0.5)
    def __init__(self, data) -> None:
        self.name = data['name']
        self.id = data['internalId']
        self.location = data['location']
        self.latitude = data['latitude']
        self.longitude = data['longitude']
        self.url = data['url']

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"

    def get_showtimes(self, date: datetime, page: int = 1, showtimes: list = None) -> list[Showtime]:
        if showtimes is None:
            showtimes = []
        
        datestr = date.strftime("%Y-%m-%d")
        
        try:
            r = self._session.get(f"https://www.allocine.fr/_/showtimes/theater-{self.id}/d-{datestr}/p-{page}/")
            r.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed for theater {self.name} on {datestr} page {page}: {str(e)}")
            return showtimes  # return what we have so far
        
        try:
            data = r.json()

            if data.get("message") in ["no.showtime.error", "next.showtime.on"]:
                return showtimes
                
            if data.get('error'):
                print(f"API Error for theater {self.name}: {data}")
                return showtimes

            # Handle empty or invalid results
            if not data.get('results'):
                print(f"No results for theater {self.name} on {datestr}")
                return showtimes

            for result in data['results']:
                # Skip if movie data is missing or invalid
                if not result.get("movie"):
                    print(f"Missing movie data in result for theater {self.name}")
                    continue
                    
                try:
                    movie = Movie(result["movie"])
                except Exception as e:
                    print(f"Failed to parse movie data: {e}")
                    continue
                
                if data.get("message") in ["no.showtime.error", "next.showtime.on"]:
                    return showtimes
                
                if data.get('error'):
                    print(f"API Error for theater {self.name}: {data}")
                    return showtimes
                
                for movie in data['results']:
                    inst = Movie(movie["movie"])
                    movie_showtimes = movie["showtimes"].get("dubbed", []) + \
                                    movie["showtimes"].get("original", []) + \
                                    movie["showtimes"].get("local", []) + \
                                    movie["showtimes"].get("original_st", []) + \
                                    movie["showtimes"].get("multiple_st", [])

                    for showtime_data in movie_showtimes:
                        showtimes.append(Showtime(showtime_data, self, inst))
                
                if int(data['pagination']['page']) < int(data['pagination']["totalPages"]):
                    return self.get_showtimes(date, page + 1, showtimes)
        
        except Exception as e:
            print(f"Error processing showtimes for {self.name} on {datestr}: {e}")
            return showtimes

        return showtimes
    
    @staticmethod
    def new(query:str):
        r = requests.get(f"https://www.allocine.fr/_/localization_city/{query}")

        try:
            data = r.json()
        except:
            return {"error": True, "message": "Can't parse JSON", "content": r.content}

        if len(data["values"]["theaters"]) == 0:
            return {"error": True, "message": "Not found", "content": r.content}
        
        return Theater(data["values"]["theaters"][0]["node"])