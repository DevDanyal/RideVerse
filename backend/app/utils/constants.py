"""Application constants."""

# ──────────────────────────────────────────────
# API Constants
# ──────────────────────────────────────────────
API_V1_PREFIX = "/api/v1"
APP_NAME = "RideVerse"
APP_VERSION = "0.1.0"
DEBUG = False

# ──────────────────────────────────────────────
# Authentication
# ──────────────────────────────────────────────
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"

# ──────────────────────────────────────────────
# Rate Limiting
# ──────────────────────────────────────────────
DEFAULT_RATE_LIMIT = 100
RATE_LIMIT_WINDOW_SECONDS = 60

# ──────────────────────────────────────────────
# Player
# ──────────────────────────────────────────────
MAX_USERNAME_LENGTH = 32
MIN_USERNAME_LENGTH = 3
MAX_PLAYERS_PER_IP = 3
DEFAULT_PLAYER_LEVEL = 1
MAX_PLAYER_LEVEL = 100

# ──────────────────────────────────────────────
# Vehicles
# ──────────────────────────────────────────────
MAX_VEHICLES_PER_PLAYER = 10
VEHICLE_TYPES = ["bike", "car", "truck", "boat", "aircraft"]
VEHICLE_CONDITION_MIN = 0
VEHICLE_CONDITION_MAX = 100
VEHICLE_FUEL_MIN = 0
VEHICLE_FUEL_MAX = 100

# ──────────────────────────────────────────────
# Economy
# ──────────────────────────────────────────────
DEFAULT_CURRENCY = "RVN"
CURRENCY_SYMBOL = "$"
MAX_WALLET_BALANCE = 999_999_999
MAX_BANK_BALANCE = 99_999_999_999
DAILY_REWARD_AMOUNT = 1000
DAILY_REWARD_STREAK_MULTIPLIER = 1.5
MAX_TRANSFER_AMOUNT = 10_000_000

# ──────────────────────────────────────────────
# Inventory
# ──────────────────────────────────────────────
MAX_INVENTORY_SLOTS = 50
MAX_STACK_SIZE = 999
ITEM_RARITY = ["common", "uncommon", "rare", "epic", "legendary"]

# ──────────────────────────────────────────────
# Missions
# ──────────────────────────────────────────────
MAX_ACTIVE_MISSIONS = 5
MISSION_TYPES = ["story", "side", "daily", "weekly", "event", "repeatable"]

# ──────────────────────────────────────────────
# Clubs
# ──────────────────────────────────────────────
MAX_CLUB_MEMBERS = 50
MIN_CLUB_NAME_LENGTH = 3
MAX_CLUB_NAME_LENGTH = 32

# ──────────────────────────────────────────────
# Chat
# ──────────────────────────────────────────────
MAX_MESSAGE_LENGTH = 500
CHAT_COOLDOWN_SECONDS = 1

# ──────────────────────────────────────────────
# Marketplace
# ──────────────────────────────────────────────
MARKETPLACE_LISTING_FEE = 100
MARKETPLACE_TAX_RATE = 0.05
MAX_ACTIVE_LISTINGS = 20

# ──────────────────────────────────────────────
# Police / Crime
# ──────────────────────────────────────────────
WANTED_LEVELS = [0, 1, 2, 3, 4, 5]
BASE_FINE_AMOUNT = 500
FINE_MULTIPLIER_PER_LEVEL = 2.0
SURRENDER_COOLDOWN_SECONDS = 300

# ──────────────────────────────────────────────
# Weather
# ──────────────────────────────────────────────
WEATHER_TYPES = ["clear", "cloudy", "rainy", "stormy", "foggy", "snowy"]
WEATHER_CHANGE_INTERVAL_MINUTES = 30

# ──────────────────────────────────────────────
# WebSocket
# ──────────────────────────────────────────────
WS_HEARTBEAT_INTERVAL = 30
WS_MAX_CONNECTIONS_PER_PLAYER = 2
WS_MESSAGE_MAX_SIZE = 4096
