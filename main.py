from calendar import week
from datetime import timedelta
from datetime import date
from datetime import datetime
from ftplib import all_errors
from sys import breakpointhook
from xml.dom.minidom import AttributeList
import spotipy
from math import ceil
from spotipy.oauth2 import SpotifyOAuth
import os
import os.path
import json
from dotenv import load_dotenv

load_dotenv('local.env')

scope = "user-follow-read, user-top-read, playlist-modify-private"
client_id = "12c6e5ab3601483db07e0247b5888d02"
client_secret = os.environ['CLIENT_SECRET']
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


def get_all_artists_albums(num_artists): #generates list of all followed artist uris to provide artist uri for album/single api requests
    all_albums = []
    loops = -1
    if num_artists != -1:
        loops = ceil(num_artists / 50)
    if loops == 0:
        return all_albums

    got_all_artists = False
    uri = None
    i = 0
    while (not got_all_artists) and ((loops == -1) or (i < loops)): #parameter loops to limit api requests in batches of 50, set i ~ ((i == -1) or~
        i += 1
        results = sp.current_user_followed_artists(limit=50, after=uri)
        if not results['artists']['items']:
            got_all_artists = True
        for idx, item in enumerate(results['artists']['items']):
            #print("processing an artist")
            uri = item['uri'][15:]
            all_artist_albums = get_artist_albums(uri)
            for album in all_artist_albums:
                all_albums.append(album)
    return all_albums


def fetch_album_cache(num_artists):
    file_exists = os.path.exists('album_cache.json')
    if file_exists == False:
        f = open("album_cache.json", "w")
        all_albums = get_all_artists_albums(num_artists)
        dictionary = {
            "all_albums" : all_albums,
        }
        f.write(json.dumps(dictionary))
        return all_albums
    else:
        f = open('album_cache.json', "r")
        dictionary = json.load(f)
        all_albums = dictionary["all_albums"]
        return all_albums


def recent_album_releases(num_artists): #input -1 for all artists
    all_albums = fetch_album_cache(num_artists) #input -1 for all artists
    all_albums.sort(key=get_date, reverse=True)
    return all_albums


def isRelevant(albumName: str) -> bool: #checks if current album name contains a filter word, (@@repurpose to filter Remix into separate playlist)
    filters = ['TikTok', 'Playlist', 'Indie', 'Remix', 'Trending']
    for filter in filters:
        if filter in albumName:
            return False
    return True


def album_uri_check(album_uris, album):
    for uri in album_uris:# skips if album uri already exists
            if album["uri"] == uri: 
                return True
                

def artist_name_parsing(album, artist_names):#separates out artist names for printing
    for artist in album["artists"]: 
           return artist_names.append(artist['name'])



def print_top_albums(all_albums, count):
    album_uris = []
    x = 0 #print counter set to 0
    duplicate_uri = 0 #counter
    for idx, album in enumerate(all_albums):  # these lines create a table of artist names
        artist_names = []
        skip = False
        skip = album_uri_check(album_uris, album)
        for artist in album["artists"]: 
            artist_names.append(artist['name'])
        if skip:
            duplicate_uri += 1
            continue
        album_uris.append(album['uri'])
        print(x, " ~ ", album['name'], " ~ ", ", ".join(artist_names), " ~ ", album['album_type'], "(", album['total_tracks'], ")", " ~ ", album['release_date'], " ~ ", album['id'])
        x+=1      
        if x == count:
            print("Duplicate URI:", duplicate_uri)
            break


def get_album_track_uri(album): #using album uri, makes an api call for all tracks on album and returns track uris
    tracks = sp.album_tracks(album['uri'], limit=25, offset=0, market='US')
    track_uris = []
    for track in tracks['items']:
        track_uris.append(track['uri'])
    return track_uris

def get_album_track(album): # list of track dictionaries
    album_tracks = sp.album_tracks(album['uri'], limit=25, offset=0, market='US')
    tracks = []
    for track in album_tracks['items']:
        tracks.append(track)
    return tracks

def release_week_check(album, num_days):#number of days 
    release_week = timedelta(days=num_days)
    album_iso_date = date.fromisoformat(album['release_date'])
    current_date = date.today()
    if (album_iso_date + release_week) <= current_date: #checks if release is older than 1 week
        return None
    else:
        track_uris = get_album_track_uri(album)
        return track_uris


def recent_release_track_uri(all_albums, num_days, count_limit):# num_days limits results to days before current date. count limit limts overall count
    album_uris = []
    track_uris = []
    x = 0 #print counter set to 0
    duplicate_uri = 0 #counter
    for idx, album in enumerate(all_albums):  # these lines create a table of artist names
        artist_names = []
        skip = False
        skip = album_uri_check(album_uris, album)
        for artist in album["artists"]: 
            artist_names.append(artist['name'])
        if skip:
            duplicate_uri += 1
            continue
        album_uris.append(album['uri'])
        album_track_uris = release_week_check(album, num_days)
        if album_track_uris == None:
            print(album['release_date'])
            break
        for track_uri in album_track_uris:
            track_uris.append(track_uri)
        print(x, " ~ ", album['name'], " ~ ", ", ".join(artist_names), " ~ ", album['album_type'], "(", album['total_tracks'], ")", " ~ ", album['release_date'], " ~ ", album['id'])
        x+=1      
        if x == count_limit:
            print("Duplicate URI:", duplicate_uri)
            break
    return track_uris


def generate_weekly_playlist():
    all_albums = recent_album_releases(-1)
    track_uris = recent_release_track_uri(all_albums, 6, 200)
    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d")
    playlist_name = date.today()
    user_id = sp.me()['id']
    new_playlist = sp.user_playlist_create(user_id, date_time, public=False, collaborative=False, description='New music for the week ending on ' + date_time)
    all_items_on_playlist = int(len(track_uris) / 100) + ((len(track_uris) % 100) > 0)
    for i in range(0, all_items_on_playlist):
        sp.playlist_add_items(new_playlist['id'], track_uris[100*i:100*(i+1)], position=None)


all_albums = recent_album_releases(-1)
print_top_albums(all_albums, 500)
#generate_weekly_playlist()

#all_albums = recent_album_releases(-1)
#weekly_playlist_uris = recent_release_track_uri(all_albums, 6, 200)
#print(weekly_playlist_uris)
#print_top_albums(all_albums, 500)