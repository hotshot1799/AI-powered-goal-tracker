from typing import Optional
import logging

def safe_int_conversion(value: Any) -> Optional[int]:
    """Safely convert a value to integer."""
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError) as e:
        logging.error(f"Error converting value to int: {value}, Error: {str(e)}")
        return None

def validate_user_session(session_id: Any) -> Optional[int]:
    """Validate and convert session user_id to integer."""
    user_id = safe_int_conversion(session_id)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user_id
