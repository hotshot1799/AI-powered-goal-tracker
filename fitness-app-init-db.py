from app import app, db
from models import User, Goal

with app.app_context():
    db.create_all()
    print("Database tables created.")
