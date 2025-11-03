from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY']='SUPER-SECRET-KEY'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'


db  = SQLAlchemy(app)
api = Api(app)
CORS(app)
jwt = JWTManager(app)


# === EXISTING USER MODEL ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)

# === UPDATED MODEL FOR RIGHTS SUGGESTIONS ===
class RightsInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    situation = db.Column(db.String(200), nullable=False, index=True) 
    rights = db.Column(db.Text, nullable=False)
    best_action = db.Column(db.Text, nullable=False)
    legal_section = db.Column(db.String(100), nullable=True) # For IPC sections
    keywords = db.Column(db.Text, nullable=True, index=True) # For better search

# === UPDATED FUNCTION TO ADD 20 SAMPLES ===
def add_sample_data():
    if RightsInfo.query.first() is None:
        print("Adding 20 sample rights info entries...")
        sample_data = [
            # ... (All 20 of your sample data entries go here) ...
            RightsInfo(
                situation="Arrest by Police",
                rights="You have the right to remain silent. You have the right to an attorney. Police must inform you of the grounds for arrest.",
                best_action="Clearly state 'I am going to remain silent and I would like a lawyer.' Do not resist arrest.",
                legal_section="CrPC Sec 41, 50, 50A",
                keywords="cops, detained, police, handcuffs, station, custody"
            ),
            RightsInfo(
                situation="Police Stop (Traffic)",
                rights="You must provide your license and registration. Police need probable cause to search your car without a warrant. You can film the interaction.",
                best_action="Stay calm and polite. Do not consent to a search. Ask if you are being detained or free to go.",
                legal_section="Motor Vehicles Act",
                keywords="car, bike, pulled over, checkpost, driving, license, traffic, police"
            ),
            # (Add all your other 18 samples here)
        ]
        
        db.session.bulk_save_objects(sample_data)
        db.session.commit()
        print("Sample data added.")

# Create database tables and add sample data
with app.app_context():
    db.create_all()
    add_sample_data() # Call the function to add data


# ===============================================
# === API ROUTES (These return JSON)
# ===============================================

@app.route('/api/search')
def api_search():
    user_input = request.args.get('q')
    results_list = []
    if user_input:
        search_term = f"%{user_input.lower()}%"
        results = RightsInfo.query.filter(
            or_(
                db.func.lower(RightsInfo.situation).like(search_term),
                db.func.lower(RightsInfo.keywords).like(search_term)
            )
        ).all()

        for item in results:
            results_list.append({
                "id": item.id, # Added ID
                "situation": item.situation,
                "rights": item.rights,
                "best_action": item.best_action,
                "legal_section": item.legal_section
            })
    return jsonify(results_list)

@app.route('/signup', methods = ['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 200

@app.route('/login', methods = ['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({"message": "Login successful!", "access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/user-info')
@jwt_required()
def user_info():
    current_user = get_jwt_identity()
    return jsonify({"username": current_user})

# ===============================================
# === PAGE SERVING ROUTES (These return HTML)
# ===============================================

# === HOMEPAGE ROUTE (CHANGED) ===
# This now serves your login page
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# === LOGIN PAGE ROUTE (CHANGED) ===
# This also serves the login page, which is fine.
# Your login.js POSTs to this, which is correct.
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# === NEW DASHBOARD ROUTE (CHANGED) ===
# This is the new home for your dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)