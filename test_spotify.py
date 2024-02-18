import pytest
from unittest.mock import patch

from plyer import notification

from analysis import SAnalysis

@pytest.fixture
def spotify_analyzer():
    return SpotifyAnalysis(['user_config.yml'], 'some_artist_id')

# Test the successful album fetch scenario
@patch('requests.get')  #
@patch('plyer.notification.notify')
def test_fetch_albums_success(mock_notify, mock_get, spotify_analyzer):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'items': [
            {'name': 'Album 1', 'release_date': '2023-01-01', 'id': 'album_id_1'},
            {'name': 'Album 2', 'release_date': '2022-05-15', 'id': 'album_id_2'}
        ]
    }

    result = spotify_analyzer._fetch_albums()

    # Assertions
    assert mock_get.called
    assert result == mock_response.json()


