from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Goal, ProgressUpdate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ai_analysis import analyze_data

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
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

def log_debug(message, data=None):
    print(f"DEBUG: {message}")
    if data:
        print(f"DATA: {data}")

def init_db():
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("Database tables created successfully")
            
            # Verify tables
            tables = db.engine.table_names()
            print(f"Available tables: {tables}")
            
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            traceback.print_exc()
            raise e

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

        # Check existing users
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
            # Store user data in session
            session['user_id'] = user.id
            session['username'] = user.username
            
            log_debug(f"Login successful", {
                "username": user.username, 
                "user_id": user.id,
                "session": dict(session)
            })
            
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
    # Check if user is logged in
    if 'user_id' not in session:
        log_debug("Unauthorized dashboard access attempt")
        return redirect(url_for('index'))
    
    log_debug("Dashboard access", {
        "user_id": session.get('user_id'),
        "username": session.get('username')
    })
    
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    # Clear session
    session.clear()
    return redirect(url_for('index'))

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
                "progress": 0  # You can implement proper progress calculation here
            } for goal in user.goals
        ]
        
        return jsonify({
            "success": True,
            "goals": goals
        })
        
    except Exception as e:
        log_debug(f"Error fetching goals: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"success": False, "error": "Failed to fetch goals"}), 500

@app.route('/goal/<int:goal_id>')
def goal_details(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    return render_template('goal_details.html', goal=goal)

@app.route('/update_progress/<int:goal_id>', methods=['POST'])
def update_progress(goal_id):
    try:
        data = request.get_json()
        if not data or 'update_text' not in data:
            return jsonify({"success": False, "error": "Update text required"}), 400

        goal = Goal.query.get_or_404(goal_id)
        
        # Prepare data for AI analysis
        analysis_data = {
            "goal_category": goal.category,
            "goal_description": goal.description,
            "update_text": data['update_text']
        }
        
        # Get AI analysis
        try:
            analysis_result = analyze_data(str(analysis_data))
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            analysis_result = "Unable to generate analysis at this time."

        # Create progress update
        progress_update = ProgressUpdate(
            goal_id=goal_id,
            update_text=data['update_text'],
            analysis=analysis_result
        )
        
        db.session.add(progress_update)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "update": {
                "text": progress_update.update_text,
                "analysis": progress_update.analysis,
                "created_at": progress_update.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Progress update error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_updates/<int:goal_id>')
def get_updates(goal_id):
    try:
        updates = ProgressUpdate.query.filter_by(goal_id=goal_id).order_by(ProgressUpdate.created_at.desc()).all()
        return jsonify({
            "success": True,
            "updates": [{
                "text": update.update_text,
                "analysis": update.analysis,
                "created_at": update.created_at.isoformat()
            } for update in updates]
        })
    except Exception as e:
        print(f"Error fetching updates: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
