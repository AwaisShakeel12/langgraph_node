# filename: main.py

import os
from fastapi import FastAPI, Query
import uuid
import csv

app = FastAPI()

CSV_FILE = r'E:\Gen_AI2\lang_graph\prec\internship_task\task1_unregisterd_agent\new_with_fastapi\data.csv'




@app.post("/register-user")
def register_user():
    user_id = str(uuid.uuid4())[:8]  
    status = "registered"

    # Check if CSV exists, write header if not
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["user_id", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"user_id": user_id, "status": status})

    return {"message": "User registered", "user_id": user_id, "status": status}


def read_csv():
    users = {}
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users[row['user_id']] = row['status']
    return users


@app.get("/check-status")
def check_status(user_id: str = Query(...)):
    users = read_csv()
    status = users.get(user_id)
    if status:
        return {"user_id": user_id, "status": status}
    return {"message": "User not found"}


@app.get("/confirm_registration")
def confirm_registration(user_id: str = Query(...)):
    users = read_csv()
    if users.get(user_id) == 'registered':
        return {"user_id": user_id, "account_created": True}
    elif user_id in users:
        return {"user_id": user_id, "account_created": False}
    return {"message": "User not found"}
