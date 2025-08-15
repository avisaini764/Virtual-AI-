# # from flask import Flask, request, jsonify, send_from_directory
# # import os
# # import requests
# # import random
# # import urllib.parse
# # import pywhatkit

# # # local config loader (reads .env via ss.py)
# # import ss

# # # selenium wrapper (must provide a function open_google_and_search(query))
# # import selenium_web

# # app = Flask(__name__, static_folder=None)

# # # ---------- Helpers ----------
# # def news_api_key():
# #     return getattr(ss, "NEWS_API_KEY", None)

# # def weather_api_key():
# #     return getattr(ss, "WEATHER_API_KEY", None)

# # # ---------- Basic ----------
# # @app.route("/")
# # def home():
# #     return jsonify({"message": "Voice Assistant API is running!"})

# # @app.route("/index.html")
# # def index():
# #     return send_from_directory(os.getcwd(), "index.html")

# # # ---------- News (rich items) ----------
# # @app.route("/get_news", methods=["GET"])
# # def get_news():
# #     key = news_api_key()
# #     if not key:
# #         return jsonify({"error": "NEWS_API_KEY not set in ss.py/.env"}), 500
# #     try:
# #         # newsdata.io endpoint (returns 'results' list)
# #         url = f"https://newsdata.io/api/1/news?apikey={key}&country=in&language=en&page=1"
# #         resp = requests.get(url, timeout=12)
# #         resp.raise_for_status()
# #         j = resp.json()
# #         results = []
# #         for a in j.get("results", [])[:12]:
# #             title = a.get("title") or a.get("heading") or ""
# #             link = a.get("link") or a.get("url") or ""
# #             image = a.get("image_url") or a.get("image") or ""
# #             source = a.get("source_id") or a.get("source_name") or ""
# #             description = a.get("description") or a.get("content") or ""
# #             results.append({
# #                 "title": title,
# #                 "link": link,
# #                 "image": image,
# #                 "source": source,
# #                 "description": description
# #             })
# #         return jsonify({"news": results}), 200
# #     except Exception as e:
# #         return jsonify({"error": f"News fetch failed: {e}"}), 500

# # # ---------- Weather ----------
# # @app.route("/get_weather", methods=["GET"])
# # def get_weather():
# #     city = request.args.get("city", "").strip()
# #     key = weather_api_key()
# #     if not key:
# #         return jsonify({"error": "WEATHER_API_KEY not set in ss.py/.env"}), 500
# #     if not city:
# #         return jsonify({"error": "City parameter is required"}), 400
# #     try:
# #         safe_city = urllib.parse.quote(city)
# #         url = f"http://api.openweathermap.org/data/2.5/weather?q={safe_city}&appid={key}"
# #         resp = requests.get(url, timeout=12)
# #         resp.raise_for_status()
# #         return jsonify(resp.json()), 200
# #     except Exception as e:
# #         return jsonify({"error": f"Weather fetch failed: {e}"}), 500

# # # ---------- Wikipedia (REST summary) ----------
# # @app.route("/search_wikipedia", methods=["GET"])
# # def search_wikipedia():
# #     query = request.args.get("query", "").strip()
# #     if not query:
# #         return jsonify({"error": "Query parameter is required"}), 400
# #     try:
# #         safe_q = urllib.parse.quote(query)
# #         rest_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_q}"
# #         r = requests.get(rest_url, timeout=10)
# #         if r.status_code == 200:
# #             j = r.json()
# #             result = {
# #                 "title": j.get("title"),
# #                 "extract": j.get("extract"),
# #                 "thumbnail": j.get("thumbnail", {}).get("source", ""),
# #                 "url": j.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{safe_q}")
# #             }
# #             return jsonify({"result": result}), 200
# #         elif r.status_code == 404:
# #             return jsonify({"error": "No Wikipedia page found for that query"}), 200
# #         else:
# #             return jsonify({"error": f"Wikipedia REST API error: {r.status_code}"}), 500
# #     except Exception as e:
# #         return jsonify({"error": f"Wikipedia error: {e}"}), 500

# # # ---------- Google search (Selenium) ----------
# # @app.route("/search_google", methods=["GET"])
# # def search_google():
# #     query = request.args.get("query", "").strip()
# #     if not query:
# #         return jsonify({"error": "Query parameter is required"}), 400
# #     try:
# #         selenium_web.open_google_and_search(query)
# #         return jsonify({"status": f"Opened Google and searched for: {query}"}), 200
# #     except Exception as e:
# #         return jsonify({"error": f"Selenium error: {e}"}), 500

