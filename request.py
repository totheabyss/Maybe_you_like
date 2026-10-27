from dotenv import load_dotenv
import os
import requests
import hashlib
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
LASTFM_KEY = os.getenv("LASTFM_KEY")

def get_artist_info(artist):
    params = {
        "method" : "artist.getInfo",
        "artist" :  artist,
        "api_key" : LASTFM_KEY,
        "format" : "json"
        }
    response = requests.get("https://ws.audioscrobbler.com/2.0/",params=params)
    response.raise_for_status()
    data = response.json()
    if data.get("error") == 6:
        raise FileNotFoundError("Artist not found")
    
    artist_name = data["artist"]["name"]
    artist_id = data["artist"].get("mbid")
    #bandas q vierem sem mbid eu crio um hash pra identificar
    if artist_id == None:
        artist_id = hashlib.sha256(artist_name.lower().encode()).hexdigest()
    artist_listeners = data["artist"]["stats"]["listeners"]
    return {
    "name": artist_name,
    "id": artist_id,
    "listeners": artist_listeners
    }
    

def get_recommendation(artist):
    params2 = {
        "method" : "artist.getSimilar",
        "artist" :  artist,
        "api_key" : LASTFM_KEY,
        "format" : "json"
        }
    response2 = requests.get("https://ws.audioscrobbler.com/2.0/",params=params2)
    response2.raise_for_status()
    data2 = response2.json()
    
    similars = []
    position = 0
    nomes = []
    for artist in data2["similarartists"]["artist"]:
        name = artist["name"]
        match = artist["match"]
        position += 1
        similar = {"name":name, "match" : match, "position" : position}
        
        if position > 20 and position < 60:
            nomes.append(name)
            similars.append(similar)
            
    with ThreadPoolExecutor(max_workers=5) as executor:
        resultados = list(executor.map(get_artist_info, nomes))
        for similar, resultado in zip(similars, resultados):
            similar["listeners"] = resultado["listeners"]
            similar["id"] = resultado["id"]
    return similars
    
