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


def get_date(artist_albums):
    return artist_albums['release_date']

uri=None




#all_albums = []

#for i in range(0,1):
#    results = sp.current_user_followed_artists(limit=50, after=uri)
#    for idx, item in enumerate(results['artists']['items']):
#        artist_name = item['name']
#        artist_popularity = item['popularity']
#        uri = item['uri'][15:]
        #print(idx+50*i, artist_name," - ", uri, "popularity:", artist_popularity)
#        artist_albums = sp.artist_albums(uri, album_type=None, country='US', limit=4, offset=0)
        #artist_albums['items'].sort(key=get_date, reverse=True)
#        for album in artist_albums['items']:
            #album_name = album['name']
            #album_id = album['id']
            #album_release_date = album['release_date']
#            all_albums.append(album)
            #print(f"{artist_name} - {album_name} - {album_release_date}")   


#create new file: album_cache.json
#f = open("album_cache.json", "w")
#f.write(str(all_albums))

file_exists = os.path.exists('album_cache.json')
if file_exists == False:
    f = open("album_cache.json", "w")
    all_albums = []
    got_all_artists = False
    #ii = 0
    while (not got_all_artists):# and (ii < 1): loop limiter
        #ii += 1
        results = sp.current_user_followed_artists(limit=50, after=uri)
        print("got all artists")
        if not results['artists']['items']:
            print("resultsbreak")
            got_all_artists = True
        for idx, item in enumerate(results['artists']['items']):
            print("processing an artist")
            uri = item['uri'][15:]
            i = 0
            got_all_albums = False
            while not got_all_albums:
                print("getting artist albums")
                artist_albums = sp.artist_albums(uri, album_type="single,album", country='US', limit=20, offset=(i*20))
                #print(artist_albums['items'])
                if artist_albums['items']:
                    print("more albums")
                    i += 1
                    for album in artist_albums['items']:
                        all_albums.append(album)
                        print("appended album")
                else:
                    got_all_albums = True
                    print("next artist~~~~~~~~~~~~~~~~~~~~~")
                    break
    dictionary = {
        "all_albums" : all_albums,
    }
    f.write(json.dumps(dictionary))
else:
    f = open('album_cache.json', "r")
    dictionary = json.load(f)
    all_albums = dictionary["all_albums"]
####

all_albums.sort(key=get_date, reverse=True)
album_uris = []
x = 0 #print counter set to 0
poop = 0 #filtered results
duplicate_uri = 0
for idx, album in enumerate(all_albums):  # these lines create a table of artist names
    artist_names = []
    skip = False
    for uri in album_uris:
        if album["uri"] == uri:
            skip = True
            duplicate_uri += 1
    for artist in album["artists"]:
        if ("Various Artists") in artist['name']:
            skip = True
        artist_names.append(artist['name'])
    if skip:
        continue
    album_uris.append(album['uri'])
    if not (("TikTok" in album['name']) \
        or ("Playlist" in album['name']) \
        or ("Indie" in album['name']) \
        or ("Remix" in album['name']) \
        or ("Trending" in album['name']) \
        ):
        print(x, " ~ ", album['name'], " ~ ", ", ".join(artist_names), " ~ ", album['album_type'], "(", album['total_tracks'], ")", " ~ ", album['release_date'], " ~ ", album['id'])
        x+=1
        
    else:
        poop += 1
       # print("poop")
        #print(x)
    if x == 100:
        print(album)
        print("Results removed: ", poop, " - Duplicate URI: ", duplicate_uri)
        break