#!/usr/bin/env python3
"""
Test script for role-based access control
Tests login with different user roles and verifies JWT tokens
"""
import requests
import json
import jwt

# Configuration
BASE_URL = "http://localhost:5000"
SECRET_KEY = "your-secret-key-here-change-in-production-min-32-chars"  # Should match backend

def test_login(identifier, password, expected_role):
    """Test login and verify role in response"""
    print(f"\n{'='*60}")
    print(f"Testing login: {identifier}")
    print(f"Expected role: {expected_role}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"identifier": identifier, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful")
            print(f"  Username: {data['user']['username']}")
            print(f"  Email: {data['user'].get('email', 'N/A')}")
            print(f"  Role: {data['user']['role']}")
            
            # Decode JWT to verify role is in token
            token = data['access_token']
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"\nJWT Token payload:")
            print(f"  sub (username): {decoded.get('sub')}")
            print(f"  email: {decoded.get('email', 'N/A')}")
            print(f"  role: {decoded.get('role')}")
            
            # Verify role matches expected
            if data['user']['role'] == expected_role:
                print(f"\n✓ PASS: Role matches expected ({expected_role})")
            else:
                print(f"\n✗ FAIL: Role mismatch. Got {data['user']['role']}, expected {expected_role}")
            
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_session(token, expected_role):
    """Test session endpoint with JWT token"""
    print(f"\n{'='*60}")
    print(f"Testing /api/session endpoint")
    print(f"{'='*60}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/session",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['authenticated']:
                print(f"✓ Session valid")
                print(f"  Username: {data['user']['username']}")
                print(f"  Email: {data['user'].get('email', 'N/A')}")
                print(f"  Role: {data['user']['role']}")
                
                if data['user']['role'] == expected_role:
                    print(f"\n✓ PASS: Session role matches ({expected_role})")
                else:
                    print(f"\n✗ FAIL: Session role mismatch")
                return True
            else:
                print(f"✗ Session not authenticated")
                return False
        else:
            print(f"✗ Session check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("ROLE-BASED ACCESS CONTROL TEST SUITE")
    print("="*60)
    print("\nMake sure the backend server is running on http://localhost:5000")
    
    results = []
    
    # Test 1: Premium user (admin email)
    result = test_login("admin@namisense.ai", "admin123", "premium")
    results.append(("Admin (Premium)", result))
    
    # Test 2: Standard user (user email)
    result = test_login("user@namisense.ai", "password123", "standard")
    results.append(("User (Standard)", result))
    
    # Test 3: Standard user (demo email)
    result = test_login("demo@namisense.ai", "demo123", "standard")
    results.append(("Demo (Standard)", result))
    
    # Test 4: Premium user (username)
    result = test_login("namitech", "LT3kzk46e5Q6bqmK", "premium")
    results.append(("Namitech (Premium)", result))
    
    # Test 5: Session endpoint with a token
    print("\n" + "="*60)
    print("Testing session endpoint")
    print("="*60)
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={"identifier": "admin@namisense.ai", "password": "admin123"}
    )
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        result = test_session(token, "premium")
        results.append(("Session Check", result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Role-based access control is working correctly.")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the errors above.")

if __name__ == "__main__":
    main()

