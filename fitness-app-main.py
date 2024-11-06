from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from models import db, User, Goal, ProgressUpdate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db with the app
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # You'll need to create this template

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
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
        return jsonify({"success": True, "user_id": user.id})
    return jsonify({"success": False})

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
                "created_at": goal.created_at.isoformat()
            } for goal in user.goals
        ]
        return jsonify(goals)
    return jsonify([])

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

@app.route('/analyze/<int:user_id>', methods=['GET'])
def analyze(user_id):
    user = User.query.get(user_id)
    if user:
        goals = [
            {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date.isoformat(),
                "created_at": goal.created_at.isoformat()
            } for goal in user.goals
        ]
        insights = analyze_data(goals)
        return jsonify(insights)
    return jsonify({"success": False, "message": "User not found"})

@app.route('/suggest/<int:goal_id>', methods=['GET'])
def suggest(goal_id):
    goal = Goal.query.get(goal_id)
    if goal:
        suggestions = suggest_goal_achievement({
            "category": goal.category,
            "description": goal.description,
            "target_date": goal.target_date.isoformat()
        })
        return jsonify({"success": True, "suggestions": suggestions})
    return jsonify({"success": False, "message": "Goal not found"})

if __name__ == '__main__':
    app.run(debug=True)
