# fast_whisper_service.py
"""
Optimized Faster-Whisper Service
Single model instance for fast processing
"""
import time
import threading
from typing import Optional, Tuple, Dict, Any, List

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

class FastWhisperService:
    """Singleton service for fast audio transcription"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.model = None
        self.model_size = "small"
        self.compute_type = "int8"
        self.device = "cpu"
        self._model_lock = threading.Lock()
        self._loading = False
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'total_time': 0.0,
            'errors': 0,
            'average_time': 0.0
        }
        
        print(f"🚀 FastWhisperService initialized")
        print(f"📊 Model: {self.model_size}")
        print(f"⚙️  Compute type: {self.compute_type}")
        print(f"🖥️  Device: {self.device}")
    
    def _load_model(self) -> bool:
        """Load model if not already loaded"""
        if self.model is not None:
            return True
            
        if not FASTER_WHISPER_AVAILABLE:
            print("❌ faster-whisper not available. Install with: pip install faster-whisper")
            return False
        
        with self._model_lock:
            if self.model is not None:
                return True
                
            if self._loading:
                # Wait for another thread to finish loading
                while self._loading:
                    time.sleep(0.1)
                return self.model is not None
            
            self._loading = True
            try:
                print(f"🔄 Loading {self.model_size} model...")
                start_time = time.time()
                
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                
                load_time = time.time() - start_time
                print(f"✅ Model loaded in {load_time:.2f}s")
                return True
                
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                self.model = None
                return False
            finally:
                self._loading = False
    
    def _extract_words(self, segments) -> List[Dict[str, Any]]:
        """Extract word-level timestamps from whisper segments."""
        words: List[Dict[str, Any]] = []

        for segment in segments:
            for word in getattr(segment, 'words', []) or []:
                word_text = (getattr(word, 'word', '') or '').strip()
                if not word_text:
                    continue

                words.append({
                    'word': word_text,
                    'start': round(float(getattr(word, 'start', 0.0) or 0.0), 3),
                    'end': round(float(getattr(word, 'end', 0.0) or 0.0), 3)
                })

        return words

    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        include_words: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Transcribe audio file
        
        Args:
            file_path: Path to audio file
            language: Language code (None for auto-detection)
            include_words: Include word-level timestamps in result
            
        Returns:
            Tuple of (transcription_result, error_message)
        """
        if not self._load_model():
            return None, "Model not available"
        
        start_time = time.time()
        
        try:
            # Transcribe with optimized settings
            segments, info = self.model.transcribe(
                file_path,
                language=language,
                beam_size=1,        # Faster
                best_of=1,          # Faster
                temperature=0.0,    # More stable
                vad_filter=True,    # Voice activity detection
                vad_parameters={"min_silence_duration_ms": 500},
                word_timestamps=include_words
            )
            
            # Collect transcription
            segment_list = list(segments)
            transcription = ""
            for segment in segment_list:
                transcription += segment.text + " "
            
            transcription = transcription.strip()
            result = {
                'text': transcription,
                'detected_language': getattr(info, 'language', None)
            }

            if include_words:
                result['words'] = self._extract_words(segment_list)
            
            # Update statistics
            process_time = time.time() - start_time
            self.stats['total_processed'] += 1
            self.stats['total_time'] += process_time
            self.stats['average_time'] = self.stats['total_time'] / self.stats['total_processed']
            
            return result, None
            
        except Exception as e:
            self.stats['errors'] += 1
            return None, str(e)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            'model_loaded': self.model is not None,
            'model_size': self.model_size,
            'compute_type': self.compute_type,
            'device': self.device,
            **self.stats
        }
    
    def is_ready(self) -> bool:
        """Check if service is ready to process requests"""
        return self.model is not None or self._load_model()

# Global service instance
whisper_service = FastWhisperService()
