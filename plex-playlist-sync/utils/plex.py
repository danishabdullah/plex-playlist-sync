import csv
import logging
import pathlib
import sys
from difflib import SequenceMatcher
from typing import List
import time
from urllib.parse import quote_plus
import re

import plexapi
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer

from .helperClasses import Playlist, Track, UserInputs

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def _write_csv(tracks: List[Track], name: str, path: str = "/data") -> None:
    """Write given tracks with given name as a csv.

    Args:
        tracks (List[Track]): List of Track objects
        name (str): Name of the file to write
        path (str): Root directory to write the file
    """
    # pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    data_folder = pathlib.Path(path)
    data_folder.mkdir(parents=True, exist_ok=True)
    file = data_folder / f"{name}.csv"

    with open(file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(Track.__annotations__.keys())
        for track in tracks:
            track_title = track['track']['name']
            track_artist = track['track']['artists'][0]['name']
            track_album = track['track']['album']['name']
            track_url = track['track']['href']
            writer.writerow(
                [track_title, track_artist, track_album, track_url]
            )


def _delete_csv(name: str, path: str = "/data") -> None:
    """Delete file associated with given name

    Args:
        name (str): Name of the file to delete
        path (str, optional): Root directory to delete the file from
    """
    data_folder = pathlib.Path(path)
    file = data_folder / f"{name}.csv"
    file.unlink()


def _get_available_plex_tracks(plex: PlexServer, tracks) -> List:
    """Search and return list of tracks available in plex.

    Args:
        plex (PlexServer): A configured PlexServer instance
        tracks (List[Track]): list of track objects

    Returns:
        List: of plex track objects
    """
    plex_tracks, missing_tracks = [], []
    for track in tracks:
        search = []

        track_title = track['track']['name']
        track_artist = track['track']['artists'][0]['name']

        try:
            search += plex.search(track_title, mediatype="track", limit=10)
        except BadRequest:
            logging.info("failed to search %s on plex", track_title)

        try:
            search += plex.search(track_artist + " " +  track_title, mediatype="track", limit=10)
        except BadRequest:
            logging.info("failed to search %s on plex", track_title)

        try:
            search += plex.search(track_title.split("-")[0], mediatype="track", limit=10)
        except BadRequest:
            logging.info("failed to search %s on plex", track_title)

        try:
            search += plex.search(track_title.split("'")[0], mediatype="track", limit=10)
        except BadRequest:
            logging.info("failed to search %s on plex", track_title)

        if (not search) or len(track_title.split("(")) > 1:
            logging.info("retrying search for %s", track_title)
            try:
                search += plex.search(
                    track_title.split("(")[0], mediatype="track", limit=5
                )
                logging.info("search for %s successful", track_title)
            except BadRequest:
                logging.info("unable to query %s on plex", track_title)

        found = False
        if search:
            for s in search:
                try:
                    artist_similarity = SequenceMatcher(
                        None,
                        s.artist().title.lower(),
                        track_artist.lower()
                    ).quick_ratio()

                    artist_similarity1 = SequenceMatcher(
                        None,
                        s.artist().title.lower().replace("the", ""),
                        track_artist.lower().replace("the", "")
                    ).quick_ratio()

                    track_similarity = SequenceMatcher(
                        None,
                        s.title.lower(),
                        track_title.lower()
                    ).quick_ratio()

                    track_similarity1 = SequenceMatcher(
                        None,
                        s.title.lower(),
                        track_title.lower().split("-")[0]
                    ).quick_ratio()

                    track_similarity2 = SequenceMatcher(
                        None,
                        s.title.lower(),
                        track_title.lower().split("'")[0]
                    ).quick_ratio()

                    track_similarity3 = SequenceMatcher(
                        None,
                        s.title.lower(),
                        track_title.lower().split("(")[0]
                    ).quick_ratio()

                    track_similarity4 = SequenceMatcher(
                        None,
                        s.title.lower().split("(")[0],
                        track_title.lower().split("(")[0]
                    ).quick_ratio()

                    track_similarity5 = SequenceMatcher(
                        None,
                        s.title.lower().split("-")[0],
                        track_title.lower().split("-")[0]
                    ).quick_ratio()

                    logging.info(f" artist: {s.artist().title.lower()}, {track_artist.lower()}")
                    logging.info(f" track:  {s.title.lower()}, {track_title.lower()}")

                    acoustic = False if ("acoustic" in s.title.lower() and "acoustic" not in track_title.lower()) else True
                    live = False if ("live" in s.title.lower() and "live" not in track_title.lower()) else True
                    remix = False if ("remix" in s.title.lower() and "remix" not in track_title.lower()) else True
                    intru = False if ("instrumental" in s.title.lower() and "instrumental" not in track_title.lower()) else True
                    orch = False if ("orchestral" in s.title.lower() and "orchestral" not in track_title.lower()) else True
                    bootleg = False if ("bootleg" in s.title.lower() and "bootleg" not in track_title.lower()) else True
                    mix = False if ("mix" in s.title.lower() and "mix" not in track_title.lower()) else True

                    if (artist_similarity >= 0.85 or artist_similarity1 >= 0.85) and (track_similarity >= 0.65 or track_similarity1 >= 0.65 or track_similarity2 >= 0.65 or track_similarity3 >= 0.65 or track_similarity4 >= 0.65 or track_similarity5 >= 0.65) and acoustic and live and remix and intru and orch and mix and bootleg:
                        plex_tracks.extend(s)
                        found = True
                        logging.info(f"FOUND track: {track_artist}, {track_title}")
                        break

                    # else:
                    #     logging.info(artist_similarity)

                    # if not found:
                    #     artist_similarity = SequenceMatcher(
                    #         None, s.artist().title.lower(), track_artist.lower()
                    #     ).quick_ratio()

                    # album_similarity = SequenceMatcher(
                    #     None, s.album().title.lower(), track.album.lower()
                    # ).quick_ratio()
                    #
                    # if album_similarity >= 0.9:
                    #     plex_tracks.extend(s)
                    #     found = True
                    #     break

                except IndexError:
                    logging.info(
                        "Looks like plex mismatched the search for %s,"
                        " retrying with next result",
                        track_title,
                    )
        if not found:
            logging.error("%s | not found", track_artist + " - " + track_title)
            missing_tracks.append(track)
        # else:
        #     break

    return plex_tracks, missing_tracks


def _update_plex_playlist(
    plex: PlexServer,
    available_tracks: List,
    playlist: Playlist,
    append: bool = False,
) -> plexapi.playlist.Playlist:
    """Update existing plex playlist with new tracks and metadata.

    Args:
        plex (PlexServer): A configured PlexServer instance
        available_tracks (List): list of plex track objects
        playlist (Playlist): Playlist object
        append (bool): Boolean for Append or sync

    Returns:
        plexapi.playlist.Playlist: plex playlist object
    """
    plex_playlist = plex.playlist(playlist.name)
    if not append:
        plex_playlist.removeItems(plex_playlist.items())
    plex_playlist.addItems(available_tracks)
    return plex_playlist


def update_or_create_plex_playlist(
    plex: PlexServer,
    playlist: Playlist,
    userInputs: UserInputs,
) -> None:
    """Update playlist if exists, else create a new playlist.

    Args:
        plex (PlexServer): A configured PlexServer instance
        available_tracks (List): List of plex.audio.track objects
        playlist (Playlist): Playlist object
    """
    available_tracks, missing_tracks = _get_available_plex_tracks(plex, playlist['tracks']['items'])

    plex_users = [plex]

    if userInputs.plex_token_others:
        plex_other_ids = userInputs.plex_token_others.split()
        # Add other users if provided
        if userInputs.plex_url and userInputs.plex_token and len(plex_other_ids) > 0:
            for plex_id in plex_other_ids:
                # time.sleep(1)
                try:
                    plex_other = PlexServer(
                        userInputs.plex_url, plex_id)
                    plex_users.append(plex_other)
                except:
                    logging.error("Plex Authorization error for other users")

    for p in plex_users:
        if p is None:
            break

        if available_tracks and len(available_tracks) >= userInputs.plex_min_songs:
            try:
                old_playlist = p.playlist(playlist['name'])
                old_playlist.delete()
                logging.info("Deleted playlist %s", playlist['name'])
            except NotFound:
                logging.error("No playlist to delete for %s", playlist['name'])

            try:
                p.createPlaylist(title=playlist['name'], items=available_tracks)
                logging.info("Created playlist %s", playlist['name'])
                plex_playlist = p.playlist(playlist['name'])
            except:
                logging.error("Error creating playlist %s", playlist['name'])
                break

            if playlist['description'] and userInputs.add_playlist_description:
                try:
                    description = re.sub(
                        """(<a href="(.*?)">)|(</a>)""", "", playlist['description'])
                    plex_playlist.edit(summary=description)
                except:
                    logging.info(
                        "Failed to update description for playlist %s",
                        playlist['name'],
                    )
            if playlist['images'][0]['url'] and userInputs.add_playlist_poster:
                try:
                    key = '/library/metadata/%s/posters?url=%s' % (
                        plex_playlist.ratingKey, quote_plus(playlist['images'][0]['url']))
                    plex.query(key, method=plex._session.post)
                except:
                    logging.info(
                        "Failed to update poster for playlist %s", playlist['name']
                    )
            logging.info(
                "Updated playlist %s with summary and poster", playlist['name'],
            )
        else:
            logging.info(
                "No songs for playlist %s were found on plex, skipping the"
                " playlist creation",
                playlist['name'],
            )
    if missing_tracks and userInputs.write_missing_as_csv:
        try:
            _write_csv(missing_tracks, playlist['name'])
            logging.info("Missing tracks written to %s.csv", playlist['name'])
        except:
            logging.info(
                "Failed to write missing tracks for %s, likely permission"
                " issue",
                playlist['name'],
            )

    if (not missing_tracks) and userInputs.write_missing_as_csv:
        try:
            # Delete playlist created in prev run if no tracks are missing now
            _delete_csv(playlist['name'])
            logging.info("Deleted old %s.csv", playlist['name'])
        except:
            logging.info(
                "Failed to delete %s.csv, likely permission issue",
                playlist['name'],
            )
