"""
Simple tests for QR Code Generator API
"""

import requests
import base64
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    print("✅ Health check passed")

def test_generate_qr():
    """Test QR code generation"""
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={"text": "https://example.com", "size": 300}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'qr_code' in data
    assert data['text'] == "https://example.com"
    assert data['size'] == 300
    
    # Verify base64 is valid
    try:
        base64.b64decode(data['qr_code'])
        print("✅ QR generation passed")
    except Exception as e:
        print(f"❌ Invalid base64: {e}")
        raise

def test_generate_qr_image():
    """Test QR code image endpoint"""
    response = requests.post(
        f"{BASE_URL}/api/generate/image",
        json={"text": "Hello World", "size": 400}
    )
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    assert len(response.content) > 0
    print("✅ QR image endpoint passed")

def test_validation():
    """Test input validation"""
    # Missing text
    response = requests.post(f"{BASE_URL}/api/generate", json={})
    assert response.status_code == 400
    print("✅ Validation passed")

if __name__ == '__main__':
    print("Running tests...")
    try:
        test_health()
        test_generate_qr()
        test_generate_qr_image()
        test_validation()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
