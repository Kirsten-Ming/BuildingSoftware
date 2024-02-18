import argparse
import requests
import yaml
import pandas as pd
import logging
import os
from plyer import notification

class Analysis:
    """
    A class for analyzing Spotify data.
    """

    def __init__(self, config_path, artist_id):
        """
        Initialize the SpotifyAnalyzer.

        Parameters:
        - config_path (str): The path to the configuration file.
        - artist_id (str): The Spotify artist ID.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        config_path = os.path.abspath(config_path)
        self.config = self.load_config(config_path)
        self.artist_id = artist_id
        self.df = None
        self.BASE_URL = 'https://api.spotify.com/v1/'

    def load_config(self, config_path):
        """
        Load the configuration from the specified path.

        Parameters:
        - config_path (str): The path to the configuration file.

        Returns:
        - dict: The loaded configuration.
        """
        config = {}
        try:
            with open(os.path.join(config_path, 'config', 'user_config.yml'), 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError as e:
            print(f"Error loading config files: {e}")
        return config
    
    def authenticate(self):
        """
        Authenticate with Spotify API and obtain an access token.

        Returns:
        - str: The access token.
        """
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
            raise Exception(f"Authentication error: {e}")
        
    def fetch_albums(self, access_token):
        """
        Fetch albums for the specified artist.

        Parameters:
        - access_token (str): The Spotify access token.

        Returns:
        - dict: The response JSON containing album information.
        """
        self.logger.debug("Entering fetch_albums")
        headers = {'Authorization': f'Bearer {access_token}'}
        albums_url = f'{self.BASE_URL}artists/{self.artist_id}/albums'
        params = {'include_groups': 'album', 'limit': 50}

        try:
            response = requests.get(albums_url, headers=headers, params=params)
            response.raise_for_status()
            self.logger.info("Albums fetched successfully") 
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching albums: {e}")
            return None 

    def fetch_tracks(self, album_id, access_token):
        """
        Fetch tracks for the specified album.

        Parameters:
        - album_id (str): The Spotify album ID.
        - access_token (str): The Spotify access token.

        Returns:
        - dict: The response JSON containing track information.
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        tracks_url = f'{self.BASE_URL}albums/{album_id}/tracks'

        try:
            response = requests.get(tracks_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching tracks: {e}")
            return None
    
    def fetch_audio_features(self, track_id, access_token):
        """
        Fetch audio features for the specified track.

        Parameters:
        - track_id (str): The Spotify track ID.
        - access_token (str): The Spotify access token.

        Returns:
        - dict: The response JSON containing audio features.
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        audio_features_url = f'{self.BASE_URL}audio-features/{track_id}'

        try:
            response = requests.get(audio_features_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching audio features: {e}")
        return None
    
    def load_data(self):
        """
        Load data from Spotify API and create a DataFrame.

        Populates self.df with data on track names, danceability, and energy.
        """
        access_token = self.authenticate()
        albums = self.fetch_albums(access_token)

        if albums:
            tracks = []
            for album in albums.get('items', []):
                album_id = album.get('id')
                if album_id:
                    album_tracks = self.fetch_tracks(album_id, access_token)
                    if album_tracks:
                        tracks.extend(album_tracks.get('items', []))

            audio_features = []
            for track in tracks:
                features = self.fetch_audio_features(track['id'], access_token)  
                if features: 
                    audio_features.append(features)
            
            track_names = [track['name'] for track in tracks]  
            danceability_values = [feature['danceability'] for feature in audio_features]
            energy_values = [feature['energy'] for feature in audio_features]

            data = {'track_name': track_names, 
                    'danceability': danceability_values, 
                    'energy': energy_values}

            self.df = pd.DataFrame(data)
            print(self.df.head())  # Inspect your DataFrame
        else:
            print("Error fetching albums. Check authentication.")

    def compute_analysis(self):
        """
        Compute the mean features for each track and print the result.
        """
        if not self.df.empty:
            mean_features = self.df.groupby('track_name').mean()
            print(mean_features)
        else:
           
    def main():
        parser = argparse.ArgumentParser(description='Perform analysis on Spotify data.')
        parser.add_argument('artist_id', help='The Spotify artist ID')
        parser.add_argument('config_file', help='The path to the configuration file')
    
        args = parser.parse_args()
    
        analyzer = Analysis(args.config_file, args.artist_id) 
        analyzer.load_data() 
        analyzer.compute_analysis()

    if __name__ == "__main__":
        main()
