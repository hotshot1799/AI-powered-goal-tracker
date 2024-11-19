from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Goal, ProgressUpdate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os
import traceback

app = Flask(__name__)
CORS(app)

# Configure database
database_url = os.environ.get('DATABASE_URL', 'sqlite:///goals.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config.update(
    SQLALCHEMY_DATABASE_URI=database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Debug logging function
def log_debug(message, data=None):
    print(f"DEBUG: {message}")
    if data:
        print(f"DATA: {data}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
        
    try:
        data = request.get_json()
        log_debug("Registration attempt", data)
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Check existing username/email
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"success": False, "error": "Username already exists"}), 409
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"success": False, "error": "Email already exists"}), 409

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        log_debug(f"User registered successfully", {"username": new_user.username})
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user_id": new_user.id
        })
        
    except Exception as e:
        db.session.rollback()
        log_debug(f"Registration error: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Registration failed"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json()
        log_debug("Login attempt", data)
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            log_debug(f"Login successful", {"username": user.username, "user_id": user.id})
            return jsonify({
                "success": True,
                "user_id": user.id,
                "username": user.username
            })
        
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
        
    except Exception as e:
        log_debug(f"Login error: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Login failed"}), 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/set_goal', methods=['POST'])
def create_goal():
    try:
        data = request.get_json()
        log_debug("Goal creation attempt", data)
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        user = User.query.get(data.get('user_id'))
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        goal = Goal(
            category=data['category'],
            description=data['description'],
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date(),
            user_id=user.id
        )
        
        db.session.add(goal)
        db.session.commit()
        
        log_debug("Goal created successfully", {
            "goal_id": goal.id,
            "user_id": user.id
        })
        
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
        log_debug(f"Goal creation error: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Failed to create goal"}), 500

@app.route('/get_goals/<int:user_id>')
def retrieve_goals(user_id):
    try:
        log_debug(f"Fetching goals for user", {"user_id": user_id})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        goals = [
            {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat(),
                "progress": 0  # You can implement progress calculation logic
            } for goal in user.goals
        ]
        
        return jsonify({
            "success": True,
            "goals": goals
        })
        
    except Exception as e:
        log_debug(f"Error fetching goals: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Failed to fetch goals"}), 500

@app.route('/update_goal', methods=['PUT'])
def update_goal():
    try:
        data = request.get_json()
        log_debug("Goal update attempt", data)
        
        if not data or 'id' not in data:
            return jsonify({"success": False, "error": "Invalid request"}), 400

        goal = Goal.query.get(data['id'])
        if not goal:
            return jsonify({"success": False, "error": "Goal not found"}), 404

        if 'category' in data:
            goal.category = data['category']
        if 'description' in data:
            goal.description = data['description']
        if 'target_date' in data:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()

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
        })
        
    except Exception as e:
        db.session.rollback()
        log_debug(f"Goal update error: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Failed to update goal"}), 500

@app.route('/delete_goal/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    try:
        log_debug("Goal deletion attempt", {"goal_id": goal_id})
        
        goal = Goal.query.get(goal_id)
        if not goal:
            return jsonify({"success": False, "error": "Goal not found"}), 404

        db.session.delete(goal)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Goal deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        log_debug(f"Goal deletion error: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Failed to delete goal"}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    if request.is_json:
        return jsonify({"success": False, "error": "Resource not found"}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.is_json:
        return jsonify({"success": False, "error": "Internal server error"}), 500
    return render_template('500.html'), 500

# Initialize database
def init_db():
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            traceback.print_exc()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
