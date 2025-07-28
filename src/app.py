# app.py
"""
Optimized FastAPI service for audio to text transcription
Uses faster-whisper for efficient processing
"""
import sys
import os
import time
import asyncio
import threading
from typing import Optional

import netifaces
from fastapi import FastAPI, HTTPException, Request, UploadFile, Form, File, BackgroundTasks
from fastapi.responses import JSONResponse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformer import handle_file_upload, transcribe_audio
from fast_whisper_service import whisper_service
from file_queue_processor import FileQueueProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Speech-to-Text Service",
    description="Optimized service for audio transcription using faster-whisper",
    version="2.0.0"
)

# Global variables
file_queue_processor = None
service_stats = {
    'started_at': time.time(),
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0
}

def get_local_ips():
    """Get all local IP addresses"""
    local_ips = set()
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for addr_info in addresses[netifaces.AF_INET]:
                local_ips.add(addr_info['addr'])
    return local_ips

# Get local IPs for security
local_ips = get_local_ips()
print(f"🌐 Local IPs: {local_ips}")

# TEMPORARILY DISABLED FOR REMOTE ACCESS
# @app.middleware("http")
# async def check_request_origin(request: Request, call_next):
#     """Security middleware to check request origin"""
#     client_host = request.client.host
#     if client_host not in local_ips:
#         raise HTTPException(
#             status_code=403, 
#             detail="Forbidden: requests from this host are not allowed"
#         )
#     response = await call_next(request)
#     return response

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    global file_queue_processor
    
    print("🚀 Starting Speech-to-Text Service...")
    
    # Pre-load the model
    print("📥 Pre-loading whisper model...")
    if whisper_service.is_ready():
        print("✅ Whisper model loaded successfully")
    else:
        print("❌ Failed to load whisper model")
    
    # Start file queue processor
    file_queue_processor = FileQueueProcessor()
    file_queue_processor.start()
    
    print("✅ Service startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global file_queue_processor
    
    print("🛑 Shutting down Speech-to-Text Service...")
    
    if file_queue_processor:
        file_queue_processor.stop()
    
    print("✅ Service shutdown completed")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Speech-to-Text Service",
        "version": "2.0.0",
        "status": "running",
        "model_ready": whisper_service.is_ready(),
        "uptime": time.time() - service_stats['started_at']
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "service": "Speech-to-Text Service",
        "status": "healthy" if whisper_service.is_ready() else "unhealthy",
        "model_ready": whisper_service.is_ready(),
        "whisper_stats": whisper_service.get_stats(),
        "service_stats": service_stats,
        "uptime": time.time() - service_stats['started_at']
    }

