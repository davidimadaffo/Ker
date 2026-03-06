import os
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_name = os.getenv("DB_NAME", "accidents_db")
        self.db_user = os.getenv("DB_USER", "user")
        self.db_pass = os.getenv("DB_PASS", "password")
        self.db_port = os.getenv("DB_PORT", "5432")

    def get_dsn(self):
        """Returns the Data Source Name for the database connection."""
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"