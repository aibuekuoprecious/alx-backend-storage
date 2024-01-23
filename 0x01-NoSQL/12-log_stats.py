#!/usr/bin/env python3
""" MongoDB Operations with Python using pymongo """
from pymongo import MongoClient

# Step 1: Connect to MongoDB
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client.logs
collection = db.nginx

# Step 2: Count Total Logs
total_logs = collection.count_documents({})

# Step 3: Count by HTTP Methods
methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
method_counts = {method: collection.count_documents(
    {"method": method}) for method in methods}

# Step 4: Count Specific Logs
status_check_count = collection.count_documents(
    {"method": "GET", "path": "/status"})

# Print the results
print(f"{total_logs} logs")
print("Methods:")
for method, count in method_counts.items():
    print(f"\tmethod {method}: {count}")
print(f"{status_check_count} status check")
