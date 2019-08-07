from flask import Flask, request, redirect, render_template, url_for
from spotify import app_authorization, user_authorization, get_user_top_tracks_all, get_user_top_tracks_uris, create_user_playlist, add_tracks_to_playlist, get_playlist_id

app = Flask(__name__)

@app.route('/')
def index():
    auth_url = app_authorization()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    user_authorization()
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/top-tracks')
def top_tracks():
    #time_range = request.args.get('time_range', 'medium_term', type=str)
    #limit = request.args.get('limit', 20, type=int)
    user_top_tracks_all = get_user_top_tracks_all()
    return render_template('top_tracks.html', tracks=user_top_tracks_all)

#Get song uris and build post request
@app.route('/create-playlist')
def create_playlist():
    time_range = request.args.get('time_range', 'medium_term', type=str)
    user_top_tracks_uris = get_user_top_tracks_uris(time_range)
    playlist_uri = create_user_playlist('Top Tracks')
    playlist_id = get_playlist_id(playlist_uri)
    snapshot_id = add_tracks_to_playlist(playlist_id, user_top_tracks_uris)
    return render_template('create_playlist.html', snapshot_id=snapshot_id, time_range=time_range)
