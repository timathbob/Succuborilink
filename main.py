import os
from flask import Flask, redirect, request, make_response
import tweepy
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

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
        token_data = json.dumps(auth.request_token)

        response = make_response(redirect(redirect_url))
        response.set_cookie("twitter_token", token_data, max_age=300, secure=True, httponly=True, samesite='Strict')
        return response
    except Exception as e:
        return f"Error during auth: {e}"

@app.route('/callback')
def callback():
    token_cookie = request.cookies.get("twitter_token")
    verifier = request.args.get('oauth_verifier')

    if not token_cookie or not verifier:
        return "Missing token or verifier."

    token = json.loads(token_cookie)

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
        api = tweepy.API(auth)

        api.update_profile_banner("banner.jpg")
        api.update_profile_image("profile.jpg")
        api.update_profile(description="loyal pet of @succubori")

        return "Profile successfully updated!"
    except Exception as e:
        return f"Error updating profile: {e}"


