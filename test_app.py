#!/usr/bin/env python3
"""
Comprehensive test script for Smart Expense Tracker
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.append('backend')

def test_backend_import():
    """Test if backend imports successfully"""
    try:
        import server
        print("✅ Backend imports successfully")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation and basic functionality"""
    try:
        from server import app
        from flask.testing import FlaskClient
        
        client = FlaskClient(app)
        
        # Test health endpoint
        response = client.get('/api/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test test endpoint
        response = client.get('/api/test')
        if response.status_code == 200:
            print("✅ Test endpoint working")
        else:
            print(f"❌ Test endpoint failed: {response.status_code}")
            return False
        
        # Test expenses endpoint
        response = client.get('/api/expenses')
        if response.status_code == 200:
            data = response.json
            print(f"✅ Expenses endpoint working ({len(data['data'])} expenses)")
        else:
            print(f"❌ Expenses endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_ai_functionality():
    """Test AI functionality (with fallbacks)"""
    try:
        from server import app
        from flask.testing import FlaskClient
        
        client = FlaskClient(app)
        
        # Test categorization
        response = client.get('/api/expenses/categorize?expense_name=Coffee&amount=150')
        if response.status_code == 200:
            data = response.json
            if data.get('success') and data.get('suggested_category'):
                print(f"✅ Categorization working (suggested: {data['suggested_category']})")
            else:
                print("❌ Categorization failed")
                return False
        else:
            print(f"❌ Categorization endpoint failed: {response.status_code}")
            return False
        
        # Test AI analysis
        test_data = {
            'expenses': [
                {'name': 'Coffee', 'amount': 150, 'category': 'Food', 'date': '2025-01-10'},
                {'name': 'Uber', 'amount': 300, 'category': 'Transportation', 'date': '2025-01-10'}
            ]
        }
        response = client.post('/api/ai/comprehensive-analysis', json=test_data)
        if response.status_code == 200:
            data = response.json
            if data.get('success'):
                print("✅ AI analysis working")
            else:
                print("❌ AI analysis failed")
                return False
        else:
            print(f"❌ AI analysis endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ AI functionality test failed: {e}")
        return False

def test_frontend_files():
    """Test if frontend files exist and are accessible"""
    try:
        frontend_dir = Path('frontend/public')
        index_file = frontend_dir / 'index.html'
        
        if index_file.exists():
            print("✅ Frontend files exist")
            
            # Check if HTML contains expected content
            content = index_file.read_text()
            if 'Smart Expense Tracker' in content and 'API_BASE_URL' in content:
                print("✅ Frontend HTML looks correct")
            else:
                print("❌ Frontend HTML missing expected content")
                return False
        else:
            print("❌ Frontend files not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_vercel_config():
    """Test Vercel configuration"""
    try:
        vercel_file = Path('vercel.json')
        if vercel_file.exists():
            config = json.loads(vercel_file.read_text())
            if 'builds' in config and 'routes' in config:
                print("✅ Vercel configuration looks correct")
            else:
                print("❌ Vercel configuration missing required fields")
                return False
        else:
            print("❌ Vercel configuration file not found")
            return False
        
        # Check API entry point
        api_file = Path('api/index.py')
        if api_file.exists():
            print("✅ API entry point exists")
        else:
            print("❌ API entry point not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Vercel config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Smart Expense Tracker Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Import", test_backend_import),
        ("Flask App", test_flask_app),
        ("AI Functionality", test_ai_functionality),
        ("Frontend Files", test_frontend_files),
        ("Vercel Config", test_vercel_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Set GOOGLE_API_KEY environment variable in Vercel")
        print("2. Deploy to Vercel: vercel --prod")
        print("3. Test the deployed app")
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)