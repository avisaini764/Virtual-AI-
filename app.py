import os
import requests
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. SETUP ---
app = Flask(__name__)
CORS(app) 
load_dotenv()

# --- API KEY CONFIGURATION ---
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Make sure it's set in your .env file.")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

# --- 2. GEMINI AI STREAMING ROUTE ---
@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    if not model:
        return jsonify({"error": "AI model is not configured. Check API key."}), 500
        
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # This is a generator function that will stream the response
        def stream_response():
            # Use stream=True to get chunks as they are generated
            response_chunks = model.generate_content(prompt, stream=True)
            for chunk in response_chunks:
                if chunk.text:
                    yield chunk.text # Send each piece of text to the frontend
        
        return Response(stream_response(), mimetype='text/plain')
        
    except Exception as e:
        print(f"Error with Gemini API stream: {e}")
        return jsonify({"error": f"An error occurred with the AI service: {e}"}), 500

# --- 3. OTHER API ROUTES ---
@app.route('/get_news')
def get_news():
    if not NEWS_API_KEY:
        return jsonify({"error": "News API key is missing."}), 500
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        formatted_news = {"news": [{"title": article.get("title"),"description": article.get("description"),"link": article.get("url"),"image": article.get("urlToImage"),"source": article.get("source",{}).get("name")} for article in data.get("articles",[])[:5]]}
        return jsonify(formatted_news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_weather')
def get_weather():
    if not WEATHER_API_KEY:
        return jsonify({"error": "Weather API key is missing."}), 500
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is missing"}), 400
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search_wikipedia')
def search_wikipedia():
    query = request.args.get('query')
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {"action":"query","prop":"extracts|pageimages","exintro":True,"explaintext":True,"generator":"search","gsrsearch":query,"gsrlimit":1,"format":"json","pithumbsize":200}
    try:
        response = S.get(url=URL,params=PARAMS)
        data = response.json()
        page_id = list(data['query']['pages'].keys())[0]
        page = data['query']['pages'][page_id]
        result = {"title":page['title'],"extract":page['extract'],"url":f"https://en.wikipedia.org/?curid={page_id}","thumbnail":page.get('thumbnail',{}).get('source')}
        return jsonify({"result":result})
    except Exception:
        return jsonify({"error": f"No Wikipedia result found for '{query}'."})

@app.route('/get_joke')
def get_joke():
    response = requests.get("https://v2.jokeapi.dev/joke/Any")
    data = response.json()
    if data.get('type') == 'twopart':
        joke = f"{data['setup']} ... {data['delivery']}"
    else:
        joke = data.get('joke', 'Could not find a joke.')
    return jsonify({"joke": joke})

@app.route('/get_quote')
def get_quote():
    response = requests.get("https://api.quotable.io/random")
    data = response.json()
    return jsonify({"quote":data.get('content'),"author":data.get('author')})

if __name__ == '__main__':
    app.run(debug=True, port=5000)