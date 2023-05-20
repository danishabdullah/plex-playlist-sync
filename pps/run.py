import logging
import os
import threading
import time

from pps.config import config

from pps.providers.plex import connect_to_plex

from pps.providers.spotify import connect_to_spotify, spotify_playlist_sync
from pps.providers.p_deezer import connect_to_deezer, deezer_playlist_sync
from pps.config.logging_utils import setup_logging

from pps import CACHE_DIR
from pps.providers import spotify_callback


def sync_playlists(plex, sp, dz, user_inputs):
    if sp:
        spotify_playlist_sync(sp, plex, user_inputs)
        logging.info("Spotify playlist sync complete")
    else:
        logging.info("Could not Sync Spotify playlists")

    if dz:
        deezer_playlist_sync(dz, plex, user_inputs)
        logging.info("Deezer playlist sync complete")
    else:
        logging.info("could not sync Deezer_playlists")


def run():
    # Read ENV variables
    user_inputs = config.get_environment_variables()

    # Setup logging
    setup_logging()

    # Create cache directory
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Start flask callback server
    app_thread = threading.Thread(target=spotify_callback.app.run, kwargs={'host': '0.0.0.0', 'port': 8888})
    app_thread.start()

    # Body Loop
    while True:
        logging.info("Starting playlist sync")

        # Connect to Plex
        plex = connect_to_plex(user_inputs)

        # Connect to Spotify
        sp = connect_to_spotify(user_inputs)

        # Connect to Deezer
        dz = connect_to_deezer(user_inputs)

        # Sync playlists
        sync_playlists(plex, sp, dz, user_inputs)

        logging.info("All playlist(s) sync complete")
        logging.info(f"Sleeping for {user_inputs.wait_seconds} seconds"
                     f" ({time.ctime(time.time() + user_inputs.wait_seconds)})")
        time.sleep(user_inputs.wait_seconds)


if __name__ == "__main__":
    run()
