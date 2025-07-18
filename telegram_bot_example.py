#!/usr/bin/env python3
"""
Пример интеграции с телеграм-ботом
Демонстрирует как использовать сервис для обработки голосовых сообщений
"""
import requests
import time
import io

# Конфигурация
SPEECH_SERVICE_URL = "http://localhost:8338"

def transcribe_audio_file(file_path, client_id, segment_number=None):
    """
    Отправить аудиофайл в сервис для транскрипции
    
    Args:
        file_path: Путь к аудиофайлу
        client_id: ID клиента (например, ID пользователя в телеграм)
        segment_number: Номер сегмента (опционально)
    
    Returns:
        dict: Результат транскрипции или ошибка
    """
    try:
        # Открыть файл
        with open(file_path, 'rb') as audio_file:
            files = {
                'file': (file_path, audio_file, 'audio/wav')
            }
            
            data = {
                'client_id': str(client_id),
                'segment_number': str(segment_number) if segment_number else 'unknown'
            }
            
            # Отправить запрос
            response = requests.post(
                f"{SPEECH_SERVICE_URL}/transcribe",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'result': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def transcribe_audio_data(audio_data, filename, client_id, segment_number=None):
    """
    Отправить аудиоданные в сервис для транскрипции
    
    Args:
        audio_data: Бинарные данные аудиофайла
        filename: Имя файла
        client_id: ID клиента
        segment_number: Номер сегмента (опционально)
    
    Returns:
        dict: Результат транскрипции или ошибка
    """
    try:
        files = {
            'file': (filename, io.BytesIO(audio_data), 'audio/ogg')
        }
        
        data = {
            'client_id': str(client_id),
            'segment_number': str(segment_number) if segment_number else 'unknown'
        }
        
        # Отправить запрос
        response = requests.post(
            f"{SPEECH_SERVICE_URL}/transcribe",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'result': response.json()
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_service_status():
    """Получить статус сервиса"""
    try:
        response = requests.get(f"{SPEECH_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

def get_service_stats():
    """Получить статистику сервиса"""
    try:
        response = requests.get(f"{SPEECH_SERVICE_URL}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

# Пример использования с PyTelegramBotAPI
def telegram_bot_example():
    """
    Пример интеграции с телеграм-ботом
    
    Установите: pip install pyTelegramBotAPI
    """
    print("📞 Пример интеграции с телеграм-ботом")
    print("=" * 50)
    
    # Проверим статус сервиса
    status = get_service_status()
    if not status or not status.get('model_ready'):
        print("❌ Сервис не готов к работе")
        return
    
    print(f"✅ Сервис готов: {status.get('service')} v{status.get('version')}")
    
    # Пример кода для бота
    bot_code = '''
import telebot
import requests
import io

bot = telebot.TeleBot("YOUR_BOT_TOKEN")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Получить информацию о файле
        file_info = bot.get_file(message.voice.file_id)
        
        # Скачать файл
        audio_data = bot.download_file(file_info.file_path)
        
        # Отправить в сервис транскрипции
        files = {
            'file': ('voice.ogg', io.BytesIO(audio_data), 'audio/ogg')
        }
        
        data = {
            'client_id': str(message.from_user.id),
            'segment_number': str(message.message_id)
        }
        
        response = requests.post(
            'http://localhost:8338/transcribe',
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('translated_text', '')
            processing_time = result.get('processing_time', 0)
            
            if text.strip():
                bot.reply_to(message, f"🎵➡️📝 {text}")
                print(f"✅ Processed voice for user {message.from_user.id}: {text[:50]}...")
            else:
                bot.reply_to(message, "🤷‍♂️ Не удалось распознать речь")
        else:
            bot.reply_to(message, "❌ Ошибка обработки аудио")
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        bot.reply_to(message, "❌ Произошла ошибка")
        print(f"❌ Exception: {e}")

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    # Аналогично для аудио файлов
    handle_voice(message)

@bot.message_handler(commands=['status'])
def handle_status(message):
    try:
        response = requests.get('http://localhost:8338/health', timeout=5)
        if response.status_code == 200:
            status = response.json()
            bot.reply_to(message, f"🤖 Сервис: {status.get('status', 'unknown')}")
        else:
            bot.reply_to(message, "❌ Сервис недоступен")
    except Exception:
        bot.reply_to(message, "❌ Ошибка подключения к сервису")

# Запуск бота
if __name__ == '__main__':
    print("🤖 Telegram bot started...")
    bot.polling(none_stop=True)
    '''
    
    print("\n📝 Пример кода для телеграм-бота:")
    print(bot_code)
    
    # Тестирование с локальным файлом
    print("\n🧪 Тестирование с локальным файлом:")
    test_file = "uploads/Speech-to-TXT-Server_segment_20.wav"
    
    result = transcribe_audio_file(test_file, "test_user", 1)
    
    if result['success']:
        data = result['result']
        print(f"✅ Транскрипция успешна!")
        print(f"📝 Текст: {data.get('translated_text', '')}")
        print(f"⏱️ Время: {data.get('processing_time', 0):.2f}s")
    else:
        print(f"❌ Ошибка: {result['error']}")

if __name__ == "__main__":
    telegram_bot_example()
