#!/usr/bin/env python3
"""
Launcher script for TPB-Enhanced EWS system.
Runs both the Flask server and real-time data generator.
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def run_flask_server():
    """Run the Flask server"""
    print("🌐 Starting Flask server...")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Flask server error: {e}")
    except KeyboardInterrupt:
        print("🛑 Flask server stopped")

def run_data_generator():
    """Run the real-time data generator"""
    print("📊 Starting real-time data generator...")
    try:
        subprocess.run([sys.executable, "realtime_data_generator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Data generator error: {e}")
    except KeyboardInterrupt:
        print("🛑 Data generator stopped")

def main():
    print("🚀 TPB-Enhanced Early Warning System Launcher")
    print("=" * 50)
    print("This will start both the Flask server and real-time data generator.")
    print("Press Ctrl+C to stop both services.")
    print()
    
    # Check if required files exist
    required_files = ["app.py", "realtime_data_generator.py", "ews_model.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file not found: {file}")
            return
    
    print("✅ All required files found")
    print()
    
    try:
        # Start Flask server in a separate thread
        flask_thread = threading.Thread(target=run_flask_server, daemon=True)
        flask_thread.start()
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("🌐 Flask server started at http://127.0.0.1:8000")
        print("📊 Starting data generator...")
        print()
        
        # Run data generator in main thread
        run_data_generator()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down EWS system...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
