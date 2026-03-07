import psycopg2
from ..config import Settings

def establish_connection():
    """Establishes a connection to the PostgreSQL database."""
    settings = Settings()
    try:
        conn = psycopg2.connect(settings.get_dsn())
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None