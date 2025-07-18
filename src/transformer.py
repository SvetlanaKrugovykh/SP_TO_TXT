# transformer.py
import os
import sys
from typing import Tuple, Optional

from fast_whisper_service import whisper_service
from converters.audio_converter import convert_to_wav

def handle_file_upload(clientId, file, segment_number):
    """Handle file upload and save to uploads directory"""
    if file.filename == '':
        return {"error": "No selected file"}, 400

    filename = generate_filename(segment_number, clientId)
    filepath = os.path.join('uploads', filename)
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
    
    return filepath, filename

def generate_filename(segment_number, clientId):
    """Generate filename for uploaded file"""
    segment_name = os.getenv('SEGMENT_NAME', 'segment')
    return f"{clientId}_{segment_name}_{segment_number}.wav"
    
def transcribe_audio(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe audio file using faster-whisper service
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Tuple of (transcription_text, error_message)
    """
    try:
        # Convert to WAV format if needed
        wav_file_path = convert_to_wav(file_path)
        if wav_file_path is None:
            return None, "Failed to convert audio to WAV format"
        
        # Transcribe using the optimized service
        transcription, error = whisper_service.transcribe(wav_file_path)
        
        if error:
            print(f"Error in audio transcription: {error}")
            return None, error
        
        return transcription, None
        
    except Exception as e:
        error_msg = f"Error in audio transcription: {e}"
        print(error_msg)
        return None, error_msg
    