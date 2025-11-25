#!/usr/bin/env python3
"""
Quick test script to verify the authentication backend is working correctly
"""

import requests
import sys

BASE_URL = "http://localhost:5000"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✓ Health check passed")
            return True
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_login():
    """Test login endpoint"""
    print("\nTesting login endpoint...")
    session = requests.Session()

    try:
        # Test successful login
        response = session.post(
            f"{BASE_URL}/api/login", json={"username": "admin", "password": "admin123"}
        )

        if response.status_code == 200 and response.json().get("success"):
            print("✓ Login successful")

            # Test session check
            response = session.get(f"{BASE_URL}/api/session")
            if response.status_code == 200 and response.json().get("authenticated"):
                print("✓ Session check passed")
            else:
                print("✗ Session check failed")
                return False

            # Test logout
            response = session.post(f"{BASE_URL}/api/logout")
            if response.status_code == 200 and response.json().get("success"):
                print("✓ Logout successful")
            else:
                print("✗ Logout failed")
                return False

            # Verify session is cleared
            response = session.get(f"{BASE_URL}/api/session")
            if response.status_code == 200 and not response.json().get("authenticated"):
                print("✓ Session cleared after logout")
                return True
            else:
                print("✗ Session not cleared properly")
                return False
        else:
            print("✗ Login failed")
            return False

    except Exception as e:
        print(f"✗ Login test error: {e}")
        return False


def test_invalid_login():
    """Test login with invalid credentials"""
    print("\nTesting invalid login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"username": "admin", "password": "wrongpassword"},
        )

        if response.status_code == 401 and not response.json().get("success"):
            print("✓ Invalid login rejected correctly")
            return True
        else:
            print("✗ Invalid login not handled properly")
            return False

    except Exception as e:
        print(f"✗ Invalid login test error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Backend Authentication Test Suite")
    print("=" * 50)
    print(f"\nTesting backend at: {BASE_URL}")
    print()

    tests = [
        ("Health Check", test_health),
        ("Login Flow", test_login),
        ("Invalid Login", test_invalid_login),
    ]

    results = []
    for name, test_func in tests:
        results.append(test_func())

    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for i, (name, _) in enumerate(tests):
        status = "✓ PASSED" if results[i] else "✗ FAILED"
        print(f"{name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please check the backend.")
        sys.exit(1)


if __name__ == "__main__":
    print("Make sure the backend server is running before running this test!")
    print("Start the backend with: python backend/server.py")
    print()
    input("Press Enter to continue...")
    main()


