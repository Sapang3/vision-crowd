#!/usr/bin/env python3
"""
Start dynamic simulation with high fluctuation for testing.
"""

import subprocess
import sys
import time

def main():
    print("🚀 Starting Dynamic TPB-Enhanced EWS Simulation")
    print("=" * 60)
    print("This will start the data generator with high fluctuation")
    print("for testing the dynamic UI and real-time visualization.")
    print()
    
    try:
        # Start the data generator with interactive input
        print("Starting data generator...")
        print("Duration: 10 minutes")
        print("Update interval: 3 seconds")
        print("High fluctuation mode: ON")
        print()
        
        # Run the data generator with predefined parameters
        process = subprocess.Popen([
            sys.executable, "realtime_data_generator.py"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Send input parameters
        process.stdin.write("10\n")  # 10 minutes duration
        process.stdin.write("3\n")   # 3 seconds interval
        process.stdin.flush()
        
        print("📊 Data generator started!")
        print("🌐 Open http://127.0.0.1:8000 in your browser")
        print("📈 Watch the dynamic charts and metrics update in real-time")
        print()
        print("Press Ctrl+C to stop the simulation")
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        if stdout:
            print(stdout)
        if stderr:
            print("Errors:", stderr)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
