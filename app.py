import os
import requests
from flask import Flask, jsonify, request, Response, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from sqlalchemy.orm import Mapped, mapped_column
import json

# --- 1. SETUP ---
app = Flask(__name__)

# Load environment variables
load_dotenv()

# --- SECURITY & DATABASE CONFIGURATION ---
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")

if os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.root_path, "evoai.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

CORS(app, supports_credentials=True)

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

# --- DATABASE MODELS ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
class Conversation(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query: Mapped[str] = mapped_column(db.Text, nullable=False)
    response: Mapped[str] = mapped_column(db.Text, nullable=False)
    timestamp: Mapped[db.DateTime] = mapped_column(db.DateTime, default=db.func.current_timestamp())

# Create the database tables
with app.app_context():
    db.create_all()

# ==============================================================================
# --- 2. AUTHENTICATION ROUTES ---
# ==============================================================================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db.session.scalar(db.select(User).filter_by(username=username))

    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Logged in successfully", "user_id": user.id}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    
@app.route('/login_page', methods=['GET'])
def login_page():
    return jsonify({"message": "Please log in"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    existing_user = db.session.scalar(db.select(User).filter_by(username=username))
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get_user_info')
def get_user_info():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username, "user_id": current_user.id}), 200
    return jsonify({"username": None, "user_id": None}), 200

# ==============================================================================
# --- 3. SERVE THE FRONTEND & CORE API ROUTES ---
# ==============================================================================
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    if not model:
        print("Error: AI model is not configured.")
        return jsonify({"error": "AI model is not configured. Check API key."}), 500
        
    try:
        if request.data:  # FIX: Check if request has data before parsing JSON
            data = request.get_json()
            prompt = data.get('prompt')
            user_id = data.get('user_id')
            print(f"Received prompt: '{prompt}' for user_id: {user_id}")
        else:
            prompt = None
            user_id = None
            print("Received request with no data.")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return Response(json.dumps({"error": f"Invalid JSON in request: {str(e)}"}), mimetype='application/json', status=400)
        
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    full_response = ""
    def stream_response():
        nonlocal full_response
        try:
            print("Calling Gemini API...")
            response_chunks = model.generate_content(prompt, stream=True)
            for chunk in response_chunks:
                print(f"Received chunk: {chunk.text}")
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            print("Gemini API call finished.")
        except Exception as e:
            print(f"Gemini API Error: {e}")
            yield json.dumps({"error": f"Gemini API Error: {str(e)}"}).encode('utf-8')

    try:
        if user_id and user_id is not None:
            user = db.session.get(User, user_id)
            if user:
                new_conversation = Conversation(user_id=user.id, query=prompt, response="")
                db.session.add(new_conversation)
                db.session.commit()
                print("Conversation entry created.")

                response_generator = stream_response()
                for chunk in response_generator:
                    yield chunk

                with app.app_context():
                    new_conversation.response = full_response
                    db.session.commit()
                print("Conversation entry updated.")
            else:
                return jsonify({"error": "User not found"}), 404
        else:
            return Response(stream_response(), mimetype='text/plain')
            
    except Exception as e:
        print(f"Error with Gemini API or database interaction: {e}")
        return jsonify({"error": f"An error occurred with the AI service: {e}"}), 500

@app.route('/get_conversations')
@login_required
def get_conversations():
    conversations = db.session.scalars(db.select(Conversation).filter_by(user_id=current_user.id).order_by(Conversation.timestamp)).all()
    conversation_list = [{"query": c.query, "response": c.response} for c in conversations]
    return jsonify(conversation_list)

# --- 4. OTHER API ROUTES (No changes here) ---
@app.route('/get_news')
def get_news():
    if not NEWS_API_KEY: return jsonify({"error": "News API key is missing."}), 500
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
    if not WEATHER_API_KEY: return jsonify({"error": "Weather API key is missing."}), 500
    city = request.args.get('city')
    if not city: return jsonify({"error": "City parameter is missing"}), 400
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