import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUMMARY_TIME = os.getenv("SUMMARY_TIME", "21:00")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jerusalem")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

# Todoist integration (optional)
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
TODOIST_PROJECT_NAME = os.getenv("TODOIST_PROJECT_NAME", "Brain Dump")

CATEGORIES = ["Career", "Health", "Fitness", "Relationships", "Finance", "Learning", "Projects"]
CATEGORY_EMOJIS = {
    "Career": "💼",
    "Health": "🏥",
    "Fitness": "💪",
    "Relationships": "👥",
    "Finance": "💰",
    "Learning": "📚",
    "Projects": "🔧",
}
