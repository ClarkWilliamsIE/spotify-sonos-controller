from flask import Flask, request, redirect, jsonify
import requests, os

app = Flask(__name__)

# Spotify App Credentials from Render Environment Variables
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN")  # You must manually set this in Render

# Hardcoded playlist list
playlists = [
    {"name": "Morning Chill", "uri": "spotify:playlist:7Kra2IBWzl51pB16RlrOt2"},
    {"name": "Top Hits NZ", "uri": "spotify:playlist:37i9dQZEVXcGxuK4C0FSOl"},
    {"name": "Lo-Fi Vibes", "uri": "spotify:playlist:1ighsAlXR1hjYgTtD0w3H2"},
    {"name": "Throwback Jams", "uri": "spotify:playlist:5bXu3F3e1rMZvSRDrePfSz"},
]

@app.route("/")
def index():
    return '<a href="/login">Login with Spotify</a>'

@app.route("/login")
def login():
    scope = "user-modify-playback-state user-read-playback-state"
    return redirect(f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    tokens = response.json()
    return f"Access Token: {tokens.get('access_token')}<br>Refresh Token: {tokens.get('refresh_token')}"

# Function to get a new access token using the refresh token
def get_access_token():
    refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    print("🔐 Trying to refresh token...")
    print("Refresh token:", refresh_token is not None)
    print("Client ID:", client_id is not None)

    response = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    })

    print("🔁 Spotify response:", response.status_code, response.text)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

# Endpoint to return list of playlists
@app.route("/playlists")
def get_playlists():
    return jsonify(playlists)

# Endpoint to play a selected playlist
@app.route("/play", methods=["POST"])
def play_playlist():
    data = request.get_json()
    playlist_uri = data.get("uri")

    access_token = get_access_token()
    if not access_token:
        return "Failed to refresh access token", 401

    response = requests.put(
        "https://api.spotify.com/v1/me/player/play",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"context_uri": playlist_uri}
    )

    if response.status_code == 204:
        return "Playing playlist", 200
    else:
        return f"Error: {response.status_code}, {response.text}", 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

