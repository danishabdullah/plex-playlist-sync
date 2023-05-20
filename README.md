# Plex Playlist Sync

Create spotify and deezer playlists in your plex account using tracks from your server and keeps plex playlists in sync with original playlists. 

This DOES NOT download any songs from anywhere.

## Features
* From Spotify: Sync all of the given user account's playlists to plex
* From Deezer: Sync all of the given user account's public playlists and/or any given public playlist IDs to plex
* --- New ---
* Option to write missing songs as a csv
* Option to include poster and description in playlists.

## Prerequisites
### Plex
* Use:
  * Plex Username and Password
  * Plex Server Name you wish to sync with 
* Or:
    * Plex server's host and port
    * Plex token - [Don't know where to find it?](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

### To use Spotify sync
* Spotify client ID and client secret - Can be obtained from [spotify developer](https://developer.spotify.com/dashboard/login)
* Spotify user ID - This can be found on spotify [account page](https://www.spotify.com/us/account/overview/)
* Spotify Redirect URI: Will allways be http://localhost:8888/callback

### To use Deezer sync
* Deezer profile ID of the account from which playlists need to sync from
  * Login to deezer.com
  * Click on your profile
  * Grab the profile ID from the URL
  *  Example: https://www.deezer.com/us/profile/9999999 - Here 9999999 is the profile ID
OR
* Get playlists IDs of playlists you want to sync
  *  Example: https://www.deezer.com/us/playlist/1313621735 - Here 1313621735 is the playlist ID

## Docker Setup
You need either docker or docker with docker-compose to run this. Docker images are available on [the hub](https://hub.docker.com/repository/docker/dregsozworld/plex_playlist_sync/tags?page=1&ordering=last_updated) for amd64, arm64 and arm/v7 and will be auto pulled based on your platform.

Configure the parameters as needed. Plex URL and TOKEN are mandatory and either one of the Options (1,2,3) fields are required.

### Docker Run

```
docker run -d \
  --name playlistSync \
  -p 8888:8888/tcp \
  -v <directory where csv stored>:/data \
  -v <directory to store spotify keys>:/caches \
  -e PLEX_URL=<Your local plex url> \
  -e PLEX_TOKEN=<Your token> \
  -e PLEX_USERNAME=<Username / email for your Plex Account> \
  -e PLEX_PASSWORD=<Password for your Plex Account> \
  -e SERVER_NAME=<Name for your plex server ie plex> \
  -e WRITE_MISSING_AS_CSV=<1 | 0> \
  -e APPEND_SERVICE_SUFFIX=<1 | 0> \
  -e ADD_PLAYLIST_POSTER=<1 | 0> \
  -e ADD_PLAYLIST_DESCRIPTION=<1 | 0> \
  -e APPEND_INSTEAD_OF_SYNC=<1 | 0> \
  -e SECONDS_TO_WAIT=43200 \
  -e SPOTIFY_CLIENT_ID=<Your ID> \
  -e SPOTIFY_REDIRECT_URI=http://localhost:8888/callback \
  -e SPOTIFY_CLIENT_SECRET=<Your Secret> \
  -e SPOTIFY_USER_ID=<Your ID / Username> \
  -e DEEZER_USER_ID=<your spotify user id> \
  -e DEEZER_PLAYLIST_ID= \
  --restart unless-stopped \
  dregsozworld/plex_playlist_sync:latest
```
#### Notes
- Include `http://` in the PLEX_URL
- Remove comments (ex: `# Optional x`) before running 
- Do  Not change spotify_redirect_url pls

### Docker Compose

docker-compose.yml can be configured as follows. See [docker-compose-example.yml](https://github.com/rnagabhyrava/plex-playlist-sync/blob/main/docker-compose-example.yml) for example
```
version: "2.1"
services:
  playlistSync:
    image: dregsozworld/plex_playlist_sync
    container_name: playlistSync
    ports:
      - "8888:8888/tcp"
    volumes:
      - <directory where csv stored>:/data
      - <directory to store spotify keys>:/caches
    environment:
      - PLEX_URL= <Your local plex url>
      - PLEX_TOKEN=<Your token>
      - PLEX_USERNAME=<Username / email for your Plex Account>
      - PLEX_PASSWORD=<Password for your Plex Account>
      - SERVER_NAME=<Name for your plex server ie plex>
      - WRITE_MISSING_AS_CSV=<1 | 0 >
      - APPEND_SERVICE_SUFFIX= <1 | 0>
      - ADD_PLAYLIST_POSTER= ><1 | 0 >
      - ADD_PLAYLIST_DESCRIPTION= < 1 | 0 >
      - APPEND_INSTEAD_OF_SYNC= <1 | 0 >
      - SECONDS_TO_WAIT=43200  #12 Hours Default
      - SPOTIFY_CLIENT_ID= <Your ID>
      - SPOTIFY_REDIRECT_URI=http://localhost:8888/callback #DO NOT CHANGE
      - SPOTIFY_CLIENT_SECRET= <Your Secret>
      - SPOTIFY_USER_ID= <Your ID / Username > # Do not need anymore
      - DEEZER_USER_ID=<your spotify user id>
      - DEEZER_PLAYLIST_ID= # multiple playlists are space separated
    restart: unless-stopped
```
And run with :
```
docker-compose up
```

### Issues
Something's off? See room for improvement? Feel free to open an issue with as much info as possible. Cheers!
