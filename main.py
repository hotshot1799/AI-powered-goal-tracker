from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from core.config import settings
from api.v1.router import api_router
from database import Base, engine, get_db
from models import User  # Add this import
from models import Goal, ProgressUpdate
from services.ai import AIService  # Add this import
import logging
import os
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the static and templates directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

# Move templates outside the function to make it globally accessible
templates = Jinja2Templates(directory=templates_dir)  # Use templates_dir here

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        same_site="lax",
        https_only=True,
        max_age=1800  # 30 minutes
    )
    
    # Mount static files with specific subdirectories
    app.mount("/static/styles", StaticFiles(directory=os.path.join(static_dir, "styles")), name="styles")
    app.mount("/static/script", StaticFiles(directory=os.path.join(static_dir, "script")), name="scripts")
    
    # Remove duplicate templates initialization
    # templates = Jinja2Templates(directory="templates")  # Remove this line
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse(
            "index.html", 
            {"request": request}
        )
    
    @app.get("/login")
    async def login_page(request: Request):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request}
        )
    
    @app.get("/dashboard")
    async def dashboard_page(request: Request):
        # Check session here if needed
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request}
        )
    
    @app.get("/register")
    async def register(request: Request):
        return templates.TemplateResponse(
            "register.html", 
            {"request": request}
        )
    
    @app.post("/api/v1/auth/login")
    async def login(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')

            user = await db.execute(
                select(User).where(User.username == username)
            )
            user = user.scalar_one_or_none()

            if user and user.verify_password(password):
                # Set session data
                request.session['user_id'] = str(user.id)
                request.session['username'] = user.username
            
                return {
                    "success": True,
                    "user_id": user.id,
                    "username": user.username,
                    "redirect": "/dashboard"
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials"
                )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @app.get("/get_goals/{user_id}")
    async def get_goals(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
        try:
            if str(user_id) != str(request.session.get('user_id')):
                raise HTTPException(status_code=403, detail="Not authorized")

            query = select(Goal).filter(Goal.user_id == user_id)
            result = await db.execute(query)
            goals = result.scalars().all()
            
            return {
                "success": True,
                "goals": [
                    {
                        "id": goal.id,
                        "category": goal.category,
                        "description": goal.description,
                        "target_date": goal.target_date.isoformat(),
                        "created_at": goal.created_at.isoformat(),
                        "progress": 0  # You can implement proper progress calculation
                    } for goal in goals
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching goals: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


    @app.post("/set_goal")
    async def set_goal(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                raise HTTPException(status_code=401, detail="Not authenticated")

            data = await request.json()
        
            goal = Goal(
                user_id=int(user_id),  # Convert string to int
                category=data['category'],
                description=data['description'],
                target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date()
            )
        
            db.add(goal)
            await db.commit()
            await db.refresh(goal)
        
            return {
                "success": True,
                "goal": {
                    "id": goal.id,
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat(),
                    "created_at": goal.created_at.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error creating goal: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @app.get("/get_suggestions/{user_id}")
    async def get_suggestions(
        user_id: int, 
        request: Request,
        db: AsyncSession = Depends(get_db)
    ):
        try:
            if not request.session.get('user_id'):
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # Get user's goals for context
            query = select(Goal).filter(Goal.user_id == user_id)
            result = await db.execute(query)
            goals = result.scalars().all()
            
            ai_service = AIService()
            
            # If no goals yet, get starter suggestions
            if not goals:
                return {
                    "success": True,
                    "suggestions": [
                        "Start by creating a SMART goal - Specific, Measurable, Achievable, Relevant, and Time-bound",
                        "Consider breaking down your future goals into smaller, manageable tasks",
                        "Set up regular check-ins to track your progress"
                    ]
                }

            # Create goals context for AI
            goals_analysis = "\n".join([
                f"Goal {i+1}:"
                f"\nCategory: {goal.category}"
                f"\nDescription: {goal.description}"
                f"\nTarget Date: {goal.target_date}"
                for i, goal in enumerate(goals)
            ])
            
            analysis_prompt = f"""
            Based on these goals:
            {goals_analysis}

            Provide 3 specific, actionable suggestions that:
            1. Address immediate next steps for achieving these goals
            2. Suggest ways to track progress effectively
            3. Offer strategies to overcome potential challenges

            Make each suggestion directly related to the user's goals.
            Format as a numbered list.
            Each suggestion should be specific to the goals mentioned.
            """
            
            try:
                suggestions_text = await ai_service.analyze_data(analysis_prompt)
                suggestions = [
                    s.strip() for s in suggestions_text.split('\n') 
                    if s.strip() and not s.startswith(('1.', '2.', '3.'))
                ][:3]
                
                if len(suggestions) < 3:
                    raise ValueError("Insufficient AI suggestions generated")
            except Exception as ai_error:
                logger.error(f"AI analysis error: {str(ai_error)}")
                # Fallback suggestions based on actual goals
                suggestions = [
                    f"For your {goals[0].category} goal: Break down '{goals[0].description}' into weekly milestones",
                    "Set up a daily tracking system for each of your goals",
                    "Schedule weekly review sessions to assess your progress"
                ]
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except HTTPException as http_error:
            raise http_error
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    @app.get("/goal/{goal_id}")
    async def goal_details_page(
        goal_id: int, 
        request: Request,
        db: AsyncSession = Depends(get_db)
    ):
        try:
        # Check if user is authenticated
            user_id = request.session.get('user_id')
            if not user_id:
                return RedirectResponse(url="/login")

            # Fetch goal data
            goal_query = select(Goal).filter(
                Goal.id == goal_id,
                Goal.user_id == user_id
            )
            result = await db.execute(goal_query)
            goal = result.scalar_one_or_none()

            if not goal:
                raise HTTPException(status_code=404, detail="Goal not found")

            # Fetch progress updates for the goal
            progress_query = select(ProgressUpdate).filter(
                ProgressUpdate.goal_id == goal_id
            ).order_by(ProgressUpdate.created_at.desc())
            progress_result = await db.execute(progress_query)
            progress_updates = progress_result.scalars().all()

            # Get latest progress value
            latest_progress = 0
            if progress_updates:
                latest_progress = progress_updates[0].progress_value

            # Convert goal to dict for template
            goal_data = {
                "id": goal.id,
                "category": goal.category,
                "description": goal.description,
                "target_date": goal.target_date,
                "created_at": goal.created_at,
                "progress": latest_progress
            }

            return templates.TemplateResponse(
                "goal_details.html",
                {
                    "request": request,
                    "goal": goal_data,
                    "progress_updates": [
                        {
                            "text": update.update_text,
                            "progress": update.progress_value,
                            "analysis": update.analysis,
                            "created_at": update.created_at
                        }
                        for update in progress_updates
                    ]
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching goal details: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    # Add or update the progress endpoints
    @app.post("/progress/{goal_id}")
    async def update_progress(
        goal_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db)
    ):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                raise HTTPException(status_code=401, detail="Not authenticated")

            data = await request.json()
            update_text = data.get('update_text')
            if not update_text:
                raise HTTPException(status_code=400, detail="Update text required")

            # Verify goal ownership
            goal = await db.get(Goal, goal_id)
            if not goal or str(goal.user_id) != str(user_id):
                raise HTTPException(status_code=404, detail="Goal not found")

            # Use AI to analyze progress
            ai_service = AIService()
            analysis_prompt = f"""
            Goal: {goal.description}
            Category: {goal.category}
            Progress Update: {update_text}

            Based on this progress update, provide:
            1. A percentage (0-100) indicating goal completion progress
            2. A brief analysis explaining why this percentage was chosen
            
            Respond in JSON format:
            {{
                "percentage": number,
                "analysis": "brief explanation"
            }}
            """

            try:
                ai_response = await ai_service.analyze_data(analysis_prompt)
                ai_data = json.loads(ai_response)
                progress_value = float(ai_data.get('percentage', 0))
                analysis = ai_data.get('analysis', 'Progress analyzed')
                # Ensure progress is between 0 and 100
                progress_value = max(0, min(100, progress_value))
            except Exception as ai_error:
                logger.error(f"AI analysis error: {str(ai_error)}")
                progress_value = 0
                analysis = "Unable to analyze progress"

            # Create progress update
            progress_update = ProgressUpdate(
                goal_id=goal_id,
                update_text=update_text,
                progress_value=progress_value,
                analysis=analysis
            )

            db.add(progress_update)
            await db.commit()
            await db.refresh(progress_update)

            return {
                "success": True,
                "update": {
                    "text": update_text,
                    "progress": progress_value,
                    "analysis": analysis,
                    "created_at": progress_update.created_at.isoformat()
                }
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Progress update error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/progress/{goal_id}")
    async def get_progress_updates(
        goal_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db)
    ):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                raise HTTPException(status_code=401, detail="Not authenticated")

            # Verify goal ownership
            goal = await db.get(Goal, goal_id)
            if not goal or str(goal.user_id) != str(user_id):
                raise HTTPException(status_code=404, detail="Goal not found")

            # Get progress updates
            query = select(ProgressUpdate).filter(
                ProgressUpdate.goal_id == goal_id
            ).order_by(ProgressUpdate.created_at.desc())
            
            result = await db.execute(query)
            updates = result.scalars().all()

            return {
                "success": True,
                "updates": [{
                    "text": update.update_text,
                    "progress": update.progress_value,
                    "analysis": update.analysis,
                    "created_at": update.created_at.isoformat()
                } for update in updates]
            }

        except Exception as e:
            logger.error(f"Error fetching progress updates: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Update the get_goals endpoint to include latest progress
    @app.get("/get_goals/{user_id}")
    async def get_goals(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
        try:
            if str(user_id) != str(request.session.get('user_id')):
                raise HTTPException(status_code=403, detail="Not authorized")

            query = select(Goal).filter(Goal.user_id == user_id)
            result = await db.execute(query)
            goals = result.scalars().all()
            
            goals_with_progress = []
            for goal in goals:
                # Get latest progress update for each goal
                progress_query = select(ProgressUpdate).filter(
                    ProgressUpdate.goal_id == goal.id
                ).order_by(ProgressUpdate.created_at.desc())
                progress_result = await db.execute(progress_query)
                latest_progress = progress_result.scalar_one_or_none()

                goals_with_progress.append({
                    "id": goal.id,
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat(),
                    "created_at": goal.created_at.isoformat(),
                    "progress": latest_progress.progress_value if latest_progress else 0
                })
            
            return {
                "success": True,
                "goals": goals_with_progress
            }
        except Exception as e:
            logger.error(f"Error fetching goals: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/update_goal")
    async def update_goal(request: Request, db: AsyncSession = Depends(get_db)):
        try:
            data = await request.json()
            user_id = request.session.get('user_id')
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Not authenticated")

            goal = await db.get(Goal, data['id'])
            if not goal:
                raise HTTPException(status_code=404, detail="Goal not found")
            
            if str(goal.user_id) != str(user_id):
                raise HTTPException(status_code=403, detail="Not authorized")

            # Update goal fields
            if 'category' in data:
                goal.category = data['category']
            if 'description' in data:
                goal.description = data['description']
            if 'target_date' in data:
                goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()

            await db.commit()
            await db.refresh(goal)
            
            return {
                "success": True,
                "goal": {
                    "id": goal.id,
                    "category": goal.category,
                    "description": goal.description,
                    "target_date": goal.target_date.isoformat(),
                    "created_at": goal.created_at.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error updating goal: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/delete_goal/{goal_id}")
    async def delete_goal(goal_id: int, request: Request, db: AsyncSession = Depends(get_db)):
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                raise HTTPException(status_code=401, detail="Not authenticated")

            goal = await db.get(Goal, goal_id)
            if not goal:
                raise HTTPException(status_code=404, detail="Goal not found")
            
            if str(goal.user_id) != str(user_id):
                raise HTTPException(status_code=403, detail="Not authorized")

            await db.delete(goal)
            await db.commit()
            
            return {
                "success": True,
                "message": "Goal deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting goal: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "api_version": settings.VERSION}

    # Global exception handler
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        logger.error(f"Internal Server Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "message": str(exc)}
        )

    @app.exception_handler(404)
    async def not_found_error_handler(request: Request, exc: Exception):
        logger.error(f"Not Found Error: {str(exc)}")
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found", "path": str(request.url)}
        )
        
    # Include API router with debug logging
    logger.info(f"Mounting API router at {settings.API_V1_STR}")
    app.include_router(
        api_router, 
        prefix=settings.API_V1_STR
    )
    
    @app.on_event("startup")
    async def startup():
        try:
             async with engine.begin() as conn:
                # Drop all tables
                await conn.run_sync(Base.metadata.drop_all)
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables recreated successfully")
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Application shutting down...")
            
    return app

# Create the application instance
app = create_application()
wsgi_app = app

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
