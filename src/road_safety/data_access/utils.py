import psycopg2
from ..config import Settings
import os
from typing import Optional

import psycopg2
from psycopg2.extensions import connection

from road_safety.bootstrap import load_dotenv_if_present


def establish_connection() -> Optional[connection]:
    load_dotenv_if_present()

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5888"))
    user = os.getenv("DB_USER", "user")
    password = os.getenv("DB_PASS", "password")
    dbname = os.getenv("DB_NAME", "accidents_db")

    try:
        return psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
        )
    except Exception as e:
        print(f"Connection error: {e}")
        return None