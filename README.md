# Plex Playlist Sync

**This a fork of the original project here https://github.com/rnagabhyrava/plex-playlist-sync**

Create spotify playlists in your plex account using tracks from your server and keeps plex playlists in sync with original playlists. 

This DOES NOT download any songs from anywhere.

## Features
* From Spotify: Sync all of the given user account's public playlists to plex
* Option to write missing songs as a csv
* Option to include poster and description in playlists.

## New features in this fork

- Ability to copy playlists to multiple managed plex users
- Add Spotify items by their IDs
- Option to add playlist by their Spotify categories
- Improved song matching
- **Removed Deezer integration for now** go to original project for this


## Prerequisites
### Plex
* Plex server's host and port
* Plex token - [Don't know where to find it?](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

### To use Spotify sync
* Spotify client ID and client secret - Can be obtained from [spotify developer](https://developer.spotify.com/dashboard/login)
* Spotify user ID - This can be found on spotify [account page](https://www.spotify.com/us/account/overview/)
* Sportify Redirect Uri - Can just be http://localhost

### Multiple plex users

You need to get the individual plex tokens for each plex user. To get each one, you need to login with each user in the Plex web interface and click on a music artist. Then go to the developer console (F12 on chrome), navigate to the network tab and click on one of the names you should see a value similar to this https://i.imgur.com/ainu7v1.png

Copy that and add it to the docker `PLEX_TOKEN_USERS` variable.

### Spotify playlist categories

In addition to adding playlists by their IDs, you can use the categories Spotify define and maintain. For example spotify have a category called "top" which will include playlists like "Global top 50", "Official Charts". Rock will include "Rocktail hour", "Rock Party" etc. Throwback will include "Born in the 90s", "Throwback Thursday". It keeps the playlists fresh and dynamic.

** Warning - Each category can contain around 20 playlists **

The values to use are below:

```python
throw # Throwback playlists
featured # Spotify featured playlists
top # Spotify top charts playlists
hiphop
indie
mood
party
dance
rnb
rock
home
```



## Docker Setup
You need either docker or docker with docker-compose to run this. Docker images are available on [the hub](https://hub.docker.com/r/rnagabhyrava/plexplaylistsync/tags) for amd64, arm64 and arm/v7 and will be auto pulled based on your platform.

Configure the parameters as needed. Plex URL and TOKEN are mandatory and either one of the Options (1,2,3) fields are required.

### Docker Compose

docker-compose.yml can be configured as follows. See [docker-compose-example.yml](https://github.com/rnagabhyrava/plex-playlist-sync/blob/main/docker-compose-example.yml) for example
```
version: "2.1"
services:
  playlistSync:
    image: silkychap/plex-playlist-sync:latest
    container_name: playlistSync
    # optional only if you chose WRITE_MISSING_AS_CSV=1 in env
    volumes:
      - <Path where you want to write missing tracks>:/data
    environment:
      - PLEX_URL= <your local plex url>
      - PLEX_TOKEN=<your plex token> # Owners/Primary user's plex token
      - plex_token_others=<managed plex tokens> # Other managed user's plex tokens
      - plex_min_songs=<min songs number per playlist> # Minimum number of songs for a playlist to be created
      - WRITE_MISSING_AS_CSV=<1 or 0> # Default 0, 1 = writes missing tracks from each playlist to a csv
      - APPEND_SERVICE_SUFFIX=<1 or 0> # Default 1, 1 = appends the service name to the playlist name
      - ADD_PLAYLIST_POSTER=<1 or 0> # Default 1, 1 = add poster for each playlist
      - ADD_PLAYLIST_DESCRIPTION=<1 or 0> # Default 1, 1 = add description for each playlist
      - APPEND_INSTEAD_OF_SYNC=0 # Default 0, 1 = Sync tracks, 0 = Append only
      - SECONDS_TO_WAIT=84000
      - SPOTIFY_CLIENT_ID=<your spotify client id>
      - SPOTIFY_CLIENT_SECRET=<your spotify client secret>
      - SPOTIFY_USER_ID=<your spotify user id>
      - SPOTIFY_REDIRECT_URI=http://localhost
      - SPOTIFY_PLAYLIST_IDS=<spotify playlist ids> # List of playlist ids
      - SPOTIFY_CATEGORIES=<spotify category names> # List of categories to add playlists from
    restart: unless-stopped

```
And run with :
```
docker-compose up
```

### Issues
Something's off? See room for improvement? Feel free to open an issue with as much info as possible. Cheers!