# # # ---------- YouTube ----------
# # @app.route("/open_youtube", methods=["GET"])
# # def open_youtube():
# #     return jsonify({"status": "ok"}), 200

# # @app.route("/play_youtube", methods=["GET"])
# # def play_youtube():
# #     query = request.args.get("query", "").strip()
# #     if not query:
# #         return jsonify({"error": "Query parameter is required"}), 400
# #     try:
# #         # This opens the video in your default browser using pywhatkit
# #         pywhatkit.playonyt(query)
# #         return jsonify({"status": f"Playing {query} on YouTube"}), 200
# #     except Exception as e:
# #         return jsonify({"error": f"YouTube play failed: {e}"}), 500

# # # ---------- Joke (local) ----------
# # @app.route("/get_joke", methods=["GET"])
# # def get_joke():
# #     jokes = [
# #         "Why don't skeletons fight each other? They don't have the guts.",
# #         "I'm on a seafood diet. I see food and I eat it.",
# #         "Why did the computer show up at work late? It had a hard drive.",
# #         "Why did the scarecrow win an award? Because he was outstanding in his field.",
# #         "Why did the math book look sad? Because it had too many problems."
# #     ]
# #     return jsonify({"joke": random.choice(jokes)})

# # # ---------- Quote (online with offline fallback) ----------
# # @app.route("/get_quote", methods=["GET"])
# # def get_quote():
# #     local_quotes = [
# #         {"quote": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
# #         {"quote": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
# #         {"quote": "Success is not final, failure is not fatal: It is the courage to continue that counts.", "author": "Winston Churchill"},
# #         {"quote": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
# #         {"quote": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"}
# #     ]
# #     try:
# #         r = requests.get("https://api.quotable.io/random", timeout=8)
# #         if r.status_code == 200:
# #             data = r.json()
# #             return jsonify({"quote": data.get("content"), "author": data.get("author")}), 200
# #         else:
# #             raise Exception("API error")
# #     except Exception:
# #         return jsonify(random.choice(local_quotes)), 200

# # # ---------- Run ----------
# # if __name__ == "__main__":
# #     # Flask debug for dev; change host/port when deploying
# #     app.run(debug=True)



# import os
# import random
# import urllib.parse
# import webbrowser
# from functools import wraps
# import logging

# import requests
# from flask import Flask, jsonify, request

# # Local config loader (ss.py should contain your API keys)
# # e.g., NEWS_API_KEY = "your_key_here"
# try:
#     import ss
#     import selenium_web
# except ImportError:
#     print("Warning: ss.py or selenium_web.py not found. Some features will be disabled.")
#     ss = object()
#     selenium_web = object()

# # --- App Configuration ---
# app = Flask(__name__, static_folder="static", static_url_path="")
# app.config['NEWS_API_KEY'] = getattr(ss, "NEWS_API_KEY", None)
# app.config['WEATHER_API_KEY'] = getattr(ss, "WEATHER_API_KEY", None)

# # Set up basic logging to see errors in the console
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Constants ---
# NEWS_API_URL = "https://newsdata.io/api/1/news"
# WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
# WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
# QUOTABLE_API_URL = "https://api.quotable.io/random"

# JOKES = [
#     "Why don't skeletons fight each other? They don't have the guts.",
#     "I'm on a seafood diet. I see food and I eat it.",
#     "Why did the computer show up at work late? It had a hard drive.",
#     "Why did the scarecrow win an award? Because he was outstanding in his field.",
#     "Why did the math book look sad? Because it had too many problems."
# ]

# LOCAL_QUOTES = [
#     {"quote": "The best way to predict the future is to create it.", "author": "Peter Drucker"},
#     {"quote": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
#     {"quote": "Success is not final, failure is not fatal: It is the courage to continue that counts.", "author": "Winston Churchill"},
#     {"quote": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
#     {"quote": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"}
# ]

# # --- Custom Error Handling ---
# class ApiError(Exception):
#     """Custom exception for API-related errors."""
#     def __init__(self, message, status_code=500):
#         super().__init__(message)
#         self.status_code = status_code

# @app.errorhandler(ApiError)
# def handle_api_error(error):
#     """Handles custom ApiError exceptions."""
#     app.logger.error(f"ApiError: {error}")
#     response = {"status": "error", "message": str(error)}
#     return jsonify(response), error.status_code

# @app.errorhandler(Exception)
# def handle_generic_error(error):
#     """Handles all other unhandled exceptions."""
#     app.logger.error(f"Unhandled Exception: {error}", exc_info=True)
#     response = {"status": "error", "message": "An unexpected server error occurred."}
#     return jsonify(response), 500

