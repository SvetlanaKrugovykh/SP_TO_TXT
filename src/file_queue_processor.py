# file_queue_processor.py
"""
File Queue Processor for batch processing of audio files
Processes files from directories in background
"""
import os
import time
import threading
import queue
import glob
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime

from fast_whisper_service import whisper_service
from converters.audio_converter import convert_to_wav

class FileQueueProcessor:
    """Background processor for audio file queues"""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.processing_thread = None
        self.is_running = False
        self.stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'total_time': 0.0,
            'current_file': None,
            'queue_size': 0
        }
        
        # Supported audio formats
        self.supported_extensions = {'.ogg', '.m4a', '.wav', '.mp3', '.flac', '.aac', '.mp4'}
        
        # Default directories
        self.default_source_dir = os.getenv('AUDIO_SOURCE_DIR', './audio_input')
        self.default_output_dir = os.getenv('OUTPUT_DIR', './output')
    
    def start(self):
        """Start the background processing thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
        
        print("🔄 File queue processor started")
    
    def stop(self):
        """Stop the background processing thread"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        print("⏹️ File queue processor stopped")
    
    def add_directory(self, source_dir: str, output_dir: Optional[str] = None):
        """Add a directory to the processing queue"""
        if not os.path.exists(source_dir):
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        if output_dir is None:
            output_dir = self.default_output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all audio files in the directory
        audio_files = self._find_audio_files(source_dir)
        
        if not audio_files:
            print(f"⚠️ No audio files found in {source_dir}")
            return
        
        # Add files to queue
        for audio_file in audio_files:
            self.queue.put({
                'file_path': audio_file,
                'output_dir': output_dir,
                'added_at': time.time()
            })
        
        self.stats['queue_size'] = self.queue.qsize()
        print(f"📁 Added {len(audio_files)} files from {source_dir} to queue")
        return len(audio_files)
    
    def add_file(self, file_path: str, output_dir: Optional[str] = None):
        """Add a single file to the processing queue"""
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        if output_dir is None:
            output_dir = self.default_output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.queue.put({
            'file_path': file_path,
            'output_dir': output_dir,
            'added_at': time.time()
        })
        
        self.stats['queue_size'] = self.queue.qsize()
        print(f"📄 Added file {file_path} to queue")
    
    def _find_audio_files(self, directory: str) -> List[str]:
        """Find all audio files in directory and subdirectories"""
        audio_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                if file_ext in self.supported_extensions:
                    audio_files.append(file_path)
        
        return audio_files
    
    def _process_queue(self):
        """Background thread function to process the queue"""
        print("🎯 Queue processing thread started")
        
        while self.is_running:
            try:
                # Get item from queue with timeout
                try:
                    item = self.queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Update queue size
                self.stats['queue_size'] = self.queue.qsize()
                
                # Process the file
                self._process_file(item)
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                print(f"❌ Error in queue processing: {e}")
                self.stats['failed_processed'] += 1
    
    def _process_file(self, item: Dict[str, Any]):
        """Process a single file"""
        file_path = item['file_path']
        output_dir = item['output_dir']
        
        start_time = time.time()
        self.stats['current_file'] = os.path.basename(file_path)
        
        try:
            print(f"🎵 Processing: {os.path.basename(file_path)}")
            
            # Convert to WAV if needed
            wav_file_path = convert_to_wav(file_path)
            if wav_file_path is None:
                raise ValueError("Failed to convert audio to WAV format")
            
            # Transcribe audio
            transcription, error = whisper_service.transcribe(wav_file_path)
            
            if error:
                raise ValueError(f"Transcription error: {error}")
            
            if not transcription or not transcription.strip():
                raise ValueError("Empty transcription result")
            
            # Save transcription
            self._save_transcription(file_path, transcription, output_dir)
            
            # Update statistics
            process_time = time.time() - start_time
            self.stats['total_processed'] += 1
            self.stats['successful_processed'] += 1
            self.stats['total_time'] += process_time
            
            print(f"✅ Processed: {os.path.basename(file_path)} ({process_time:.2f}s)")
            
        except Exception as e:
            print(f"❌ Failed to process {os.path.basename(file_path)}: {e}")
            self.stats['total_processed'] += 1
            self.stats['failed_processed'] += 1
        
        finally:
            self.stats['current_file'] = None
    
    def _save_transcription(self, file_path: str, transcription: str, output_dir: str):
        """Save transcription to file"""
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"{base_name}_transcription.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Source: {file_path}\n")
            f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Service: Faster-Whisper Queue Processor\n")
            f.write("=" * 60 + "\n\n")
            f.write(transcription)
        
        print(f"💾 Saved: {output_path}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            'is_running': self.is_running,
            'queue_size': self.queue.qsize(),
            'current_file': self.stats.get('current_file'),
            'total_processed': self.stats['total_processed'],
            'successful_processed': self.stats['successful_processed'],
            'failed_processed': self.stats['failed_processed'],
            'total_time': self.stats['total_time'],
            'average_time': (
                self.stats['total_time'] / self.stats['total_processed'] 
                if self.stats['total_processed'] > 0 else 0
            )
        }
    
    def clear_queue(self):
        """Clear all items from the queue"""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
        
        self.stats['queue_size'] = 0
        print("🧹 Queue cleared")
