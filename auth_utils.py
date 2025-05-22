import pymongo
import os
from dotenv import load_dotenv
import hashlib

# Load .env variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI)
db = client["multi_disease_app"]
users_collection = db["users"]

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# Signup logic
def register_user(name, email, doctor_id, password):
    if users_collection.find_one({"email": email}):
        return False, "Email already registered"
    
    hashed_pw = hash_password(password)
    users_collection.insert_one({
        "name": name,
        "email": email,
        "doctor_id": doctor_id,
        "password": hashed_pw
    })
    return True, "Signup successful"

# Login logic
def login_user(email, password):
    user = users_collection.find_one({"email": email})
    if not user:
        return False, "User not found"
    if not verify_password(password, user["password"]):
        return False, "Incorrect password"
    return True, user
