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
SCOPE = 'user-top-read'

#Spotify URLs
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'

#Needs work
def app_authorization():
    return f'{SPOTIFY_AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}'

def user_authorization():
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

    authorization_header = {'Authorization': f'Bearer {access_token}'}
    return authorization_header

def get_user_top_tracks(authorization_header):
    user_top_tracks_api_endpoint = f'{SPOTIFY_API_URL}/me/top/tracks'
    user_top_tracks_request = requests.get(user_top_tracks_api_endpoint, headers=authorization_header)
    user_top_tracks_data = json.loads(user_top_tracks_request.text)
    return user_top_tracks_data['items']
