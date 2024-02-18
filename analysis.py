import argparse
import requests
import yaml
import pandas as pd
import logging
import os

from plyer import notification



class Analysis:
    def __init__(self, config_paths, artist_id):
        # Set up the logger FIRST
        self.logger = logging.getLogger(__name__) 
        self.logger.setLevel(logging.DEBUG)

        absolute_path = os.path.abspath(config_paths)
        print("Absolute Path:", absolute_path) 

        # Load configuration at initialization
        self.config = self.load_config(absolute_path)  
        self.logger.debug("Loaded Configuration: %s", self.config)
       
        self.artist_id = artist_id
        self.df = None
        self.BASE_URL = 'https://api.spotify.com/v1/'

        self.logger.debug("Configuration paths: %s", config_paths) 

        absolute_path = os.path.abspath(config_paths)
        print("Absolute Path:", absolute_path) 
        self.config = self.load_config(absolute_path)

    def load_config(self, config_paths):
        config = {}
        try:
            with open('config/user_config.yml', 'r') as f:  
                config = yaml.safe_load(f) 
        except FileNotFoundError as e:
            print(f"Error loading config files: {e}")
        return config 
    
    def _authenticate(self):
        print("Loaded Configuration:", self.config)
    
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
            print(f"Authentication error: {e}")
        
    def _fetch_albums(self):
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
        headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
        tracks_url = self.BASE_URL + 'albums/{}/tracks'.format(album_id)

        try:
            response = requests.get(tracks_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching tracks: {e}")  # Use logger here 
            return None
        
    def _fetch_audio_features(self, track_id, access_token):
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
        
        print(len(track_names))
        print(len(danceability_values))
        print(len(energy_values)) 

        self.df = pd.DataFrame(data)
        print(self.df.head())  # Inspect your DataFrame

    def compute_analysis(self):
        if not self.df.empty:
            mean_features = self.df.groupby('track_name').mean()
            print(mean_features)
        else:
            print("No data loaded. Call load_data() first.")

    def notify_done(self, message: str) -> None: #I changed the notification section because Python3 does not support Nfty

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

        analyzer = Analysis('user_config.yml', args.artist_id) 
        analyzer.load_data() 
        analyzer.compute_analysis() 
