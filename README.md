# 🎯 AI-Powered Goal Tracker

> An intelligent goal tracking application that leverages AI to provide personalized suggestions and help users achieve their goals more effectively.

## ✨ Features

### 🔐 **Core Features**
- **User Authentication**
  - Secure registration system
  - Email verification
  - JWT-based authentication
  - Password reset functionality

### 📊 **Goal Management**
- **Create & Track Goals**
  - Multiple goal categories
  - Progress tracking
  - Timeline management
  - Visual progress indicators

### 🤖 **AI Integration**
- **Smart Suggestions**
  - Personalized recommendations
  - Progress-based insights
  - Category-specific advice
  - Goal prioritization algorithms

### 📱 **User Interface**
- **Modern Dashboard**
  - Responsive design
  - Real-time updates
  - Interactive progress charts
  - Mobile-friendly layout

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async database ORM
- **PostgreSQL** - Primary database
- **Groq API** - AI integration with Llama model

### Frontend
- **React.js** - UI framework
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **React Router** - Navigation

## 🚀 Getting Started

### Prerequisites
```bash
# Required software
Python 3.8+
Node.js 14+
PostgreSQL
Groq API key
```

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/hotshot1799-ai-powered-goal-tracker.git
cd hotshot1799-ai-powered-goal-tracker
```

2. **Backend Setup**
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Environment Configuration**
```env
# Create .env file in backend directory with:
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
```

4. **Database Initialization**
```bash
python init_db.py
```

5. **Frontend Setup**
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install
```

6. **Start the Application**
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` to access the application.
