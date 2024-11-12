from flask import Flask, render_template, request, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Goal, ProgressUpdate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import traceback
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure database
database_url = os.environ.get('DATABASE_URL', 'sqlite:///goals.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Initialize the db with the app
db.init_app(app)
migrate = Migrate(app, db)

def calculate_goal_progress(goal):
    """Calculate progress for a goal"""
    updates_count = len(goal.progress_updates)
    if updates_count == 0:
        return 0
    # Simple progress calculation - can be enhanced
    return min(100, updates_count * 20)  # 20% progress per update, max 100%

# Custom JSON error handler
@app.errorhandler(404)
def not_found_error(error):
    if request.is_json or request.headers.get('Accept') == 'application/json':
        response = jsonify({
            "success": False,
            "error": "Resource not found",
            "path": request.path
        })
        return response, 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.is_json or request.headers.get('Accept') == 'application/json':
        response = jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(error)
        })
        return response, 500
    return render_template('500.html'), 500

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

# Initialize database on startup
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({"success": False, "error": "Username already exists"}), 409
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"success": False, "error": "Email already exists"}), 409
        
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": user.id
        })
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Registration failed"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    try:
        # Log received data
        print("Received login request")
        data = request.get_json()
        print(f"Login data: {data}")
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                "success": False,
                "error": "Username and password required"
            }), 400

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            print(f"Login successful for user: {username}")
            return jsonify({
                "success": True,
                "user_id": user.id,
                "username": user.username
            })
            
        print(f"Login failed for user: {username}")
        return jsonify({
            "success": False,
            "error": "Invalid credentials"
        }), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        return jsonify({
            "success": False,
            "error": "Login failed"
        }), 500

@app.route('/set_goal', methods=['POST'])
def create_goal():
    try:
        data = request.get_json()
        print(f"Received goal creation request with data: {data}")  # Debug log
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "User ID is required"}), 400
            
        # Convert user_id to int if it's a string
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid user ID format"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": f"User not found with ID: {user_id}"}), 404

        # Validate required fields
        required_fields = ['category', 'description', 'target_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        # Parse target date
        try:
            target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400

        goal = Goal(
            category=data['category'],
            description=data['description'],
            target_date=target_date,
            user_id=user_id
        )
        
        db.session.add(goal)
        db.session.commit()
        
        response_data = {
            "success": True,
            "goal": {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat()
            }
        }
        
        print(f"Created goal successfully: {response_data}")  # Debug log
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        print(f"Goal creation error: {str(e)}\n{error_details}")
        return jsonify({
            "success": False,
            "error": "Failed to create goal",
            "details": str(e)
        }), 500

@app.route('/get_goals/<user_id>')
def retrieve_goals(user_id):
    try:
        if not user_id or user_id == 'null':
            return jsonify({
                "success": False,
                "error": "Valid user ID is required"
            }), 400

        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid user ID format"
            }), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": f"User not found with ID: {user_id}"
            }), 404

        goals = [
            {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat(),
                "progress": calculate_goal_progress(goal)
            } for goal in user.goals
        ]
        
        return jsonify({
            "success": True,
            "goals": goals
        })
        
    except Exception as e:
        print(f"Error retrieving goals: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve goals",
            "details": str(e)
        }), 500

# Add a health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    # Get port from environment variable for Render deployment
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true')
