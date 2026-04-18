from fastapi.testclient import TestClient

from input_handler import app


client = TestClient(app)


# =========================
# GET USER MAIL TESTS
# =========================

def test_get_usermail_success(monkeypatch):

    def mock_find_email(username):
        return ("test@gmail.com", "reset123")

    monkeypatch.setattr("input_handler.find_Email", mock_find_email)

    response = client.post(
        "/auth/get_usermail/",
        data={"username": "testuser"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "usrmail": "test@gmail.com",
        "reset_key": "reset123"
    }


def test_get_usermail_too_many_attempts(monkeypatch):

    def mock_find_email(username):
        raise Exception("Too many attempts")

    monkeypatch.setattr("input_handler.find_Email", mock_find_email)

    response = client.post(
        "/auth/get_usermail/",
        data={"username": "testuser"}
    )

    assert response.status_code == 429
    assert "Too many attempts" in response.json()["detail"]


def test_get_usermail_not_found(monkeypatch):

    def mock_find_email(username):
        raise Exception("User not found")

    monkeypatch.setattr("input_handler.find_Email", mock_find_email)

    response = client.post(
        "/auth/get_usermail/",
        data={"username": "wronguser"}
    )

    assert response.status_code == 404


# =========================
# OTP VERIFICATION TESTS
# =========================

def test_otp_verification_success(monkeypatch):

    def mock_verify_otp(mail, reset_key, OTP):
        return ("new_reset_key", "OTP verified successfully")

    monkeypatch.setattr("input_handler.verify_OTP", mock_verify_otp)

    response = client.post(
        "/auth/OTP_verification/",
        data={
            "mail": "test@gmail.com",
            "reset_key": "reset123",
            "OTP": "123456"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "reset_key": "new_reset_key",
        "content": "OTP verified successfully"
    }


def test_otp_verification_invalid(monkeypatch):

    def mock_verify_otp(mail, reset_key, OTP):
        raise Exception("Invalid OTP")

    monkeypatch.setattr("input_handler.verify_OTP", mock_verify_otp)

    response = client.post(
        "/auth/OTP_verification/",
        data={
            "mail": "test@gmail.com",
            "reset_key": "reset123",
            "OTP": "000000"
        }
    )

    assert response.status_code == 401
    assert "Invalid OTP" in response.json()["detail"]


def test_otp_verification_too_many_attempts(monkeypatch):

    def mock_verify_otp(mail, reset_key, OTP):
        raise Exception("Too many attempts")

    monkeypatch.setattr("input_handler.verify_OTP", mock_verify_otp)

    response = client.post(
        "/auth/OTP_verification/",
        data={
            "mail": "test@gmail.com",
            "reset_key": "reset123",
            "OTP": "123456"
        }
    )

    assert response.status_code == 429
