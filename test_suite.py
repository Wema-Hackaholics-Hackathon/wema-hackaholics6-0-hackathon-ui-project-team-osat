import requests
import json
import uuid
import base64
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo  # For timezone-aware datetime
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
import os
import redis

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/auth"
RESULTS_FILE = "test_results.json"
TEST_EMAIL = f"test_{str(uuid.uuid4())[:8]}@test.com"
PRIVATE_KEY_PATH = "private_key.pem"
PUBLIC_KEY_PATH = "public_key.pem"
REDIS_HOST = "localhost"  # Update with your Redis host
REDIS_PORT = 6379        # Update with your Redis port
REDIS_DB = 0             # Update with your Redis DB

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Initialize results storage
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, 'w') as f:
        json.dump({"tests": []}, f, indent=2)

def load_results():
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def save_results(test_result):
    results = load_results()
    results["tests"].append(test_result)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def generate_key_pair():
    """Generate ECDSA key pair and save to files."""
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key()

    # Save private key
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save public key
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    # Read public key PEM
    with open(PUBLIC_KEY_PATH, "r") as f:
        public_pem = f.read()
    return public_pem

def sign_challenge(challenge):
    """Sign a challenge using the private key."""
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    signature = private_key.sign(challenge.encode(), ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode()

def get_otp_from_redis(user_id, email):
    """Fetch OTP from Redis."""
    try:
        otp = redis_client.get(f"otp:{user_id}:{email}")
        if not otp:
            print(f"No OTP found in Redis for {email}")
            return None
        return otp
    except redis.RedisError as e:
        print(f"Redis error: {str(e)}")
        return None

def test_signup():
    """Test the signup endpoint."""
    correlation_id = str(uuid.uuid4())
    payload = {
        "email": TEST_EMAIL,
        "password": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    result = {
        "test": "signup",
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
        "correlation_id": correlation_id,
        "status_code": response.status_code,
        "response": response.json(),
        "success": response.status_code == 200
    }
    save_results(result)
    return response.json() if response.status_code == 200 else None

def test_verify_email(enroll_token, email):
    """Test the email verification endpoint."""
    correlation_id = str(uuid.uuid4())
    # Fetch OTP from Redis
    otp = get_otp_from_redis(enroll_token, email)
    if not otp:
        print("Failed to retrieve OTP from Redis, skipping email verification.")
        result = {
            "test": "verify_email",
            "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
            "correlation_id": correlation_id,
            "status_code": 500,
            "response": {"message": "Failed to retrieve OTP from Redis"},
            "success": False
        }
        save_results(result)
        return False

    payload = {
        "email": email,
        "otp": otp
    }
    response = requests.post(f"{BASE_URL}/verify-email", json=payload)
    result = {
        "test": "verify_email",
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
        "correlation_id": correlation_id,
        "status_code": response.status_code,
        "response": response.json(),
        "success": response.status_code == 200
    }
    save_results(result)
    return response.status_code == 200

def test_register_device():
    """Test the device registration endpoint."""
    correlation_id = str(uuid.uuid4())
    public_pem = generate_key_pair()
    payload = {
        "email": TEST_EMAIL,
        "public_jwk": {"pem": public_pem},
        "browser_fp_hash": str(uuid.uuid4()),
        "first_seen_ip": "127.0.0.1"
    }
    response = requests.post(f"{BASE_URL}/register-device", json=payload)
    result = {
        "test": "register_device",
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
        "correlation_id": correlation_id,
        "status_code": response.status_code,
        "response": response.json(),
        "success": response.status_code == 200
    }
    save_results(result)
    return response.json() if response.status_code == 200 else None

def test_login(device_id):
    """Test the login endpoint."""
    correlation_id = str(uuid.uuid4())
    challenge = str(uuid.uuid4())
    challenge_b64 = base64.b64encode(challenge.encode()).decode()
    signature_b64 = sign_challenge(challenge)
    payload = {
        "email": TEST_EMAIL,
        "device_id": device_id,
        "challenge_b64": challenge_b64,
        "signature_b64": signature_b64,
        "browser_fp_hash": str(uuid.uuid4()),
        "posture": "secure",
        "rtt_ms": random.randint(10, 100),
        "keystroke_vector": [random.randint(50, 150) for _ in range(5)],
        "geo": {
            "country": "NG",
            "city": "Lagos",
            "lat": 6.5244,
            "lon": 3.3792
        }
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)
    result = {
        "test": "login",
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
        "correlation_id": correlation_id,
        "status_code": response.status_code,
        "response": response.json(),
        "success": response.status_code == 200
    }
    save_results(result)
    return response.json() if response.status_code == 200 else None

def run_tests():
    """Run all tests in sequence."""
    print("Starting test suite...")

    # Test signup
    signup_result = test_signup()
    if not signup_result:
        print("Signup failed, aborting.")
        return

    # Test email verification
    if not test_verify_email(signup_result["enroll_token"], TEST_EMAIL):
        print("Email verification failed, proceeding with caution.")
        return

    # Test device registration
    device_result = test_register_device()
    if not device_result:
        print("Device registration failed, aborting.")
        return

    # Test login
    login_result = test_login(device_result["device_id"])
    if login_result:
        print("Login successful!")
    else:
        print("Login failed.")

if __name__ == "__main__":
    run_tests()