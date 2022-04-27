# soupyspotify

# Description
Spotify's weekly release radar playlist is commonly inaccurate, including older releases and omitting new releases by lesser known followed artists. 
This project solves this issue by generating a weekly playlist covering every artist your spotify account follows.

# Main Features
- generate_weekly_playlist(): requests every release from every artist your spotify account follows and then generates a playlist of songs and albums from the past week.
- create_discover_weekly_backup(): generates a copy of the currently available discover weekly playlist

# Read before running
This code makes a high volume of requests to the spotify api. During first run of the code, artist count should be limited to minimum to ensure no issues that result in 

# Installation
After the repository is cloned to your directory of choice, you will need to set up the authorization credentials. Follow the OAuth setup below.

# OAuth setup
1. Go to the [Spotify Developer Portal](https://developer.spotify.com/dashboard/login). Log in or create an account.
2. On the Spotify Dashboard, create an app.
3. Select Edit Settings and set Redirect URI as: http://localhost:1084  (If you use a different port, make sure to update the code/dashboard redirect appropriately)
4. Copy the "Client ID" and "Client Secret" into respective fields of rsbautomator. These can also be stored as environment variables.
5. First time running the code, spotify will request a browser login authentication. Log into the account you wish to generate weekly playlists on.

# Troubleshooting
1. If OAuth is causing errors, try deleting the .cache file from the program directory and try again.
