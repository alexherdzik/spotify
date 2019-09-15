from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
#from spotify import app_authorization, user_authorization, get_spotify_username, get_user_top_tracks, get_user_top_tracks_uris, create_user_playlist, add_tracks_to_playlist, get_playlist_id, convert_time_range, check_user_playlist, get_playlist_tracks, get_tracks_added, get_tracks_removed, replace_playlist_tracks
from spotify import *

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify.db'

db = SQLAlchemy(app)

class Playlist(db.Model):
    playlist_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50))
    time_range = db.Column(db.String(20))
    tracks = db.Column(db.Integer)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

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
    time_range = request.args.get('time_range', 'medium_term', type=str)
    limit = request.args.get('limit', 25, type=int)

    time_range_title = convert_time_range(time_range)

    user_top_tracks = get_user_top_tracks(time_range, limit)
    return render_template('top_tracks.html', tracks=user_top_tracks, time_range=time_range, limit=limit, time_range_title=time_range_title)

#Get song uris and build post request
@app.route('/create-playlist')
def create_playlist():
    time_range = request.args.get('time_range', 'medium_term', type=str)
    limit = request.args.get('limit', 25, type=int)

    user_top_tracks_uris = get_user_top_tracks_uris(time_range, limit)
    playlist_id = create_user_playlist(time_range, limit)
    username = get_spotify_username()

    playlist = Playlist(playlist_id=playlist_id, username=username, time_range=time_range, tracks=limit)
    db.session.add(playlist)
    db.session.commit()

    snapshot_id = add_tracks_to_playlist(playlist_id, user_top_tracks_uris)
    return render_template('create_playlist.html', snapshot_id=snapshot_id, time_range=time_range, limit=limit)

@app.route('/select')
def select_top_tracks():
    return render_template('select.html')

@app.route('/playlists')
def playlists():
    username = get_spotify_username()
    playlists = Playlist.query.filter_by(username=username).all()
    playlists_trim = []
    for playlist in playlists:
        if check_user_playlist(playlist.playlist_id):
            playlists_trim.append(playlist)
    return render_template('playlists.html', playlists=playlists_trim)

@app.route('/playlist')
def playlist():
    playlist_id = request.args.get('id', type=str)
    playlist_tracks = get_playlist_tracks(playlist_id)
    return render_template('playlist.html', tracks=playlist_tracks)

@app.route('/check-playlist')
def check_playlist():
    playlist_id = request.args.get('id', type=str)
    tracks_old = get_playlist_tracks(playlist_id)
    playlist = Playlist.query.filter_by(playlist_id=playlist_id).first()
    tracks_new = get_user_top_tracks(playlist.time_range, playlist.tracks)
    tracks_added = get_tracks_added(tracks_new, tracks_old)
    tracks_removed = get_tracks_removed(tracks_old, tracks_new)
    return render_template('check_playlist.html', playlist_id=playlist_id, tracks_added=tracks_added, tracks_removed=tracks_removed)

@app.route('/update-playlist')
def update_playlist():
    playlist_id = request.args.get('id', type=str)
    playlist = Playlist.query.filter_by(playlist_id=playlist_id).first()
    user_top_tracks_uris = get_user_top_tracks_uris(playlist.time_range, playlist.tracks)
    update = replace_playlist_tracks(playlist_id, user_top_tracks_uris)
    return redirect(url_for('playlist', id=playlist_id))

@app.route('/append-playlist')
def append_playlist():
    return redirect(url_for('playlist', id=playlist_id))
