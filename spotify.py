import json
import base64
import requests
import datetime
from flask import request

#Client Keys
CLIENT_ID = ''
CLIENT_SECRET = ''
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

def get_user_top_tracks(time_range, limit):
    user_top_tracks_api_endpoint = f'{SPOTIFY_API_URL}/me/top/tracks?time_range={time_range}&limit={limit}'
    user_top_tracks_request = requests.get(user_top_tracks_api_endpoint, headers=AUTHORIZATION_HEADER)
    user_top_tracks_data = json.loads(user_top_tracks_request.text)
    return user_top_tracks_data['items']

def get_user_top_tracks_all():
    time_ranges = ['short_term', 'medium_term', 'long_term']
    user_top_tracks_all = {}
    for time_range in time_ranges:
        user_top_tracks_all[time_range] = get_user_top_tracks(time_range)
    return user_top_tracks_all

def get_user_top_tracks_uris(time_range, limit):
    user_top_tracks = get_user_top_tracks(time_range, limit)
    uris = []
    for track in user_top_tracks:
        uris.append(track['uri'])
    return uris

def get_user_profile():
    curr_user_api_endpoint = f'{SPOTIFY_API_URL}/me'
    curr_user_request = requests.get(curr_user_api_endpoint, headers=AUTHORIZATION_HEADER)
    curr_user_data = json.loads(curr_user_request.text)
    return curr_user_data

def get_spotify_username():
    curr_user_api_endpoint = f'{SPOTIFY_API_URL}/me'
    curr_user_request = requests.get(curr_user_api_endpoint, headers=AUTHORIZATION_HEADER)
    curr_user_data = json.loads(curr_user_request.text)
    return curr_user_data['id']

def create_user_playlist(time_range, limit):
    user = get_spotify_username()
    create_playlist_api_endpoint = f'{SPOTIFY_API_URL}/users/{user}/playlists'
    now = datetime.datetime.now()
    time_range_title = convert_time_range(time_range)
    name = f'Top {limit} ({time_range_title})'
    parameters = {
        'name': name,
        'public': True,
        'collaborative': False,
        'description': f'Created on {now.strftime("%b %d, %Y at %I:%M %p")}'
    }
    create_playlist_request = requests.post(create_playlist_api_endpoint, json=parameters, headers=AUTHORIZATION_HEADER)
    create_playlist_data = json.loads(create_playlist_request.text)

    playlist_id = get_playlist_id(create_playlist_data['uri'])

    #insert_playlist(playlist_id, user, time_range, limit, now, now)

    return playlist_id

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

def convert_time_range(time_range):
    switcher = {
        'short_term': '4 Weeks',
        'medium_term': '6 Months',
        'long_term': 'All Time'
    }
    return switcher.get(time_range, "Unknown")

#default is 20 playlists
def check_user_playlist(playlist_id):
    get_playlists_api_endpoint = f'{SPOTIFY_API_URL}/me/playlists'
    get_playlists_response = requests.get(get_playlists_api_endpoint, headers=AUTHORIZATION_HEADER)
    get_playlists_data = json.loads(get_playlists_response.text)

    #Get list of playlist ids
    playlists = get_playlists_data['items']
    playlist_ids = []
    for playlist in playlists:
        playlist_ids.append(playlist['id'])

    #Check if playlist id is in playlist_ids
    return playlist_id in playlist_ids

def get_playlist_tracks(playlist_id):
    get_playlist_tracks_api_endpoint = f'{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks'
    get_playlist_tracks_response = requests.get(get_playlist_tracks_api_endpoint, headers=AUTHORIZATION_HEADER)
    get_playlist_tracks_data = json.loads(get_playlist_tracks_response.text)
    return get_playlist_tracks_data['items']

def get_tracks_added(tracks_new, tracks_old):
    tracks_added = []
    for track_new in tracks_new:
        if not any(track_old['track']['id'] == track_new['id'] for track_old in tracks_old):
            tracks_added.append(track_new)
    return tracks_added

def get_tracks_removed(tracks_old, tracks_new):
    tracks_removed = []
    for track_old in tracks_old:
        if not any(track_new['id'] == track_old['track']['id'] for track_new in tracks_new):
            tracks_removed.append(track_old)
    return tracks_removed

#Check status code at some point
def replace_playlist_tracks(playlist_id, track_uris):
    replace_playlist_tracks_api_endpoint = f'{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks'
    parameters = {
        'uris': track_uris
    }
    replace_playlist_tracks_request = requests.put(replace_playlist_tracks_api_endpoint, json=parameters, headers=AUTHORIZATION_HEADER)
    return

"""
def insert_playlist(db, playlist_id, username, time_range, limit, created, updated):
    playlist = Playlist(playlist_id=playlist_id, username=username, time_range=time_range, tracks=limit, created=created, updated=updated)
    db.session.add(playlist)
    db.session.commit()
    return
"""
