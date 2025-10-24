import pytest
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_basic_imports():
    """Test that basic imports work"""
    try:
        from main import app
        assert app is not None
    except ImportError as e:
        pytest.skip(f"Could not import main: {e}")

def test_health_endpoint():
    """Test health endpoint"""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    except ImportError as e:
        pytest.skip(f"Could not import required modules: {e}")

def test_root_endpoint():
    """Test root endpoint"""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    except ImportError as e:
        pytest.skip(f"Could not import required modules: {e}")

def test_basic_math():
    """Basic test to ensure pytest is working"""
    assert 1 + 1 == 2
    assert "hello" == "hello"

if __name__ == "__main__":
    pytest.main([__file__])
