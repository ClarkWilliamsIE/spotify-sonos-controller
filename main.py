from flask import Flask, request, redirect
import requests, os

app = Flask(__name__)

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

