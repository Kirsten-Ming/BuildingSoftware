Spotify Analysis Tool
Overview
This Python script performs analysis on Spotify data for a given artist. It utilizes the Spotify API to fetch information about the artist's albums, tracks, and audio features. The analysis includes computing mean features for the tracks.

Requirements
Python 3.x
Required Python packages: requests, yaml, pandas, logging, os
Setup
Clone the repository or download the script.

Install the required packages using the following command:

bash
Copy code
pip install requests yaml pandas
Create a Spotify application and obtain the CLIENT_ID and CLIENT_SECRET.

Save the CLIENT_ID and CLIENT_SECRET in a configuration file (user_config.yml) in the specified format:

yaml
Copy code
CLIENT_ID: YOUR_CLIENT_ID
CLIENT_SECRET: YOUR_CLIENT_SECRET
Run the script with the artist ID and the path to the configuration file as command-line arguments:

bash
Copy code
python analysis.py <artist_id> <config_file_path>
Usage
Run the script with the artist ID and the path to the configuration file as command-line arguments. The script will fetch data from the Spotify API and perform analysis on the artist's tracks.

bash
Copy code
python analysis.py <artist_id> <config_file_path>
Output
The script outputs mean features of the tracks, computed from the fetched data.

Author
Kirsten Ming
