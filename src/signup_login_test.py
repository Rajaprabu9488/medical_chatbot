from fastapi.testclient import TestClient
from input_handler import app

client = TestClient(app)

# =========================
# SIGNUP TESTS
# =========================

def test_signup_success(monkeypatch):
    def mock_update_user(username, email, password):
        return "user123"

    monkeypatch.setattr("input_handler.upadate_user", mock_update_user)

    response = client.post("/auth/signup/", data={
        "username": "test",
        "email": "test@gmail.com",
        "password": "123"
    })

    assert response.status_code == 200
    assert response.json() == {"identity": "user123", "usermail": "test@gmail.com"}


def test_signup_conflict(monkeypatch):
    def mock_update_user(username, email, password):
        raise Exception("User exists")

    monkeypatch.setattr("input_handler.upadate_user", mock_update_user)

    response = client.post("/auth/signup/", data={
        "username": "test",
        "email": "test@gmail.com",
        "password": "123"
    })

    assert response.status_code == 409


# =========================
# SIGNUP VERIFICATION
# =========================

def test_signup_verification_success(monkeypatch):
    def mock_signup_verified(userid, OTP):
        return {"msg": "verified"}

    monkeypatch.setattr("input_handler.signup_verified", mock_signup_verified)

    response = client.post("/auth/signup_verification/", data={
        "userid": "123",
        "mail": "test@gmail.com",
        "OTP": "111"
    })

    assert response.status_code == 200


def test_signup_verification_timeout(monkeypatch):
    def mock_signup_verified(userid, OTP):
        raise Exception("Request Timeout")

    monkeypatch.setattr("input_handler.signup_verified", mock_signup_verified)

    response = client.post("/auth/signup_verification/", data={
        "userid": "123",
        "mail": "test@gmail.com",
        "OTP": "111"
    })

    assert response.status_code == 401


def test_signup_verification_too_many(monkeypatch):
    def mock_signup_verified(userid, OTP):
        raise Exception("Too many attempts")

    monkeypatch.setattr("input_handler.signup_verified", mock_signup_verified)

    response = client.post("/auth/signup_verification/", data={
        "userid": "123",
        "mail": "test@gmail.com",
        "OTP": "111"
    })

    assert response.status_code == 429


# =========================
# LOGIN TESTS
# =========================

def test_login_success(monkeypatch):
    def mock_validate_user(username, password):
        return ("id123", "mail@gmail.com", "session123")

    def mock_update_session(session):
        return None

    monkeypatch.setattr("input_handler.validate_user", mock_validate_user)
    monkeypatch.setattr("input_handler.update_session", mock_update_session)

    response = client.post("/auth/login/", data={
        "username": "test",
        "password": "123"
    })

    assert response.status_code == 200
    assert response.json()["identity"] == "id123"


def test_login_invalid(monkeypatch):
    def mock_validate_user(username, password):
        raise Exception("Invalid")

    monkeypatch.setattr("input_handler.validate_user", mock_validate_user)

    response = client.post("/auth/login/", data={
        "username": "test",
        "password": "wrong"
    })

    assert response.status_code == 401


# =========================
# GET USER MAIL
# =========================

def test_get_usermail_success(monkeypatch):
    def mock_find_email(username):
        return ("mail@gmail.com", "reset123")

    monkeypatch.setattr("input_handler.find_Email", mock_find_email)

    response = client.post("/auth/get_usermail/", data={"username": "test"})

    assert response.status_code == 200


# =========================
# OTP VERIFICATION
# =========================

def test_otp_success(monkeypatch):
    def mock_verify(mail, key, otp):
        return ("newkey", "ok")

    monkeypatch.setattr("input_handler.verify_OTP", mock_verify)

    response = client.post("/auth/OTP_verification/", data={
        "mail": "test@gmail.com",
        "reset_key": "123",
        "OTP": "111"
    })

    assert response.status_code == 200


def test_otp_invalid(monkeypatch):
    def mock_verify(mail, key, otp):
        raise Exception("Invalid")

    monkeypatch.setattr("input_handler.verify_OTP", mock_verify)

    response = client.post("/auth/OTP_verification/", data={
        "mail": "test@gmail.com",
        "reset_key": "123",
        "OTP": "000"
    })

    assert response.status_code == 401