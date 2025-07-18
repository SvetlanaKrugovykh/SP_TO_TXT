#!/usr/bin/env python3
"""
Batch file processor using the queue system
"""
import os
import sys
import time
import requests
import json
from pathlib import Path

def add_directory_to_queue(source_dir, output_dir=None):
    """Add directory to processing queue"""
    base_url = "http://localhost:8338"
    
    data = {
        'source_dir': source_dir
    }
    
    if output_dir:
        data['output_dir'] = output_dir
    
    try:
        response = requests.post(f"{base_url}/queue/add", data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Directory added to queue: {source_dir}")
            print(f"   Queue size: {result.get('queue_size', 0)}")
            return True
        else:
            print(f"❌ Failed to add directory: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding directory: {e}")
        return False

def monitor_queue():
    """Monitor queue processing"""
    base_url = "http://localhost:8338"
    
    print("🔍 Monitoring queue processing...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            response = requests.get(f"{base_url}/queue/status")
            
            if response.status_code == 200:
                status = response.json()
                
                print(f"\r📊 Queue: {status.get('queue_size', 0)} files | "
                      f"Processed: {status.get('total_processed', 0)} | "
                      f"Success: {status.get('successful_processed', 0)} | "
                      f"Failed: {status.get('failed_processed', 0)}", end="")
                
                current_file = status.get('current_file')
                if current_file:
                    print(f" | Current: {current_file}", end="")
                
                # If queue is empty and no current file, processing is done
                if status.get('queue_size', 0) == 0 and not current_file:
                    print("\n✅ Queue processing completed!")
                    break
                    
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

def main():
    """Main function"""
    print("📦 Batch File Processor")
    print("=" * 50)
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:8338/health")
        if response.status_code != 200:
            print("❌ Service is not running. Start it first with: python start_service.py")
            sys.exit(1)
    except Exception:
        print("❌ Service is not accessible. Start it first with: python start_service.py")
        sys.exit(1)
    
    # Get source directory
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = os.getenv('AUDIO_SOURCE_DIR')
        if not source_dir:
            source_dir = input("📁 Enter source directory path: ").strip()
    
    if not source_dir or not os.path.exists(source_dir):
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)
    
    # Get output directory
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = os.getenv('OUTPUT_DIR', './output')
    
    print(f"📁 Source: {source_dir}")
    print(f"📁 Output: {output_dir}")
    print("=" * 50)
    
    # Add directory to queue
    if add_directory_to_queue(source_dir, output_dir):
        print("⏳ Processing started...")
        monitor_queue()
    else:
        print("❌ Failed to start processing")
        sys.exit(1)

if __name__ == "__main__":
    main()