# # --- Decorators ---
# def require_api_key(key_name: str):
#     """Decorator to protect routes that need an API key."""
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if not app.config.get(key_name):
#                 raise ApiError(f"Server configuration error: {key_name} is not set.", 500)
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# # --- API Routes ---

# @app.route("/")
# def home():
#     """Serves the main index.html file from the 'static' folder."""
#     return app.send_static_file("index.html")

# @app.route("/get_news", methods=["GET"])
# @require_api_key('NEWS_API_KEY')
# def get_news():
#     """Fetches top news headlines for India from NewsData.io."""
#     params = {
#         "apikey": app.config['NEWS_API_KEY'],
#         "country": "in",
#         "language": "en",
#     }
#     resp = requests.get(NEWS_API_URL, params=params, timeout=12)
#     resp.raise_for_status()  # Will raise an exception for 4xx/5xx errors

#     data = resp.json().get("results", [])[:12]
#     results = [
#         {
#             "title": item.get("title", "No Title"),
#             "link": item.get("link"),
#             "image": item.get("image_url"),
#             "source": item.get("source_id"),
#             "description": item.get("description", "")
#         }
#         for item in data
#     ]
#     return jsonify({"news": results})

# @app.route("/get_weather", methods=["GET"])
# @require_api_key('WEATHER_API_KEY')
# def get_weather():
#     """Fetches weather data for a given city from OpenWeatherMap."""
#     city = request.args.get("city", "").strip()
#     if not city:
#         raise ApiError("City parameter is required", 400)
    
#     params = {"q": city, "appid": app.config['WEATHER_API_KEY']}
#     resp = requests.get(WEATHER_API_URL, params=params, timeout=12)
#     resp.raise_for_status()
#     return jsonify(resp.json())

# @app.route("/search_wikipedia", methods=["GET"])
# def search_wikipedia():
#     """Fetches a summary of a topic from Wikipedia's REST API."""
#     query = request.args.get("query", "").strip()
#     if not query:
#         raise ApiError("Query parameter is required", 400)

#     safe_q = urllib.parse.quote(query)
#     url = f"{WIKIPEDIA_API_URL}{safe_q}"
    
#     resp = requests.get(url, timeout=10)
#     if resp.status_code == 404:
#         return jsonify({"error": "No Wikipedia page found for that query"}), 200 # Return 200 so frontend handles it as a valid "not found" response
    
#     resp.raise_for_status() # Handle other errors
    
#     j = resp.json()
#     result = {
#         "title": j.get("title"),
#         "extract": j.get("extract"),
#         "thumbnail": j.get("thumbnail", {}).get("source"),
#         "url": j.get("content_urls", {}).get("desktop", {}).get("page")
#     }
#     return jsonify({"result": result})

# @app.route("/search_google", methods=["GET"])
# def search_google():
#     """Launches a Google search on the local machine using Selenium."""
#     query = request.args.get("query", "").strip()
#     if not query:
#         raise ApiError("Query parameter is required", 400)
    
#     if not hasattr(selenium_web, 'open_google_and_search'):
#         raise ApiError("Selenium module is not correctly configured on the server.", 501)

#     selenium_web.open_google_and_search(query)
#     return jsonify({"status": f"Opened Google and searched for: {query}"})

# @app.route("/play_youtube", methods=["GET"])
# def play_youtube():
#     """Opens a YouTube search for a query in the local machine's default browser."""
#     query = request.args.get("query", "").strip()
#     if not query:
#         raise ApiError("Query parameter is required", 400)

#     # Use the lightweight, built-in webbrowser module instead of pywhatkit
#     search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
#     webbrowser.open(search_url)
#     return jsonify({"status": f"Opening YouTube search for '{query}'"})

# @app.route("/get_joke", methods=["GET"])
# def get_joke():
#     """Returns a random joke from a predefined list."""
#     return jsonify({"joke": random.choice(JOKES)})

# @app.route("/get_quote", methods=["GET"])
# def get_quote():
#     """Returns a random quote, fetching from an API with a local fallback."""
#     try:
#         resp = requests.get(QUOTABLE_API_URL, timeout=8)
#         resp.raise_for_status()
#         data = resp.json()
#         return jsonify({"quote": data.get("content"), "author": data.get("author")})
#     except requests.exceptions.RequestException as e:
#         app.logger.warning(f"Quotable API failed: {e}. Using local fallback.")
#         return jsonify(random.choice(LOCAL_QUOTES))

# # --- Run Application ---
# if __name__ == "__main__":
#     # For development: debug=True
#     # For production: use a proper WSGI server like Gunicorn or Waitress
#     app.run(host="0.0.0.0", port=5000, debug=True)

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