import os
from flask import Flask, redirect, request, session
import tweepy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "defaultsecret")  # Use a fixed key for session to work

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
CALLBACK_URL = "https://succuborilink.vercel.app/callback"

@app.route('/')
def index():
    return '<a href="/login">Authorize with Twitter</a>'

@app.route('/login')
def login():
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    try:
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
        return redirect(redirect_url)
    except Exception as e:
        return f"Error during auth: {e}"

@app.route('/callback')
def callback():
    request_token = session.pop('request_token', None)
    if not request_token:
        return "No request token found"

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth.request_token = request_token
    verifier = request.args.get('oauth_verifier')
    try:
        auth.get_access_token(verifier)
        api = tweepy.API(auth)

        # Upload banner and profile picture
        api.update_profile_banner("banner.jpg")
        api.update_profile_image("profile.jpg")

        # Update bio
        api.update_profile(description="loyal pet of @succubori")

        return "Profile successfully updated!"
    except Exception as e:
        return f"Error updating profile: {e}"

# Needed to expose the app object to Vercel
app = app

