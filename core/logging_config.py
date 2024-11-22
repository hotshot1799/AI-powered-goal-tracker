import logging
from datetime import datetime
from pathlib import Path
from app.core.config import settings

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    log_filename = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    # Suppress noisy logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting application in {settings.ENVIRONMENT} mode")
    
    return logger
