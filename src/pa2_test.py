import json
from threading import Thread
from time import sleep
import unittest

from app import app
import requests

# NOTE: Make sure you run 'pip3 install requests' in your virtualenv

# URL pointing to your local dev host
LOCAL_URL = "http://localhost:5000"

# Sample testing data
SAMPLE_USER = {"name": "Cornell AppDev", "username": "cornellappdev"}


# Request endpoint generators
def gen_users_path(user_id=None):
    base_path = f"{LOCAL_URL}/api/user"
    return (
        base_path + "s/" if user_id is None else f"{base_path}/{str(user_id)}/"
    )


def gen_send_path():
    return f"{LOCAL_URL}/api/send/"


def unwrap_response(response, body={}):
    try:
        return response.json()
    except Exception as e:
        req = response.request
        raise Exception(
            f"""
            Error encountered on the following request:

            request path: {req.url}
            request method: {req.method}
            request body: {str(body)}
            exception: {str(e)}

            There is an uncaught-exception being thrown in your
            method handler for this route!
            """
        )


class TestRoutes(unittest.TestCase):

    # -- USERS ---------------------------------------------

    def test_get_initial_users(self):
        res = requests.get(gen_users_path())
        body = unwrap_response(res)
        assert body["success"]

    def test_create_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user = body["data"]
        assert body["success"]
        assert user["name"] == SAMPLE_USER["name"]
        assert user["username"] == SAMPLE_USER["username"]
        assert user["balance"] == 0

    def test_get_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user = body["data"]
        res = requests.get(gen_users_path(user["id"]))
        body = unwrap_response(res)
        user = body["data"]
        assert body["success"]
        assert user.get("id") is not None
        assert user["name"] == SAMPLE_USER["name"]
        assert user["username"] == SAMPLE_USER["username"]
        assert user["balance"] == 0

    def test_delete_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user_id = body["data"]["id"]
        res = requests.delete(gen_users_path(user_id))
        body = unwrap_response(res)
        assert body["success"]
        res = requests.get(gen_users_path(user_id))
        body = unwrap_response(res)
        assert not body["success"]

    def _create_user_and_assert_balance(self, balance):
        user_with_balance = {**SAMPLE_USER, "balance": balance}
        res1 = requests.post(
            gen_users_path(), data=json.dumps(user_with_balance)
        )
        body = unwrap_response(res1, user_with_balance)
        assert body["success"]
        assert body["data"]["balance"] == balance
        return body["data"]["id"]

    def _get_user_and_assert_balance(self, user_id, balance):
        res = requests.get(gen_users_path(user_id))
        body = unwrap_response(res)
        assert body["success"]
        assert body["data"]["balance"] == balance

    def _send_money(self, user_id1, user_id2, amount, success=True):
        send_body = {
            "sender_id": user_id1,
            "receiver_id": user_id2,
            "amount": amount,
        }
        res = requests.post(gen_send_path(), data=json.dumps(send_body))
        body = unwrap_response(res, send_body)
        assert body["success"] == success
        if success:
            assert body["data"]["sender_id"] == user_id1
            assert body["data"]["receiver_id"] == user_id2
            assert body["data"]["amount"] == amount

    def test_send_money(self):
        user_id1 = self._create_user_and_assert_balance(10)
        user_id2 = self._create_user_and_assert_balance(10)
        self._send_money(user_id1, user_id2, 6)
        self._get_user_and_assert_balance(user_id1, 4)
        self._get_user_and_assert_balance(user_id2, 16)
        # cannot overdraw user1's balance
        self._send_money(user_id1, user_id2, 6, success=False)
        # balances remain the same
        self._get_user_and_assert_balance(user_id1, 4)
        self._get_user_and_assert_balance(user_id2, 16)

    def test_get_invalid_user(self):
        res = requests.get(gen_users_path(1000))
        body = unwrap_response(res)
        assert not body["success"]
        assert body["error"]

    def test_delete_invalid_user(self):
        res = requests.delete(gen_users_path(1000))
        body = unwrap_response(res)
        assert not body["success"]
        assert body["error"]

    def test_user_id_increments(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res, SAMPLE_USER)
        user_id1 = body["data"]["id"]
        res2 = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        body = unwrap_response(res2, SAMPLE_USER)
        user_id2 = body["data"]["id"]
        assert user_id1 + 1 == user_id2


def run_tests():
    sleep(1.5)
    unittest.main()


if __name__ == "__main__":
    thread = Thread(target=run_tests)
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)