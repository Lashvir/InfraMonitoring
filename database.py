import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL=os.environ["DATABASE_URL"]

def get_connection():
    return psycopg.connect(DATABASE_URL)
