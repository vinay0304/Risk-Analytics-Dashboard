import sqlite3
import pandas as pd
import json
import os
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "risk_analytics")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "transactions")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "risk_data.db")

@st.cache_data(ttl=600)
def load_reference_data():
    """Loads users and rules from SQLite"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        users_df = pd.read_sql("SELECT * FROM users", conn)
        rules_df = pd.read_sql("SELECT * FROM risk_rules", conn)
        conn.close()
        return users_df, rules_df
    except Exception as e:
        st.error(f"Error loading SQLite data: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def load_transaction_data():
    """Loads transactions from MongoDB or flat file fallback"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        client.server_info()
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        cursor = collection.find({}, {'_id': 0})
        tx_df = pd.DataFrame(list(cursor))
        if not tx_df.empty and 'timestamp' in tx_df.columns:
            tx_df['timestamp'] = pd.to_datetime(tx_df['timestamp'])
        return tx_df
    except Exception as e:
        # Check for fallback json
        if os.path.exists('mock_mongo_transactions.json'):
            st.warning("MongoDB connection failed. Using fallback JSON file for transactions.")
            with open('mock_mongo_transactions.json', 'r') as f:
                data = json.load(f)
                tx_df = pd.DataFrame(data)
                if not tx_df.empty and 'timestamp' in tx_df.columns:
                    tx_df['timestamp'] = pd.to_datetime(tx_df['timestamp'])
                return tx_df
        st.error(f"Error loading transaction data: {e}")
        return pd.DataFrame()

def get_joined_data():
    """Joins transaction data with user details via Pandas merging"""
    tx_df = load_transaction_data()
    users_df, rules_df = load_reference_data()
    
    if tx_df.empty or users_df.empty:
        return pd.DataFrame()
        
    # Example merging SQL-like relational data with NoSQL documents
    merged_df = pd.merge(tx_df, users_df, on='user_id', how='left')
    if not rules_df.empty:
        merged_df = pd.merge(merged_df, rules_df, left_on='rule_triggered', right_on='rule_id', how='left')
    
    return merged_df
