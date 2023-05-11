import logging
import time
from typing import List

import spotipy
from plexapi.server import PlexServer

from .helperClasses import Playlist, Track, UserInputs
from .plex import update_or_create_plex_playlist


def _get_sp_user_playlists(
    sp: spotipy.Spotify, userInputs: UserInputs, suffix: str = " - Spotify"
) -> List:
    """Get metadata for playlists in the given user_id.

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        userId (str): UserId of the spotify account (get it from open.spotify.com/account)
        suffix (str): Identifier for source
    Returns:
        List[Playlist]: list of Playlist objects with playlist metadata fields
    """
    playlists = []
    all_playlists = []

    try:

        # test = sp.categories('GB')
        # test = sp.current_user_saved_tracks()
        # a = sp.categories(country='GB')


        spotify_playlists = []
        if userInputs.spotify_playlist_ids:
            spotify_playlists = userInputs.spotify_playlist_ids.split()

        try:
            if "featured" in userInputs.spotify_categories:
                featured_playlists = sp.featured_playlists(country="GB")['playlists']['items']
                featured_playlist_ids = list(map(lambda x: x['id'], featured_playlists))
                spotify_playlists = spotify_playlists + featured_playlist_ids

            if "throw" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFN2GMExExvrS")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "dance" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFHOzuVTgTizF")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "top" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="toplists")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "hiphop" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFQ00XGBls6ym")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "indie" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFCWjUTdzaG0e")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "mood" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFzHmL4tf05da")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "party" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFA6SOHvT3gck")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "pop" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFEC4WFtoNRpw")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "rnb" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFEZPnFQSFB1T")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "rock" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFDXXwE9BDJAr")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids

            if "home" in userInputs.spotify_categories:
                category_playlists = sp.category_playlists(category_id="0JQ5DAqbMKFx0uLQR2okcc")['playlists']['items']
                category_playlist_ids = list(map(lambda x: x['id'], category_playlists))
                spotify_playlists = spotify_playlists + category_playlist_ids
        except Exception as e:
            logging.error("Error in building spotify categories")
            logging.error('Error at %s', 'division', exc_info=e)


        playlists_from_list = []
        for pid in spotify_playlists:
            p = sp.playlist(playlist_id=pid, market='GB')
            playlists_from_list.append(p)

        if len(spotify_playlists) > 0:
            all_playlists = all_playlists + playlists_from_list



        # playlists_from_list = []
        # for pid in spotify_playlists:
        #     if pid not in featured_playlist_ids:
        #         p = sp.playlist(playlist_id=pid, market='GB')
        #         playlists_from_list.append(p)

        # logging.info(all_playlists)
        # sp_playlists1 = sp.category_playlists('toplists', 'GB')
        # for playlist in sp_playlists1["playlists"]["items"]:

        # for playlist in all_playlists:
        #     playlists.append(
        #         Playlist(
        #             id=playlist["uri"],
        #             name=playlist["name"] + suffix,
        #             description=playlist.get("description", ""),
        #             # playlists may not have a poster in such cases return ""
        #             poster=""
        #             if len(playlist["images"]) == 0
        #             else playlist["images"][0].get("url", ""),
        #         )
        #     )
    except:
        logging.error("Spotify User ID Error")

    return all_playlists


# def _get_sp_tracks_from_playlist(
#     sp: spotipy.Spotify, playlist: Playlist
# ) -> List[Track]:
#     """Return list of tracks with metadata.
#
#     Args:
#         sp (spotipy.Spotify): Spotify configured instance
#         user_id (str): spotify user id
#         playlist (Playlist): Playlist object
#     Returns:
#         List[Track]: list of Track objects with track metadata fields
#     """
#
#     def extract_sp_track_metadata(track) -> Track:
#         title = track["track"]["name"]
#         artist = track["track"]["artists"][0]["name"]
#         album = track["track"]["album"]["name"]
#         # Tracks may no longer be on spotify in such cases return ""
#         url = track["track"]["external_urls"].get("spotify", "")
#         return Track(title, artist, album, url)
#
#     try:
#         sp_playlist_tracks = sp.playlist_items(playlist.id, limit=200)
#     except:
#         logging.error("Failed to get playlist items")
#
#     # Only processes first 100 tracks
#     tracks = list(
#         map(
#             extract_sp_track_metadata,
#             [i for i in sp_playlist_tracks["items"] if i.get("track")],
#         )
#     )
#
#     # If playlist contains more than 100 tracks this loop is useful
#     while sp_playlist_tracks["next"]:
#         sp_playlist_tracks = sp.next(sp_playlist_tracks)
#         tracks.extend(
#             list(
#                 map(
#                     extract_sp_track_metadata,
#                     [i for i in sp_playlist_tracks["items"] if i.get("track")],
#                 )
#             )
#         )
#     return tracks


def spotify_playlist_sync(
    sp: spotipy.Spotify, plex: PlexServer, userInputs: UserInputs
) -> None:
    """Create/Update plex playlists with playlists from spotify.

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        user_id (str): spotify user id
        plex (PlexServer): A configured PlexServer instance
    """
    playlists = _get_sp_user_playlists(
        sp,
        userInputs,
        " - Spotify" if userInputs.append_service_suffix else ""
    )
    if playlists:
        for playlist in playlists:
            # time.sleep(1)
            # tracks = _get_sp_tracks_from_playlist(
            #     sp, playlist
            # )
            if "items" in playlist['tracks']:
                update_or_create_plex_playlist(plex, playlist, userInputs)
    else:
        logging.error("No spotify playlists found for given user")
