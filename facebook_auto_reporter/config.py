import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Facebook Credentials
    FACEBOOK_USERNAME = os.getenv('FACEBOOK_USERNAME')
    FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Application Settings
    HEADLESS_MODE = False
    MAX_REPORTS_PER_SESSION = 5
    DELAY_BETWEEN_REPORTS = 15
    LOG_LEVEL = "INFO"
    LOG_FILE = "./logs/app.log"
    
    # AI Settings
    CONFIDENCE_THRESHOLD = 80.0
    
    # Report Categories
    REPORT_CATEGORIES = [
        "Impersonation",
        "Fake Profile", 
        "Harassment",
        "Hate Speech",
        "Nudity or Sexual Content",
        "Violence",
        "Self-Injury",
        "Spam",
        "Fraud or Scam",
        "Underage"
    ]
    
    # Chrome Settings
    CHROME_PROFILE_PATH = os.getenv('CHROME_PROFILE_PATH', None)
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"