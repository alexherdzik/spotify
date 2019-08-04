from flask import Flask, request, redirect, render_template, url_for
from spotify import app_authorization, user_authorization, get_user_top_tracks

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
    time_range = request.args.get('time_range', 'medium_term', type=str)
    user_top_tracks = get_user_top_tracks(time_range)
    return render_template('top_tracks.html', tracks=user_top_tracks)
