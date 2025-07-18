# Quick Start Guide

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка конфигурации
Скопируйте `.env.example` в `.env` и настройте пути:
```env
AUDIO_SOURCE_DIR=путь/к/аудио/файлам
OUTPUT_DIR=путь/к/результатам
MODEL_SIZE=small
COMPUTE_TYPE=int8
TRANSCRIPTION_OUT_LOG=1
```

### 3. Запуск сервиса
```bash
python start_service.py
```

### 4. Тестирование
```bash
python test_service.py
```

## 📋 Основные файлы

- `start_service.py` - Запуск сервиса
- `test_service.py` - Тестирование API
- `batch_process.py` - Пакетная обработка файлов
- `telegram_bot_example.py` - Пример интеграции с ботом
- `SERVICE_OVERVIEW.md` - Подробная документация

## 🔌 API Endpoints

- `POST /transcribe` - Транскрипция аудио
- `GET /health` - Статус сервиса
- `GET /stats` - Статистика
- `POST /queue/add` - Добавить в очередь
- `GET /queue/status` - Статус очереди

## 📞 Поддержка

По умолчанию сервис запускается на `http://localhost:8338`
