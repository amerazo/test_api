import os
import base64
import json
import requests
from dotenv import load_dotenv
from django.db import transaction


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tempo_project.settings")


import django
django.setup()


from tempo_app.models import Artist
from decouple import config

load_dotenv()

CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

def get_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"
    
    query_url = url + "?" + query  
    result = requests.get(query_url, headers=headers)  
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]
    
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"  
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def fetch_and_save_artists():
    token = get_token()
    if not token:
        print("Failed to get Spotify token")
        return

    artists_to_fetch = ["ACDC", "Ed Sheeran", "Taylor Swift"] 
    
    with transaction.atomic():
        for artist_name in artists_to_fetch:
            result = search_for_artist(token, artist_name)
            if result:
                artist, created = Artist.objects.get_or_create(name=artist_name)
                if created:
                    print(f"Saved artist: {artist_name}")
                 

if __name__ == "__main__":
    fetch_and_save_artists()
