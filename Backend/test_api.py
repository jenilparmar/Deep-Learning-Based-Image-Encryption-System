"""
Test script to verify the Flask backend is working correctly.
Run this after starting the Flask server.
"""

import requests
import sys

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            return True
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_image_encryption():
    """Test the image encryption endpoint"""
    print("\n🔍 Testing image encryption endpoint...")
    print("Note: You need to have a test image to run this test.")
    print("Skipping automated encryption test. Use the frontend to test image processing.")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Backend API Test Suite")
    print("=" * 60)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Please ensure:")
        print("   1. Flask server is running (python app.py)")
        print("   2. Server is accessible on http://localhost:5000")
        sys.exit(1)
    
    # Test image encryption (manual)
    test_image_encryption()
    
    print("\n" + "=" * 60)
    print("✅ Basic tests completed!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("   1. Open the frontend application")
    print("   2. Upload an image")
    print("   3. Generate or enter an encryption key")
    print("   4. Click 'Process Image' to test encryption/decryption")
