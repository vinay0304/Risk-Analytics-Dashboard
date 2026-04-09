import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pymongo import MongoClient
import json
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables if .env exists, though using defaults here for the generator
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "risk_analytics")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "transactions")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "risk_data.db")

NUM_USERS = 500
NUM_TRANSACTIONS = 5000

RULES = [
    {"rule_id": "R001", "rule_name": "Velocity Check", "description": "High volume of transactions in short timeframe", "weight": 80},
    {"rule_id": "R002", "rule_name": "Volume Spike", "description": "Unusually large transaction amount", "weight": 70},
    {"rule_id": "R003", "rule_name": "Location Anomaly", "description": "Transaction from atypical geolocation", "weight": 60},
    {"rule_id": "R004", "rule_name": "New Device", "description": "Login or transaction from unrecognized device", "weight": 40},
    {"rule_id": "R005", "rule_name": "IP Blacklist", "description": "IP address matched known risky IPs", "weight": 95},
]

def generate_sqlite_data():
    """Generates user and rule reference data in SQLite."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            account_type TEXT,
            registration_date DATE,
            risk_tier TEXT
        )
    ''')
    
    # Create Rules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_rules (
            rule_id TEXT PRIMARY KEY,
            rule_name TEXT,
            description TEXT,
            weight INTEGER
        )
    ''')
    
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM risk_rules")
    
    users = []
    for i in range(NUM_USERS):
        user_id = f"U{str(i).zfill(5)}"
        acc_type = random.choice(['Consumer', 'Business', 'Platform'])
        reg_date = (datetime.now() - timedelta(days=random.randint(30, 1000))).date()
        risk_tier = random.choices(['Low', 'Medium', 'High'], weights=[80, 15, 5])[0]
        users.append((user_id, acc_type, reg_date, risk_tier))
        
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users)
    
    rules_data = [(r['rule_id'], r['rule_name'], r['description'], r['weight']) for r in RULES]
    cursor.executemany("INSERT INTO risk_rules VALUES (?, ?, ?, ?)", rules_data)
    
    conn.commit()
    conn.close()
    logger.info(f"Generated {NUM_USERS} users and {len(RULES)} rules in SQLite: {SQLITE_DB_PATH}")
    return [u[0] for u in users]

def generate_mongodb_data(user_ids):
    """Generates transaction logs in MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # trigger connection
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB. Detailed error: {e}")
        logger.warning("Generating mock data into JSON instead for fallback.")
        db = None
        collection = None

    transactions = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(NUM_TRANSACTIONS):
        tx_id = f"TXN{str(i).zfill(6)}"
        user_id = random.choice(user_ids)
        amount = round(random.lognormvariate(4, 1.5), 2)
        
        # Determine timestamp
        random_seconds = random.randint(0, int((end_date - start_date).total_seconds()))
        ts = start_date + timedelta(seconds=random_seconds)
        
        # Risk evaluation
        is_risky = random.random() < 0.15
        
        rule_triggered = None
        risk_score = random.randint(0, 30)
        status = 'Completed'
        
        if is_risky:
            rule = random.choice(RULES)
            rule_triggered = rule['rule_id']
            risk_score = min(100, rule['weight'] + random.randint(-10, 20))
            if risk_score > 80:
                status = 'Blocked'
            elif risk_score > 60:
                status = 'Pending Review'
        
        doc = {
            "transaction_id": tx_id,
            "user_id": user_id,
            "amount": amount,
            "currency": "USD",
            "timestamp": ts,
            "risk_score": risk_score,
            "is_flagged": is_risky,
            "rule_triggered": rule_triggered,
            "status": status,
            "device_os": random.choice(["iOS", "Android", "Windows", "MacOS"]),
            "ip_country": random.choices(["US", "CA", "GB", "RU", "NG"], weights=[70, 10, 10, 5, 5])[0]
        }
        transactions.append(doc)

    if collection is not None:
        collection.delete_many({})
        collection.insert_many(transactions)
        logger.info(f"Generated {NUM_TRANSACTIONS} transactions in MongoDB collection: {MONGO_COLLECTION_NAME}")
    else:
        # Fallback to local JSON if MongoDB is not accessible
        with open('mock_mongo_transactions.json', 'w') as f:
            # converting datetime to string for json serialization
            json_tx = []
            for tx in transactions:
                tx_copy = dict(tx)
                tx_copy['timestamp'] = tx_copy['timestamp'].isoformat()
                json_tx.append(tx_copy)
            json.dump(json_tx, f)
        logger.info(f"Saved {NUM_TRANSACTIONS} falling back transactions in local JSON file: mock_mongo_transactions.json")


if __name__ == "__main__":
    logger.info("Starting data generation...")
    u_ids = generate_sqlite_data()
    generate_mongodb_data(u_ids)
    logger.info("Data generation complete.")
