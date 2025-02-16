import logging
import os

from authx import AuthX, AuthXConfig
from dotenv import load_dotenv
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()

load_dotenv()

# Конфигурация почты
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# Конфигурация БД
mongo_uri = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"
mongo_client = AsyncIOMotorClient(mongo_uri)
mongo_db = mongo_client[os.getenv("MONGO_DB")]

# Коллекции БД
users_collection = mongo_db["users"]
verification_codes_collection = mongo_db["verification_codes"]
notes_collection = mongo_db["notes"]
basket_collection = mongo_db["basket"]


# Конфигурация AuthX
config_AuthX = AuthXConfig()
config_AuthX.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config_AuthX.JWT_ACCESS_COOKIE_NAME = "access_token"
config_AuthX.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config_AuthX.JWT_TOKEN_LOCATION = ["cookies"]
config_AuthX.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config_AuthX)

# Конфигурация logging
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
cons_handler = logging.StreamHandler()
cons_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("endpoints.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
cons_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(cons_handler)
logger.addHandler(file_handler)

# Ключ для смены роли
KEY_ROLE = os.getenv("KEY_ROLE")
