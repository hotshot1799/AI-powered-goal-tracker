from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from models import db, User, Goal, ProgressUpdate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ai_analysis import analyze_data, suggest_goal_achievement, analyze_user_input

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db with the app
db.init_app(app)
migrate = Migrate(app, db)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"success": False, "message": "Username already exists"})
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"success": False, "message": "Email already exists"})
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({
            "success": True, 
            "user_id": user.id,
            "username": user.username
        })
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/goal/<int:goal_id>')
def goal_details(goal_id):
    return render_template('goal_details.html')

@app.route('/set_goal', methods=['POST'])
def create_goal():
    data = request.json
    user = User.query.get(data['user_id'])
    if user:
        goal = Goal(
            category=data['category'],
            description=data['description'],
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date(),
            created_at=datetime.now(),
            user_id=user.id
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({"success": True, "goal": {
            "id": goal.id,
            "category": goal.category,
            "description": goal.description,
            "target_date": goal.target_date.isoformat(),
            "created_at": goal.created_at.isoformat()
        }})
    return jsonify({"success": False, "message": "User not found"})

@app.route('/get_goals/<int:user_id>')
def retrieve_goals(user_id):
    user = User.query.get(user_id)
    if user:
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
        return jsonify(goals)
    return jsonify([])

@app.route('/get_goal/<int:goal_id>')
def get_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    progress = calculate_goal_progress(goal)
    return jsonify({
        "id": goal.id,
        "category": goal.category,
        "description": goal.description,
        "target_date": goal.target_date.isoformat(),
        "created_at": goal.created_at.isoformat(),
        "progress": progress
    })

def calculate_goal_progress(goal):
    # Get all progress updates for the goal
    updates = ProgressUpdate.query.filter_by(goal_id=goal.id).all()
    if not updates:
        return 0
    
    # Convert updates to format suitable for AI analysis
    updates_data = [
        {
            "text": update.update_text,
            "date": update.created_at.isoformat(),
            "analysis": update.analysis
        } for update in updates
    ]
    
    goal_data = {
        "category": goal.category,
        "description": goal.description,
        "target_date": goal.target_date.isoformat(),
        "updates": updates_data
    }
    
    # Use AI to calculate progress
    progress = calculate_ai_progress(goal_data)
    return progress

@app.route('/update_goal', methods=['PUT'])
def modify_goal():
    data = request.json
    goal = Goal.query.get(data['id'])
    if goal:
        if 'category' in data:
            goal.category = data['category']
        if 'description' in data:
            goal.description = data['description']
        if 'target_date' in data:
            goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({"success": True, "goal": {
            "id": goal.id,
            "category": goal.category,
            "description": goal.description,
            "target_date": goal.target_date.isoformat(),
            "created_at": goal.created_at.isoformat()
        }})
    return jsonify({"success": False, "message": "Goal not found"})

@app.route('/delete_goal/<int:goal_id>', methods=['DELETE'])
def remove_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Goal not found"})

@app.route('/update_progress/<int:goal_id>', methods=['POST'])
def update_progress(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify({"success": False, "message": "Goal not found"})

    data = request.json
    user_input = data.get('update_text', '')
    
    goal_data = {
        "category": goal.category,
        "description": goal.description,
        "target_date": goal.target_date.isoformat()
    }
    
    analysis_result = analyze_user_input(goal_data, user_input)
    
    progress_update = ProgressUpdate(
        goal_id=goal.id,
        update_text=user_input,
        analysis=analysis_result['analysis']
    )
    db.session.add(progress_update)
    db.session.commit()

    # Get progress from analyze_data instead
    analysis = analyze_data(goal_data)
    progress = analysis.get('progress', 0)

    return jsonify({
        "success": True, 
        "analysis": analysis_result['analysis'],
        "progress": progress
    })

@app.route('/get_progress/<int:goal_id>')
def get_progress(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return jsonify({"success": False, "message": "Goal not found"})
    
    progress_updates = [
        {
            "id": update.id,
            "update_text": update.update_text,
            "analysis": update.analysis,
            "created_at": update.created_at.isoformat()
        } for update in goal.progress_updates
    ]
    
    return jsonify({
        "success": True,
        "progress_updates": progress_updates,
        "current_progress": calculate_goal_progress(goal)
    })

@app.route('/analyze/<int:goal_id>')
def analyze(goal_id):
    goal = Goal.query.get(goal_id)
    if goal:
        goal_data = {
            "category": goal.category,
            "description": goal.description,
            "target_date": goal.target_date.isoformat(),
            "progress": calculate_goal_progress(goal)
        }
        insights = analyze_data(goal_data)
        return jsonify(insights)
    return jsonify({"success": False, "message": "Goal not found"})

@app.route('/suggest/<int:goal_id>')
def suggest(goal_id):
    goal = Goal.query.get(goal_id)
    if goal:
        goal_data = {
            "category": goal.category,
            "description": goal.description,
            "target_date": goal.target_date.isoformat(),
            "progress": calculate_goal_progress(goal)
        }
        suggestions = suggest_goal_achievement(goal_data)
        return jsonify({"success": True, "suggestions": suggestions})
    return jsonify({"success": False, "message": "Goal not found"})

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
