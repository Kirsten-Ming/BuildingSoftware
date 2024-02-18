import argparse
import requests
import yaml
import pandas as pd
import logging
import os
from plyer import notification


class Analysis:
    """
    A class for performing analysis on Spotify data.
    """

    def __init__(self, config_paths, artist_id):
        """
        Initializes the Analysis object.

        Parameters:
        - config_paths (str): The path to the configuration file.
        - artist_id (str): The Spotify artist ID.
        """
        # Set up the logger FIRST
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        absolute_path = os.path.abspath(config_paths)
        self.logger.debug("Absolute Path: %s", absolute_path)

        # Load configuration at initialization
        self.config = self.load_config(absolute_path)
        self.logger.debug("Loaded Configuration: %s", self.config)

        self.artist_id = artist_id
        self.df = None
        self.BASE_URL = 'https://api.spotify.com/v1/'

    def load_config(self, config_paths):
        """
        Load configuration from a YAML file.

        Parameters:
        - config_paths (str): The path to the configuration file.

        Returns:
        dict: The loaded configuration.
        """
        config = {}
        try:
            with open(config_paths, 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError as e:
            self.logger.error(f"Error loading config files: {e}")
            raise  # Exit the program in case of an error
        return config

    def _authenticate(self):
        """
        Authenticate with the Spotify API and obtain an access token.

        Returns:
        str: The access token.
        """
        self.logger.debug("Loaded Configuration: %s", self.config)

        auth_url = 'https://accounts.spotify.com/api/token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.config['CLIENT_ID'],
            'client_secret': self.config['CLIENT_SECRET']
        }

        try:
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            return response.json()['access_token']
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication error: {e}")
            raise  # Exit the program in case of an error

    def _fetch_albums(self):
        """
        Fetch albums for the specified artist.

        Returns:
        dict or None: The fetched albums or None in case of an error.
        """
        self.logger.debug("Entering _fetch_albums")
        access_token = self._authenticate()
        headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
        albums_url = self.BASE_URL + 'artists/{}/albums'.format(self.artist_id)
        params = {'include_groups': 'album', 'limit': 50}

        try:
            response = requests.get(albums_url, headers=headers, params=params)
            response.raise_for_status()
            self.logger.info("Albums fetched successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching albums: {e}")
            return None

    def _fetch_tracks(self, album_id, access_token):
        """
        Fetch tracks for a specific album.

        Parameters:
        - album_id (str): The ID of the album.
        - access_token (str): The Spotify API access token.

        Returns:
        dict or None: The fetched tracks or None in case of an error.
        """
        headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
        tracks_url = self.BASE_URL + 'albums/{}/tracks'.format(album_id)

        try:
            response = requests.get(tracks_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching tracks: {e}")
            return None

    def _fetch_audio_features(self, track_id, access_token):
        """
        Fetch audio features for a specific track.

        Parameters:
        - track_id (str): The ID of the track.
        - access_token (str): The Spotify API access token.

        Returns:
        dict or None: The fetched audio features or None in case of an error.
        """
        headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
        audio_features_url = self.BASE_URL + 'audio-features/{}'.format(track_id)

        try:
            response = requests.get(audio_features_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching audio features: {e}")
            return None

    def load_data(self):
        """
        Load data from Spotify API, including albums, tracks, and audio features.
        """
        albums = self._fetch_albums()
        access_token = self._authenticate()  # Fetch the token once outside the loop

        tracks = []
        for album in albums['items']:
            tracks.extend(self._fetch_tracks(album['id'], access_token)['items'])

        audio_features = []
        for track in tracks:
            features = self._fetch_audio_features(track['id'], access_token)
            if features:
                audio_features.append(features)

        track_names = [track['name'] for track in tracks]
        danceability_values = [feature['danceability'] for feature in audio_features]
        energy_values = [feature['energy'] for feature in audio_features]

        data = {'track_name': track_names,
                'danceability': danceability_values,
                'energy': energy_values}

        self.df = pd.DataFrame(data)
        self.logger.debug(self.df.head())  # Inspect your DataFrame

    def compute_analysis(self):
        """
        Compute the analysis on the loaded data, calculating mean features.
        """
        if not self.df.empty:
            mean_features = self.df.groupby('track_name').mean()
            print(mean_features)
        else:
            print("No data loaded. Call load_data() first.")

    def notify_done(self, message: str) -> None:
        """
        Notify when the Spotify analysis is completed.

        Parameters:
        - message (str): The notification message.
        """
        notification.notify(
            title='Spotify Analysis Completed',
            message=message,
            app_name='My Spotify Analysis',
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform analysis on Spotify data.')
    parser.add_argument('artist_id', help='The Spotify artist ID')
    parser.add_argument('config_file', help='The path to the configuration file')

    args = parser.parse_args()

    analyzer = Analysis(args.config_file, args.artist_id)
    analyzer.load_data()
    analyzer.compute_analysis()
