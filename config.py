import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUMMARY_TIME = os.getenv("SUMMARY_TIME", "21:00")
TIMEZONE = os.getenv("TIMEZONE", "UTC")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

# Speech-to-Text language (e.g., "en-US", "he-IL", "es-ES")
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "en-US")

# Todoist integration (optional)
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
TODOIST_PROJECT_NAME = os.getenv("TODOIST_PROJECT_NAME", "Brain Dump")

# Categories configuration
# Format: "Category1:emoji1,Category2:emoji2,..."
# Example: "Career:💼,Health:🏥,Fitness:💪"
DEFAULT_CATEGORIES = "Career:💼,Health:🏥,Fitness:💪,Relationships:👥,Finance:💰,Learning:📚,Projects:🔧,Shopping:🛒,Home:🏠"
_categories_str = os.getenv("CATEGORIES", DEFAULT_CATEGORIES)

# Parse categories from string
CATEGORIES: list[str] = []
CATEGORY_EMOJIS: dict[str, str] = {}

for item in _categories_str.split(","):
    if ":" in item:
        name, emoji = item.split(":", 1)
        name = name.strip()
        emoji = emoji.strip()
        CATEGORIES.append(name)
        CATEGORY_EMOJIS[name] = emoji
