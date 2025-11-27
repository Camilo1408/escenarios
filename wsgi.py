import os
import sys
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))


from app import create_app

application = create_app()
