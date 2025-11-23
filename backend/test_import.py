#!/usr/bin/env python
"""Test script to verify imports work correctly"""

print("Testing imports...")

try:
    print("1. Importing config...")
    from app.core.config import settings
    print(f"   ✓ Config loaded. KOPIS_API_KEY exists: {bool(settings.kopis_api_key)}")
except Exception as e:
    print(f"   ✗ Config import failed: {e}")
    exit(1)

try:
    print("2. Importing security...")
    from app.core.security import issue_token
    print("   ✓ Security module imported")
except Exception as e:
    print(f"   ✗ Security import failed: {e}")
    exit(1)

try:
    print("3. Importing services...")
    from app.services.kopis import kopis_service
    print("   ✓ KOPIS service imported")
except Exception as e:
    print(f"   ✗ KOPIS service import failed: {e}")
    exit(1)

try:
    print("4. Importing routes...")
    from app.api.routes import api_router
    print("   ✓ API routes imported")
except Exception as e:
    print(f"   ✗ API routes import failed: {e}")
    exit(1)

try:
    print("5. Importing main app...")
    from app.main import app
    print("   ✓ Main app imported successfully!")
except Exception as e:
    print(f"   ✗ Main app import failed: {e}")
    exit(1)

print("\n✅ All imports successful! The refactored backend is ready.")
