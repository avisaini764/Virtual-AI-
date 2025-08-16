import os
import random
import urllib.parse
import logging

import requests
from flask import Flask, jsonify, request, redirect

# --- IMPORTANT ---
# The selenium_web and webbrowser features have been replaced with redirects 
# to make the app compatible with cloud deployment.
# ss.py is no longer used for configuration. We now use Environment Variables.

# --- App Configuration ---
app = Flask(__name__, static_folder="static", static_url_path="")
# Read API keys from Environment Variables
app.config['NEWS_API_KEY'] = os.environ.get('NEWS_API_KEY')
app.config['WEATHER_API_KEY'] = os.environ.get('WEATHER_API_KEY')

# Set up basic logging to see errors in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
NEWS_API_URL = "https://newsdata.io/api/1/news"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
QUOTABLE_API_URL = "https://api.quotable.io/random"

JOKES = [
    "Why don't skeletons fight each other? They don't have the guts.",
    "I'm on a seafood diet. I see food and I eat it.",
    "Why did the computer show up at work late? It had a hard drive.",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "Why did the math book look sad? Because it had too many problems."
]

LOCAL_QUOTES = [
    {"quote": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
    {"quote": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
    {"quote": "Success is not final, failure is not fatal: It is the courage to continue that counts.", "author": "Winston Churchill"},
    {"quote": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
    {"quote": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"}
]

# --- Custom Error Handling ---
class ApiError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code

@app.errorhandler(ApiError)
def handle_api_error(error):
    """Handles custom ApiError exceptions."""
    app.logger.error(f"ApiError: {error}")
    response = {"status": "error", "message": str(error)}
    return jsonify(response), error.status_code

@app.errorhandler(Exception)
def handle_generic_error(error):
    """Handles all other unhandled exceptions."""
    app.logger.error(f"Unhandled Exception: {error}", exc_info=True)
    response = {"status": "error", "message": "An unexpected server error occurred."}
    return jsonify(response), 500

# --- API Routes ---

@app.route("/")
def home():
    """Serves the main index.html file from the 'static' folder."""
    return app.send_static_file("index.html")

@app.route("/get_news", methods=["GET"])
def get_news():
    """Fetches top news headlines for India from NewsData.io."""
    if not app.config.get('NEWS_API_KEY'):
        raise ApiError("Server configuration error: NEWS_API_KEY is not set.", 500)
    
    params = {
        "apikey": app.config['NEWS_API_KEY'],
        "country": "in",
        "language": "en",
    }
    resp = requests.get(NEWS_API_URL, params=params, timeout=12)
    resp.raise_for_status()

    data = resp.json().get("results", [])[:12]
    results = [
        {
            "title": item.get("title", "No Title"),
            "link": item.get("link"),
            "image": item.get("image_url"),
            "source": item.get("source_id"),
            "description": item.get("description", "")
        }
        for item in data
    ]
    return jsonify({"news": results})

@app.route("/get_weather", methods=["GET"])
def get_weather():
    """Fetches weather data for a given city from OpenWeatherMap."""
    if not app.config.get('WEATHER_API_KEY'):
        raise ApiError("Server configuration error: WEATHER_API_KEY is not set.", 500)
        
    city = request.args.get("city", "").strip()
    if not city:
        raise ApiError("City parameter is required", 400)
    
    params = {"q": city, "appid": app.config['WEATHER_API_KEY']}
    resp = requests.get(WEATHER_API_URL, params=params, timeout=12)
    resp.raise_for_status()
    return jsonify(resp.json())

@app.route("/search_wikipedia", methods=["GET"])
def search_wikipedia():
    """Fetches a summary of a topic from Wikipedia's REST API."""
    query = request.args.get("query", "").strip()
    if not query:
        raise ApiError("Query parameter is required", 400)

    safe_q = urllib.parse.quote(query)
    url = f"{WIKIPEDIA_API_URL}{safe_q}"
    
    resp = requests.get(url, timeout=10)
    if resp.status_code == 404:
        return jsonify({"error": "No Wikipedia page found for that query"}), 200
    
    resp.raise_for_status()
    
    j = resp.json()
    result = {
        "title": j.get("title"),
        "extract": j.get("extract"),
        "thumbnail": j.get("thumbnail", {}).get("source"),
        "url": j.get("content_urls", {}).get("desktop", {}).get("page")
    }
    return jsonify({"result": result})

@app.route("/search_google", methods=["GET"])
def search_google():
    """MODIFIED FOR DEPLOYMENT: Redirects the user's browser to a Google search results page."""
    query = request.args.get("query", "").strip()
    if not query:
        raise ApiError("Query parameter is required", 400)
    
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    return redirect(search_url)

@app.route("/play_youtube", methods=["GET"])
def play_youtube():
    """MODIFIED FOR DEPLOYMENT: Redirects the user's browser to a YouTube search results page."""
    query = request.args.get("query", "").strip()
    if not query:
        raise ApiError("Query parameter is required", 400)

    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    return redirect(search_url)

@app.route("/get_joke", methods=["GET"])
def get_joke():
    """Returns a random joke from a predefined list."""
    return jsonify({"joke": random.choice(JOKES)})

@app.route("/get_quote", methods=["GET"])
def get_quote():
    """Returns a random quote, fetching from an API with a local fallback."""
    try:
        resp = requests.get(QUOTABLE_API_URL, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return jsonify({"quote": data.get("content"), "author": data.get("author")})
    except requests.exceptions.RequestException as e:
        app.logger.warning(f"Quotable API failed: {e}. Using local fallback.")
        return jsonify(random.choice(LOCAL_QUOTES))

# This block is for local development only and will not be used by Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)