from flask import Flask, request, redirect, render_template
from spotify import app_authorization, user_authorization, get_user_top_tracks

app = Flask(__name__)

@app.route('/')
def index():
    auth_url = app_authorization()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    authorization_header = user_authorization()
    user_top_tracks = get_user_top_tracks(authorization_header)
    return render_template('callback.html', tracks=user_top_tracks)

    """
    user_profile_api_endpoint = f'{SPOTIFY_API_URL}/me'
    profile_request = requests.get(user_profile_api_endpoint, headers=authorization_header)

    profile_data = json.loads(profile_request.text)

    return f'{profile_request.text}'
    """
