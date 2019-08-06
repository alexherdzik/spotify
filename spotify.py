import json
import base64
import requests
from flask import request

#Client Keys
CLIENT_ID = '55f1ab9c48f040d39629c869dbb40d9b'
CLIENT_SECRET = '68729e4083a444ffa4924335343a82b9'
CLIENT_CREDENTIALS = f'{CLIENT_ID}:{CLIENT_SECRET}'

#Server Parameters
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'playlist-modify-public user-top-read'

#Spotify URLs
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'

#Authentication Header
AUTHORIZATION_HEADER = ''

#Needs work
def app_authorization():
    return f'{SPOTIFY_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}'

def user_authorization():
    global AUTHORIZATION_HEADER
    auth_code = request.args.get('code')
    code_payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_code),
        'redirect_uri': REDIRECT_URI
    }
    base64encoded = base64.urlsafe_b64encode(CLIENT_CREDENTIALS.encode()).decode()
    headers = {'Authorization': f'Basic {base64encoded}'}
    token_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    #Tokens
    response_data = json.loads(token_request.text)
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    token_type = response_data['token_type']
    expires_in = response_data['expires_in']

    AUTHORIZATION_HEADER = {'Authorization': f'Bearer {access_token}'}
    return

def get_user_top_tracks(time_range):
    user_top_tracks_api_endpoint = f'{SPOTIFY_API_URL}/me/top/tracks?time_range={time_range}'
    user_top_tracks_request = requests.get(user_top_tracks_api_endpoint, headers=AUTHORIZATION_HEADER)
    user_top_tracks_data = json.loads(user_top_tracks_request.text)
    return user_top_tracks_data['items']

def get_user_top_tracks_uris(time_range):
    user_top_tracks = get_user_top_tracks(time_range)
    uris = []
    for track in user_top_tracks:
        uris.append(track['uri'])
    return uris

def get_user_profile():
    curr_user_api_endpoint = f'{SPOTIFY_API_URL}/me'
    curr_user_request = requests.get(curr_user_api_endpoint, headers=AUTHORIZATION_HEADER)
    curr_user_data = json.loads(curr_user_request.text)
    return curr_user_data

def create_user_playlist(name):
    user = get_user_profile()['id']
    create_playlist_api_endpoint = f'{SPOTIFY_API_URL}/users/{user}/playlists'
    parameters = {
        'name': str(name),
        'public': True,
        'collaborative': False,
        'description': 'Created by me'
    }
    create_playlist_request = requests.post(create_playlist_api_endpoint, json=parameters, headers=AUTHORIZATION_HEADER)
    create_playlist_data = json.loads(create_playlist_request.text)
    return create_playlist_data['uri']

def get_playlist_id(playlist_uri):
    start_index = playlist_uri.rfind(':') + 1
    return playlist_uri[start_index:]

def add_tracks_to_playlist(playlist_id, track_uris):
    add_tracks_api_endpoint = f'{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks'
    parameters = {
        'uris': track_uris,
        'position': 0
    }
    add_tracks_request = requests.post(add_tracks_api_endpoint, json=parameters, headers=AUTHORIZATION_HEADER)
    add_tracks_data = json.loads(add_tracks_request.text)
    return add_tracks_data['snapshot_id']
