#!/usr/bin/env python3
"""
Test script for the optimized speech-to-text service
"""
import os
import sys
import time
import requests
import json
from pathlib import Path

def test_service():
    """Test the service endpoints"""
    base_url = "http://localhost:8338"
    
    print("🧪 Testing Speech-to-Text Service")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Model ready: {health_data.get('model_ready')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    try:
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint works")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: Stats endpoint
    try:
        print("\n3. Testing stats endpoint...")
        response = requests.get(f"{base_url}/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats endpoint works")
            print(f"   Total requests: {stats.get('service_stats', {}).get('total_requests', 0)}")
            print(f"   Whisper processed: {stats.get('whisper_stats', {}).get('total_processed', 0)}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
    
    # Test 4: Queue status
    try:
        print("\n4. Testing queue status...")
        response = requests.get(f"{base_url}/queue/status")
        
        if response.status_code == 200:
            queue_status = response.json()
            print(f"✅ Queue status works")
            print(f"   Queue size: {queue_status.get('queue_size', 0)}")
            print(f"   Is running: {queue_status.get('is_running', False)}")
        else:
            print(f"❌ Queue status failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Queue status error: {e}")
    
    # Test 5: File transcription (if test file exists)
    test_file = None
    
    # Look for test audio files
    possible_locations = [
        "uploads",
        "test",
        "."
    ]
    
    for location in possible_locations:
        for ext in ['.wav', '.mp3', '.ogg', '.m4a']:
            test_files = list(Path(location).glob(f"*{ext}"))
            if test_files:
                test_file = test_files[0]
                break
        if test_file:
            break
    
    if test_file and test_file.exists():
        try:
            print(f"\n5. Testing file transcription with: {test_file.name}")
            
            files = {
                'file': (test_file.name, open(test_file, 'rb'), 'audio/wav')
            }
            
            data = {
                'client_id': 'test_client',
                'segment_number': '1'
            }
            
            start_time = time.time()
            response = requests.post(f"{base_url}/transcribe", files=files, data=data)
            end_time = time.time()
            
            files['file'][1].close()  # Close file
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Transcription successful")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                print(f"   Total time: {end_time - start_time:.2f}s")
                print(f"   Language: {result.get('language', 'unknown')}")
                print(f"   Text: {result.get('translated_text', '')[:100]}...")
                
                # Test with specific language
                print(f"\n6. Testing Polish transcription with same file...")
                
                files = {
                    'file': (test_file.name, open(test_file, 'rb'), 'audio/wav')
                }
                
                data = {
                    'client_id': 'test_client',
                    'segment_number': '2',
                    'language': 'pl'
                }
                
                start_time = time.time()
                response = requests.post(f"{base_url}/transcribe", files=files, data=data)
                end_time = time.time()
                
                files['file'][1].close()  # Close file
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Polish transcription successful")
                    print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                    print(f"   Total time: {end_time - start_time:.2f}s")
                    print(f"   Language: {result.get('language', 'unknown')}")
                    print(f"   Text: {result.get('translated_text', '')[:100]}...")

                    print(f"\n7. Testing word timestamps with same file...")

                    files = {
                        'file': (test_file.name, open(test_file, 'rb'), 'audio/wav')
                    }

                    data = {
                        'client_id': 'test_client',
                        'segment_number': '3',
                        'include_words': 'true'
                    }

                    start_time = time.time()
                    response = requests.post(f"{base_url}/transcribe", files=files, data=data)
                    end_time = time.time()

                    files['file'][1].close()

                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Word timestamps successful")
                        print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                        print(f"   Total time: {end_time - start_time:.2f}s")
                        print(f"   Words returned: {len(result.get('words', []))}")
                    else:
                        print(f"❌ Word timestamps failed: {response.status_code}")
                        print(f"   Error: {response.text}")
                else:
                    print(f"❌ Polish transcription failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            else:
                print(f"❌ Transcription failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Transcription test error: {e}")
    else:
        print(f"\n5. ⚠️ No test audio file found - skipping transcription test")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed")
    
    return True

if __name__ == "__main__":
    # Wait a bit for service to start if needed
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("⏳ Waiting 5 seconds for service to start...")
        time.sleep(5)
    
    test_service()
