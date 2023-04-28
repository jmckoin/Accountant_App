import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))
