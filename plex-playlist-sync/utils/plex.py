import csv
import logging
import os.path
import pathlib
import sys
from difflib import SequenceMatcher
from typing import List

import plexapi
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
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
    logging.info(f"Creating {file}")
    with open(file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(Track.__annotations__.keys())
        for track in tracks:
            writer.writerow(
                [track.title, track.artist, track.album, track.url]
            )


def _delete_csv(name: str, path: str = "/data") -> None:
    """Delete file associated with given name

    Args:
        name (str): Name of the file to delete
        path (str, optional): Root directory to delete the file from
    """
    data_folder = pathlib.Path(path)
    logging.info(os.listdir(data_folder))
    file = data_folder / f"{name}.csv"
    logging.info(f"{str(file)} Exists: {os.path.exists(file)}")
    file.unlink()


def _get_available_plex_tracks(plex: PlexServer, tracks: List[Track]) -> (List[Track], List[Track]):
    """Search and return list of tracks available in plex.

    Args:
        plex (PlexServer): A configured PlexServer instance
        tracks (List[Track]): list of track objects

    Returns:
        Tuple containing:
            List of Tracks that are stored in Plex
            List of Tracks which are not
    """
    plex_tracks, missing_tracks = [], []
    for track in tracks:
        search = []
        try:
            search = plex.search(track.title, mediatype="track", limit=5)
        except NotFound:
            logging.info(f"{track.title} not found on plex server")
        except BadRequest:
            logging.info(f"failed to search {track.title} on plex")
        if (not search) or len(track.title.split("(")) > 1:
            logging.info("retrying search for %s", track.title)
            try:
                search += plex.search(
                    track.title.split("(")[0], mediatype="track", limit=5
                )
                logging.info(f"search for {track.title} successful")
            except BadRequest:
                logging.info(f"unable to query {track.title} on plex")

        found = False
        if search:
            for s in search:
                try:
                    artist_similarity = SequenceMatcher(
                        None, s.artist().title.lower(), track.artist.lower()
                    ).quick_ratio()

                    if artist_similarity >= 0.9:
                        plex_tracks.extend(s)
                        found = True
                        break

                    album_similarity = SequenceMatcher(
                        None, s.album().title.lower(), track.album.lower()
                    ).quick_ratio()

                    if album_similarity >= 0.9:
                        plex_tracks.extend(s)
                        found = True
                        break

                except IndexError:
                    logging.info(f"Looks like plex mismatched {track.title}, retrying with next result")
        if not found:
            missing_tracks.append(track)

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
    tracks: List[Track],
    user_inputs: UserInputs,
) -> None:
    """Update playlist if exists, else create a new playlist.

    Args:
        user_inputs: User entered Environment Vars
        tracks: (List): List of plex.audio.track objects
        plex (PlexServer): A configured PlexServer instance
        playlist (Playlist): Playlist object
    """
    available_tracks, missing_tracks = _get_available_plex_tracks(plex, tracks)
    if available_tracks:  # Set up playlist with Tracks
        try:
            plex_playlist = _update_plex_playlist(
                plex=plex,
                available_tracks=available_tracks,
                playlist=playlist,
                append=user_inputs.append_instead_of_sync,
            )
            logging.info(f"Updated playlist {playlist.name}")
        except NotFound:
            plex.createPlaylist(title=playlist.name, items=available_tracks)
            logging.info(f"Created playlist  {playlist.name}")
            plex_playlist = plex.playlist(playlist.name)

        if playlist.description and user_inputs.add_playlist_description:
            try:
                plex_playlist.edit(summary=playlist.description)
            except (Unauthorized, NotFound, BadRequest) as e:
                logging.info(f"Failed to update description for playlist {playlist.name}")
                logging.exception(e)
            except Exception as e:
                logging.error(f"Unhandled Exception: {e}")

        if playlist.poster and user_inputs.add_playlist_poster:
            try:
                plex_playlist.uploadPoster(url=playlist.poster)
            except (Unauthorized, NotFound, BadRequest) as e:
                logging.info(f"Failed to update poster for playlist {playlist.name}")
                logging.warning(str(e))
            except Exception as e:
                logging.exception(e)

        logging.info(f"Updated playlist {playlist.name} with summary and poster")

    else:
        logging.info(f"No songs for playlist {playlist.name} were found on plex, skipping the playlist creation")

    if missing_tracks and user_inputs.write_missing_as_csv:  # Write needed songs to CSV file
        try:
            _write_csv(missing_tracks, playlist.name)
            logging.info(f"Missing tracks written to {playlist.name}.csv")
        except OSError as e:
            logging.info(f"Failed to write missing tracks for {playlist.name}, likely permission issue")
            logging.warning(str(e))
        except Exception as e:
            logging.exception(e)
    if (not missing_tracks) and user_inputs.write_missing_as_csv:
        try:
            # Delete playlist created in prev run if no tracks are missing now
            if os.path.exists(pathlib.Path('/data') / (playlist.name + '.csv')):
                _delete_csv(playlist.name)
                logging.info(f"Deleted old {playlist.name}")
            else:
                logging.info(f"{playlist.name + '.csv'} does not exist in /data")
        except OSError as e:
            logging.info(f"Failed to delete {playlist.name}.csv, likely permission issue")
            logging.warning(str(e))
        except Exception as e:
            logging.exception(e)
