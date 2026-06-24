import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MUMBAI_WARDS = [
    {"ward": "A",   "name": "Colaba",         "lat": 18.9067, "lng": 72.8147},
    {"ward": "B",   "name": "Mandvi",          "lat": 18.9490, "lng": 72.8360},
    {"ward": "C",   "name": "Girgaon",         "lat": 18.9600, "lng": 72.8200},
    {"ward": "D",   "name": "Malabar Hill",    "lat": 18.9560, "lng": 72.7960},
    {"ward": "E",   "name": "Byculla",         "lat": 18.9760, "lng": 72.8360},
    {"ward": "FN",  "name": "Sion",            "lat": 19.0390, "lng": 72.8620},
    {"ward": "FS",  "name": "Mahim",           "lat": 19.0400, "lng": 72.8400},
    {"ward": "GN",  "name": "Dharavi",         "lat": 19.0400, "lng": 72.8557},
    {"ward": "GS",  "name": "Dadar",           "lat": 19.0180, "lng": 72.8440},
    {"ward": "HE",  "name": "Santacruz East",  "lat": 19.0820, "lng": 72.8510},
    {"ward": "HW",  "name": "Santacruz West",  "lat": 19.0822, "lng": 72.8355},
    {"ward": "KE",  "name": "Kurla",           "lat": 19.0726, "lng": 72.8797},
    {"ward": "KW",  "name": "Andheri West",    "lat": 19.1362, "lng": 72.8296},
    {"ward": "L",   "name": "Kurla East",      "lat": 19.0596, "lng": 72.8900},
    {"ward": "ME",  "name": "Govandi",         "lat": 19.0490, "lng": 72.9130},
    {"ward": "MW",  "name": "Chembur",         "lat": 19.0620, "lng": 72.8990},
    {"ward": "N",   "name": "Ghatkopar",       "lat": 19.0860, "lng": 72.9081},
    {"ward": "PN",  "name": "Goregaon",        "lat": 19.1663, "lng": 72.8526},
    {"ward": "PS",  "name": "Borivali South",  "lat": 19.2320, "lng": 72.8566},
    {"ward": "RC",  "name": "Dahisar",         "lat": 19.2520, "lng": 72.8570},
    {"ward": "RN",  "name": "Borivali North",  "lat": 19.2403, "lng": 72.8530},
    {"ward": "RS",  "name": "Kandivali",       "lat": 19.2094, "lng": 72.8526},
    {"ward": "S",   "name": "Bandra",          "lat": 19.0596, "lng": 72.8295},
    {"ward": "T",   "name": "Mulund",          "lat": 19.1726, "lng": 72.9570},
]

SEARCH_RADIUS_KM = 1.5

FOOD_AMENITIES = [
    "restaurant", "cafe", "fast_food", "bar",
    "bakery", "food_court", "ice_cream", "juice_bar",
    "biryani", "dhaba",
]