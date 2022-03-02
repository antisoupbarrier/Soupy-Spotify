from ftplib import all_errors
from sys import breakpointhook
from xml.dom.minidom import AttributeList
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os.path
import json

scope = "user-follow-read"
client_id = "12c6e5ab3601483db07e0247b5888d02"
client_secret = "4afea61c3e814e209dc96d29976d77c1"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret = client_secret,redirect_uri="http://localhost:1084"))

uri=None

def get_date(artist_albums):
    return artist_albums['release_date']


def get_artist_albums(uri): #uses artist uri to collect all artist albums/singles released
    i = 0
    all_artist_albums = []
    got_all_artist_albums = False
    while not got_all_artist_albums:
        artist_albums = sp.artist_albums(uri, album_type="single,album", country='US', limit=20, offset=(i*20))
        if artist_albums['items']:
            i += 1
            for album in artist_albums['items']:
                all_artist_albums.append(album)
        else:
            got_all_artist_albums = True
    return all_artist_albums


def get_all_artists_albums(loops): #generates list of all followed artist uris to provide artist uri for album/single api requests
    # loops = number_artists/50
    all_albums = []
    got_all_artists = False
    uri = None
    i = 0
    while (not got_all_artists) and ((loops == -1) or (i < loops)): #parameter loops to limit api requests in batches of 50, set i ~ ((i == -1) or~
        i += 1
        results = sp.current_user_followed_artists(limit=50, after=uri)
        if not results['artists']['items']:
            print("resultsbreak")
            got_all_artists = True
        for idx, item in enumerate(results['artists']['items']):
            #print("processing an artist")
            uri = item['uri'][15:]
            all_artist_albums = get_artist_albums(uri)
            for album in all_artist_albums:
                all_albums.append(album)
    return all_albums


def fetch_album_cache(loops):
    file_exists = os.path.exists('album_cache1.json')
    if file_exists == False:
        f = open("album_cache1.json", "w")
        all_albums = get_all_artists_albums(loops)
        dictionary = {
            "all_albums" : all_albums,
        }
        f.write(json.dumps(dictionary))
        return all_albums
    else:
        f = open('album_cache1.json', "r")
        dictionary = json.load(f)
        all_albums = dictionary["all_albums"]
        return all_albums


def isRelevant(albumName: str) -> bool: #checks if current album name contains a filter word
    filters = ['TikTok', 'Playlist', 'Indie', 'Remix', 'Trending']
    for filter in filters:
        if filter in albumName:
            return False
    return True



all_albums = fetch_album_cache(-1) #input -1 for all artists
all_albums.sort(key=get_date, reverse=True)
album_uris = []
x = 0 #print counter set to 0
removed_results = 0 #filtered results
duplicate_uri = 0 #counter
for idx, album in enumerate(all_albums):  # these lines create a table of artist names
    artist_names = []
    skip = False
    for uri in album_uris:# skips if album uri already exists
        if album["uri"] == uri: 
            skip = True
            duplicate_uri += 1
    for artist in album["artists"]: #separates out artist names for printing
        artist_names.append(artist['name'])
    if skip:
        continue
    album_uris.append(album['uri'])
    #if isRelevant(album['name']):
    print(x, " ~ ", album['name'], " ~ ", ", ".join(artist_names), " ~ ", album['album_type'], "(", album['total_tracks'], ")", " ~ ", album['release_date'], " ~ ", album['id'])
    x+=1      
    #else:
    #    removed_results += 1
    if x == 500:
        print("Results removed: ", removed_results, " - Duplicate URI: ", duplicate_uri)
        break