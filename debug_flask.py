#!/usr/bin/env python3
import sys
import traceback

print("Testing Flask app with detailed debugging...")

try:
    print("Importing app_simple...")
    import app_simple
    print("Flask app imported successfully")
except Exception as e:
    print(f"Error importing Flask app: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Creating tables...")
    app_simple.create_tables()
    print("Tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Testing Flask app configuration...")
    # Test that the app can be configured properly
    with app_simple.app.test_client() as client:
        response = client.get('/')
        print(f"Flask app responds with status: {response.status_code}")
    print("Flask app is working correctly!")
except Exception as e:
    print(f"Error testing Flask app: {e}")
    traceback.print_exc()
    sys.exit(1)
