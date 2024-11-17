from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Goal, ProgressUpdate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
CORS(app)

# Configure database and secret key
database_url = os.environ.get('DATABASE_URL', 'sqlite:///goals.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
        
    try:
        data = request.get_json()
        print(f"Registration attempt data: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False, 
                    "error": f"Missing required field: {field}"
                }), 400

        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                "success": False, 
                "error": "Username already exists"
            }), 409
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                "success": False, 
                "error": "Email already exists"
            }), 409

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"User registered successfully: {new_user.username}")
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user_id": new_user.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Registration failed"
        }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    try:
        data = request.get_json()
        print(f"Login attempt data: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                "success": False, 
                "error": "Username and password required"
            }), 400

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            print(f"Login successful for user: {user.username}")
            return jsonify({
                "success": True,
                "user_id": user.id,
                "username": user.username
            })
        
        return jsonify({
            "success": False, 
            "error": "Invalid credentials"
        }), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "Login failed"
        }), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
            
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return jsonify({"error": "Failed to load dashboard"}), 500

@app.route('/get_goals/<int:user_id>')
@login_required
def get_goals(user_id):
    try:
        if int(session['user_id']) != user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        goals = [
            {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat()
            } for goal in user.goals
        ]
        
        return jsonify({
            "success": True,
            "goals": goals
        })
    except Exception as e:
        print(f"Error fetching goals: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch goals"}), 500

@app.route('/set_goal', methods=['POST'])
@login_required
def create_goal():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        goal = Goal(
            category=data['category'],
            description=data['description'],
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date(),
            user_id=user_id
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "goal": {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Goal creation error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to create goal"}), 500

# Initialize database
def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
            
            # Create test user if none exists
            if not User.query.first():
                test_user = User(
                    username="test",
                    email="test@example.com"
                )
                test_user.set_password("test123")
                db.session.add(test_user)
                db.session.commit()
                print("Test user created successfully")
                
        except Exception as e:
            print(f"Database initialization error: {str(e)}")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
