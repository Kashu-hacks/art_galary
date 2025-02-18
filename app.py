from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key

# Configure SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# **User Model (Table)**
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# **Homepage**
@app.route('/')
def index():
    return render_template('index.html')

# **Home Page**
@app.route('/home')
def home():
    return render_template('home.html')

# **Render Signup Page**
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# **Handle Signup Form Submission**
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Fetch JSON data from frontend
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "All fields are required!"}), 400

    # Check if email already exists
    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({"error": "Email already registered!"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Signup successful! Please login."}), 200

# **Render Login Page**
@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Get JSON data from frontend
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"message": "Login successful!", "redirect": url_for('main_page')}), 200
    else:
        return jsonify({"error": "Invalid email or password!"}), 401

# **Logout Route**
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))  # Redirect to home page after logout

# **Main Page Route**
@app.route('/main')
def main_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to home page if not logged in
    return render_template('main.html', user_name=session['user_name'])

# **Create Database and Run the App**
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
