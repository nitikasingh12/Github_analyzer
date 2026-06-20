import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/github_analyzer')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-12345')
    DEBUG = os.getenv('DEBUG', True)
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
