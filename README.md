# Speech-to-Text Service

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

A high-performance speech-to-text service built with faster-whisper for real-time audio transcription. Optimized for Telegram bots and batch processing.

## ✨ Features

- **⚡ Fast Processing** - Uses faster-whisper with optimized settings
- **🎯 Singleton Model** - Loads once in memory for instant responses
- **🔄 Dual Operation Modes**:
  - HTTP API for direct requests from Telegram bots
  - File queue processor for batch processing
- **🚀 Multi-threading** - Parallel processing for high performance
- **🎵 Format Support** - MP3, OGG, WAV, M4A, FLAC, AAC, MP4
- **🌍 Language Support** - Auto detection + 80+ specific languages (pl, ru, en, de, fr, etc.)
- **📊 Real-time Monitoring** - Built-in statistics and health checks

## 📋 Requirements

- Python 3.8+
- RAM: minimum 2GB (for small model)
- CPU support (GPU optional)

## � Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/speech-to-text-service.git
cd speech-to-text-service
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` to `.env` and adjust settings:
```env
AUDIO_SOURCE_DIR=./audio_input
OUTPUT_DIR=./output
MODEL_SIZE=small
COMPUTE_TYPE=int8
TRANSCRIPTION_OUT_LOG=1
```

### 4. Start the service
```bash
python start_service.py
```

The service will be available at `http://localhost:8338`

### 5. Test the service
```bash
python test_service.py
```

## 🔌 API Endpoints

### Core Endpoints

- `GET /` - Service status
- `GET /health` - Detailed health check
- `GET /stats` - Processing statistics
- `POST /transcribe` - Main transcription endpoint
- `POST /update/` - Legacy endpoint (backward compatibility)

### Queue Processing

- `POST /queue/add` - Add directory to processing queue
- `GET /queue/status` - Queue processing status

## 📝 Usage Examples

### HTTP API (for Telegram bots)

```python
import requests

# Send audio file for transcription
files = {'file': ('audio.wav', open('audio.wav', 'rb'), 'audio/wav')}
data = {
    'client_id': 'telegram_bot',
    'segment_number': '1'
}

response = requests.post('http://localhost:8338/transcribe', files=files, data=data)
result = response.json()
print(result['translated_text'])

# Optional: word-level timestamps for karaoke-style highlighting
data['include_words'] = 'true'
response = requests.post('http://localhost:8338/transcribe', files=files, data=data)
result = response.json()
print(result.get('words', [])[:5])
```

### Batch Processing

```bash
# Add directory to processing queue
python batch_process.py /path/to/audio/files /path/to/output
```

### cURL Examples

```bash
# Health check
curl http://localhost:8338/health

# Send file for transcription (auto-detect language)
curl -X POST http://localhost:8338/transcribe \
  -F "file=@audio.wav" \
  -F "client_id=test" \
  -F "segment_number=1"

# Send file for transcription with specific language (Polish)
curl -X POST http://localhost:8338/transcribe \
  -F "file=@audio.wav" \
  -F "client_id=test" \
  -F "segment_number=1" \
  -F "language=pl"

# Send file for transcription with word-level timestamps
curl -X POST http://localhost:8338/transcribe \
  -F "file=@audio.wav" \
  -F "client_id=test" \
  -F "segment_number=1" \
  -F "include_words=true"

# Supported languages include:
# pl (Polish), ru (Russian), en (English), de (German), fr (French), 
# es (Spanish), it (Italian), pt (Portuguese), nl (Dutch), sv (Swedish),
# and 70+ more languages - see endpoint docs for full list
```

## 📊 Performance

- **Model**: small (39 languages)
- **Precision**: int8 (fast processing)
- **Processing Time**: ~0.1-0.5 seconds per second of audio
- **Memory Usage**: ~500MB for small model
- **Startup Time**: ~1.3 seconds (first load only)
- **Word Timestamps**: Available on demand via `include_words=true`; expect a small performance hit only for those requests

## 🔧 Configuration

### Environment Variables (.env)

```env
# Directories
AUDIO_SOURCE_DIR=./audio_input
OUTPUT_DIR=./output

# Model Configuration
MODEL_SIZE=small          # tiny, base, small, medium, large
COMPUTE_TYPE=int8         # int8, float16, float32

# Service Settings
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8338
LOG_LEVEL=INFO
TRANSCRIPTION_OUT_LOG=1
```

### Model Selection

- `tiny` - Fastest, basic accuracy
- `base` - Balance of speed and accuracy
- `small` - **Recommended** - Good accuracy, fast
- `medium` - High accuracy, slower
- `large` - Maximum accuracy, slowest

## 📂 Project Structure

```
├── src/
│   ├── app.py                    # Main FastAPI service
│   ├── fast_whisper_service.py   # Singleton Whisper service
│   ├── file_queue_processor.py   # File queue processor
│   ├── transformer.py            # File processing logic
│   └── converters/
│       └── audio_converter.py    # Audio format converter
├── start_service.py              # Service startup script
├── test_service.py               # API testing
├── batch_process.py              # Batch processing
├── telegram_bot_example.py       # Telegram bot integration example
├── uploads/                      # Temporary files
└── output/                       # Transcription results
```

## � Testing

Run the test suite:
```bash
python test_service.py
```

Or with service startup wait:
```bash
python test_service.py --wait
```

## 📈 Monitoring

Use the `/stats` endpoint for monitoring:

```bash
curl http://localhost:8338/stats
```

Returns statistics on processed files, processing time, and errors.

## 🐳 Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8338

CMD ["python", "start_service.py"]
```

Build and run:
```bash
docker build -t speech-to-text-service .
docker run -p 8338:8338 speech-to-text-service
```

## 🔐 Security

- Local IP restriction (can be disabled for production)
- No authentication by default (add as needed)
- File cleanup after processing
- Safe file handling

## 🛠️ Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with hot reload
python src/app.py
```

### Adding New Features

1. Create feature branch
2. Add functionality
3. Update tests
4. Submit pull request

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Service Overview](SERVICE_OVERVIEW.md)
- [API Documentation](http://localhost:8338/docs) (when service is running)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [pydub](https://github.com/jiaaro/pydub) - Audio processing library

## � Support

- Create an issue for bug reports
- Check logs for troubleshooting
- Ensure sufficient RAM for model loading
- Use Docker for production deployment

---

Built with ❤️ for fast and reliable speech-to-text processing.
