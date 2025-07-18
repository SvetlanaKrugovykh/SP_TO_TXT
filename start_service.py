#!/usr/bin/env python3
"""
Service starter script
Starts the optimized speech-to-text service
"""
import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main function to start the service"""
    print("🚀 Starting Speech-to-Text Service...")
    print("=" * 50)
    
    # Check if required directories exist
    uploads_dir = Path("uploads")
    output_dir = Path("output")
    
    uploads_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Uploads directory: {uploads_dir.absolute()}")
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # Import and run the service
    from src.app import app
    import hypercorn.asyncio
    
    try:
        # Run the service
        config = hypercorn.Config()
        config.bind = ["0.0.0.0:8338"]
        config.workers = 1  # Single worker to maintain model singleton
        config.worker_class = "asyncio"
        
        print("🚀 Starting Speech-to-Text Service on port 8338")
        print("🎯 Endpoints:")
        print("   POST /transcribe - Main transcription endpoint")
        print("   POST /update/ - Legacy endpoint") 
        print("   GET /health - Health check")
        print("   GET /stats - Service statistics")
        print("   POST /queue/add - Add directory to processing queue")
        print("   GET /queue/status - Get queue status")
        
        asyncio.run(hypercorn.asyncio.serve(app, config))
    except KeyboardInterrupt:
        print("\n⚠️ Service stopped by user")
    except Exception as e:
        print(f"\n❌ Service error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
