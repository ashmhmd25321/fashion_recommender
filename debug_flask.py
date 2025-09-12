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
    print("Testing Flask app run...")
    app_simple.app.run(host='0.0.0.0', port=5001, debug=False)
except Exception as e:
    print(f"Error running Flask app: {e}")
    traceback.print_exc()
    sys.exit(1)