@app.post("/transcribe")
async def transcribe_endpoint(
    file: UploadFile = File(...),
    client_id: str = Form(...),  
    segment_number: str = Form(default='unknown'),
    language: Optional[str] = Form(default=None)
):
    """
    Main transcription endpoint
    
    Args:
        file: Audio file to transcribe
        client_id: Client identifier
        segment_number: Segment number for file naming
        language: Language code (optional). Examples:
                 'pl' - Polish, 'ru' - Russian, 'en' - English, 'de' - German,
                 'fr' - French, 'es' - Spanish, 'it' - Italian, 'pt' - Portuguese,
                 'nl' - Dutch, 'sv' - Swedish, 'da' - Danish, 'no' - Norwegian,
                 'fi' - Finnish, 'cs' - Czech, 'sk' - Slovak, 'hu' - Hungarian,
                 'ro' - Romanian, 'bg' - Bulgarian, 'hr' - Croatian, 'sl' - Slovenian,
                 'et' - Estonian, 'lv' - Latvian, 'lt' - Lithuanian, 'uk' - Ukrainian,
                 'be' - Belarusian, 'mk' - Macedonian, 'sr' - Serbian, 'bs' - Bosnian,
                 'mt' - Maltese, 'cy' - Welsh, 'ga' - Irish, 'is' - Icelandic,
                 'eu' - Basque, 'ca' - Catalan, 'gl' - Galician, 'ast' - Asturian,
                 'ar' - Arabic, 'he' - Hebrew, 'tr' - Turkish, 'fa' - Persian,
                 'ur' - Urdu, 'hi' - Hindi, 'bn' - Bengali, 'ta' - Tamil,
                 'te' - Telugu, 'kn' - Kannada, 'ml' - Malayalam, 'si' - Sinhala,
                 'th' - Thai, 'lo' - Lao, 'my' - Myanmar, 'km' - Khmer,
                 'ka' - Georgian, 'am' - Amharic, 'ne' - Nepali, 'mr' - Marathi,
                 'gu' - Gujarati, 'pa' - Punjabi, 'or' - Odia, 'as' - Assamese,
                 'zh' - Chinese, 'ja' - Japanese, 'ko' - Korean, 'vi' - Vietnamese,
                 'id' - Indonesian, 'ms' - Malay, 'tl' - Tagalog, 'jw' - Javanese,
                 'su' - Sundanese, 'mg' - Malagasy, 'sw' - Swahili, 'yo' - Yoruba,
                 'ha' - Hausa, 'zu' - Zulu, 'af' - Afrikaans, 'sq' - Albanian,
                 'az' - Azerbaijani, 'hy' - Armenian, 'kk' - Kazakh, 'ky' - Kyrgyz,
                 'uz' - Uzbek, 'tj' - Tajik, 'mn' - Mongolian, 'tt' - Tatar,
                 'ba' - Bashkir, 'sah' - Yakut, 'fo' - Faroese, 'br' - Breton,
                 'oc' - Occitan, 'la' - Latin, 'sa' - Sanskrit, 'yi' - Yiddish,
                 'haw' - Hawaiian, 'mi' - Maori, 'ln' - Lingala, 'so' - Somali,
                 'sn' - Shona, 'lb' - Luxembourgish
                 Use 'auto' or omit for automatic detection.
    """
    start_time = time.time()
    service_stats['total_requests'] += 1
    
    try:
        print(f"🎵 Request - File: {file.filename}, Client: {client_id}, Segment: {segment_number}")
        
        # Handle file upload
        filepath, filename = handle_file_upload(client_id, file, segment_number)
        
        # Process language parameter
        target_language = None
        if language and language.lower() not in ['auto', 'none', '']:
            target_language = language.lower()
            print(f"🌍 Using specified language: {target_language}")
        else:
            print("🌍 Using auto-detection")
        
        # Transcribe audio
        transcription, error = transcribe_audio(filepath, target_language)
        
        if error:
            service_stats['failed_requests'] += 1
            print(f"❌ Transcription error: {error}")
            raise HTTPException(status_code=500, detail=f"Transcription error: {error}")
        
        # Log results if enabled
        if int(os.getenv('TRANSCRIPTION_OUT_LOG', '0')) == 1:
            print(f"📝 Client: {client_id}, File: {filename}, Text: {transcription}")
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except Exception as cleanup_error:
            print(f"⚠️ Warning: Could not delete {filepath}: {cleanup_error}")
        
        # Update statistics
        service_stats['successful_requests'] += 1
        process_time = time.time() - start_time
        
        return {
            "success": True,
            "translated_text": transcription,
            "processing_time": round(process_time, 2),
            "filename": filename,
            "segment_number": segment_number,
            "language": target_language if target_language else "auto-detected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        service_stats['failed_requests'] += 1
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/update/")
async def transformation_flow(
    file: UploadFile = File(...),
    clientId: str = Form(...),  
    segment_number: str = Form(default='unknown'),
    language: Optional[str] = Form(default=None)
):
    """
    Legacy endpoint for backward compatibility
    """
    return await transcribe_endpoint(file, clientId, segment_number, language)

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "service_stats": service_stats,
        "whisper_stats": whisper_service.get_stats(),
        "uptime": time.time() - service_stats['started_at']
    }

@app.post("/queue/add")
async def add_to_queue(
    source_dir: str = Form(...),
    output_dir: Optional[str] = Form(default=None)
):
    """
    Add directory to file processing queue
    """
    global file_queue_processor
    
    if not file_queue_processor:
        raise HTTPException(status_code=503, detail="File queue processor not available")
    
    try:
        files_added = file_queue_processor.add_directory(source_dir, output_dir)
        return {
            "success": True,
            "message": f"Directory added to queue: {source_dir}",
            "files_added": files_added,
            "queue_size": file_queue_processor.queue.qsize()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to queue: {str(e)}")

@app.get("/queue/status")
async def get_queue_status():
    """Get file queue status"""
    global file_queue_processor
    
    if not file_queue_processor:
        raise HTTPException(status_code=503, detail="File queue processor not available")
    
    return file_queue_processor.get_status()

if __name__ == "__main__":
    import hypercorn.asyncio
    import asyncio

    async def main():
        """Run the service"""
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
        
        await hypercorn.asyncio.serve(app, config)

    asyncio.run(main())