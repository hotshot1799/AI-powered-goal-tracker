from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Modify connect_args based on environment
if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    connect_args = {
        "ssl": ssl_context,
        "server_settings": {"jit": "off"}  # Disable JIT for compatibility
    }
else:
    connect_args = {}

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args=connect_args
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
