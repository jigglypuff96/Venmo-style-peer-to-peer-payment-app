import json
from flask import Flask, request
import db
from helper import *

DB = db.DatabaseDriver()

app = Flask(__name__)


def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code
@app.route("/")
@app.route("/api/users/")
def get_all_users():
    return success_response(DB.get_all_users())

@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    name = body["name"]
    username = body["username"]
    balance = int(body.get("balance", 0))
    password = body.get("password", "")
    email = body.get("email", "")
    user_id = DB.insert_user_table(name,username,balance,password,email)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Something went wrong while creating user!")
    return success_response(user, 201)


@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["POST"])
def update_user(user_id):
    body = json.loads(request.data)
    name = body["name"]
    username = body["username"]
    balance = int(body.get("balance", 0))
    password = body.get("password", "")
    email = body.get("email", "")
    DB.update_user_by_id(name,username,balance,password,email)

    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")
    return success_response(user)


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")
    DB.delete_user_by_id(user_id)
    return success_response(user)


@app.route("/api/send/", methods=["POST"])
def create_send():
    body = json.loads(request.data)
    sender_id = int(body["sender_id"])
    receiver_id = int(body["receiver_id"])
    amount = int(body["amount"])
    password = body.get("password", "")

    sender_user = DB.get_user_by_id(sender_id)
    sender_name = sender_user["name"]
    sender_username = sender_user["username"]
    sender_balance = sender_user["balance"]
    sender_password = sender_user["password"]

    if not verify_password(sender_password, password): #password != sender_password:
        return failure_response("Incorrect password!")
    receiver_user = DB.get_user_by_id(receiver_id)
    receiver_name = receiver_user["name"]
    receiver_username = receiver_user["username"]
    receiver_balance = receiver_user["balance"]
    if amount > sender_balance:
        return failure_response("Not enough balance!")

    DB.update_user_by_id(sender_id, sender_name, sender_username, sender_balance-amount)
    DB.update_user_by_id(receiver_id, receiver_name, receiver_username, receiver_balance+amount)

    send = {"sender_id": sender_id, "receiver_id": receiver_id, "amount": amount}
    return success_response(send, 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
