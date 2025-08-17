import os
import requests
from flask import Flask, jsonify, request, Response, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# --- 1. SETUP ---
app = Flask(__name__)

# Load environment variables
load_dotenv()

# --- SECURITY & DATABASE CONFIGURATION ---
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evoai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Name of the login route function

# --- FIX: Explicitly set CORS for all API routes ---
CORS(app, resources={r"/*": {"origins": "*"}})

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
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    conversations = db.relationship('Conversation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create the database tables
with app.app_context():
    db.create_all()

# ==============================================================================
# --- 2. AUTHENTICATION ROUTES ---
# ==============================================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Logged in successfully", "user_id": user.id}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

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
        return jsonify({"error": "AI model is not configured. Check API key."}), 500
        
    data = request.get_json()
    prompt = data.get('prompt')
    user_id = data.get('user_id')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    full_response = ""
    def stream_response():
        nonlocal full_response
        response_chunks = model.generate_content(prompt, stream=True)
        for chunk in response_chunks:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
                
    if user_id and user_id is not None:
        user = User.query.get(user_id)
        if user:
            # Save query to database before streaming response
            new_conversation = Conversation(user_id=user.id, query=prompt, response="")
            db.session.add(new_conversation)
            db.session.commit()
            
            # Stream the response and update the conversation entry
            stream_gen = stream_response()
            for chunk in stream_gen:
                yield chunk

            new_conversation.response = full_response
            db.session.commit()
        else:
            return jsonify({"error": "User not found"}), 404
    else:
        return Response(stream_response(), mimetype='text/plain')
        
    
@app.route('/get_conversations')
@login_required
def get_conversations():
    conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.timestamp).all()
    conversation_list = [{"query": c.query, "response": c.response} for c in conversations]
    return jsonify(conversation_list)

# --- 4. OTHER API ROUTES (No changes here, except for potential login_required decorators) ---
# For now, we won't add @login_required to these, so they can still be used without an account.
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
    # When deploying to Render, you'll need to remove the debug=True and port=5000 arguments
    # and use the default behavior for the production server.
    app.run(debug=True, port=5000)