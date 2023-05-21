import logging
from typing import List

import spotipy
from plexapi.server import PlexServer
from spotipy import CacheFileHandler, SpotifyOAuth

from pps.config.helper_classes import Playlist, Track, UserInputs
from pps.providers.plex import update_or_create_plex_playlist
from pps.providers import spotify_callback

from pps import SPOTIFY_TOKEN_CACHE_PATH

logging.getLogger(__name__)


def connect_to_spotify(user_inputs):
    cache_handler = CacheFileHandler(cache_path=SPOTIFY_TOKEN_CACHE_PATH)
    token_info = cache_handler.get_cached_token()
    logging.debug(token_info)
    auth_manager = SpotifyOAuth(
        client_id=user_inputs.spotify_client_id,
        client_secret=user_inputs.spotify_client_secret,
        redirect_uri=user_inputs.spotify_redirect_uri,
        show_dialog=False,
        open_browser=False,
        scope='playlist-read-private,playlist-read-collaborative,user-library-read',
        cache_handler=cache_handler
    )
    if not token_info or not all((token_info.get('access_token'), token_info.get('refresh_token'))):

        auth_url = auth_manager.get_authorize_url()
        print(f"Use the following link to authenticate your account: {auth_url}")
        code = spotify_callback.access_code_queue.get()
        logging.info("Got a code!")
        token_info = auth_manager.get_access_token(code)

    sp = spotipy.Spotify(auth_manager=auth_manager)
    logging.info("Successfully connected to Spotify Account")
    return sp


def get_sp_user_playlists(spotify: spotipy.Spotify, suffix: str = " - Spotify") -> List[Playlist]:
    """Get metadata for playlists in the given user_id.

    Args:
        spotify (spotipy.Spotify): Spotify configured instance
        suffix (str): Identifier for source
    Returns:
        List[Playlist]: list of Playlist objects with playlist metadata fields
    """
    playlists = []
    try:
        sp_playlists = spotify.current_user_playlists()
        for playlist in sp_playlists["items"]:
            playlists.append(
                Playlist(
                    id=playlist["uri"],
                    name=playlist["name"] + suffix,
                    description=playlist.get("description", ""),
                    poster="" if not playlist["images"] else playlist["images"][0].get("url", ""),
                )
            )
    except spotipy.SpotifyException as e:
        logging.error(f"Failed getting playlists: {e}")
    return playlists


def get_sp_tracks_from_playlist(spotify: spotipy.Spotify, playlist: Playlist) -> List[Track]:
    """Return list of tracks with metadata.

    Args:
        spotify (spotipy.Spotify): Spotify configured instance
        playlist (Playlist): Playlist object
    Returns:
        List[Track]: list of Track objects with track metadata fields
    """

    def extract_sp_track_metadata(track) -> Track:
        title = track["track"]["name"]
        artist = track["track"]["artists"][0]["name"]
        album = track["track"]["album"]["name"]
        url = track["track"]["external_urls"].get("spotify", "")
        return Track(title, artist, album, url)

    tracks = []

    try:
        sp_playlist_tracks = spotify.playlist_items(playlist.id, additional_types=("track",))
        tracks = [extract_sp_track_metadata(i) for i in sp_playlist_tracks["items"] if i.get("track")]
        while sp_playlist_tracks["next"]:
            sp_playlist_tracks = spotify.next(sp_playlist_tracks)
            tracks.extend(extract_sp_track_metadata(i) for i in sp_playlist_tracks["items"] if i.get("track"))
    except spotipy.SpotifyException as e:
        logging.error(f"Failed getting tracks: {e}")
    return tracks


def spotify_playlist_sync(spotify: spotipy.Spotify, plex: PlexServer, user_inputs: UserInputs) -> None:
    """Syncs Plex Server with User's Spotify Playlists

    Args:
        spotify (spotipy.Spotify):  Configured Spotify Instance
        plex: PlexServer object
        user_inputs: Entered Environment Vars

    Returns:

    """

    playlists = get_sp_user_playlists(spotify, " - Spotify" if user_inputs.append_service_suffix else "", )
    if playlists:
        for playlist in playlists:
            tracks = get_sp_tracks_from_playlist(spotify, playlist)
            update_or_create_plex_playlist(plex, playlist, tracks, user_inputs)
    else:
        logging.error("No spotify playlists found for given user")
