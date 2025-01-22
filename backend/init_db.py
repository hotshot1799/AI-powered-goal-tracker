import asyncio
from sqlalchemy import text
from database import engine, Base
from models import User, Goal, ProgressUpdate

async def init_db():
    """Initialize the database with required tables"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            
            # Verify tables were created
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
            tables = result.fetchall()
            print("Created tables:", [table[0] for table in tables])
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())