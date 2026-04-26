import traceback
import sys

print("Python version:", sys.version)
print("Path:", sys.path[:3])

try:
    print("\n[1] Importing FastAPI...")
    from fastapi import FastAPI
    print("    ✓ FastAPI imported")
    
    print("[2] Loading .env...")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    print("    ✓ .env loaded")
    print(f"    - DJANGO_API_URL: {os.getenv('DJANGO_API_URL')}")
    
    print("[3] Importing httpx...")
    import httpx
    print("    ✓ httpx imported")
    
    print("[4] Importing main.app...")
    from main import app
    print("    ✓ main.app imported")
    
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print(f"App: {app}")
    print(f"App title: {app.title}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
