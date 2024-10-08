from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)


# Конвертация m4a в wav (или другого формата)
def convert_audio(file_path, output_format='wav'):
    audio = AudioSegment.from_file(file_path)
    new_file_path = file_path.rsplit('.', 1)[0] + '.' + output_format
    audio.export(new_file_path, format=output_format)
    return new_file_path


# Распознавание речи
def recognize_speech(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")  # Можно выбрать нужный язык
        return text
    except sr.UnknownValueError:
        return "Google не смог распознать аудио"
    except sr.RequestError as e:
        return f"Ошибка запроса к сервису Google: {e}"


# Маршрут для загрузки аудиофайла и распознавания речи
@app.route('/recognize', methods=['POST'])
def upload_and_recognize():
    if 'file' not in request.files:
        return jsonify({"error": "Аудиофайл не найден"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Файл не выбран"}), 400

    # Сохраняем файл
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Конвертируем, если файл не в формате WAV
    if not file.filename.endswith('.wav'):
        file_path = convert_audio(file_path)

    # Распознаем речь
    result = recognize_speech(file_path)

    # Удаляем временные файлы
    os.remove(file_path)

    return jsonify({"recognized_text": result})


# Главный маршрут для проверки работы сервера
@app.route('/')
def index():
    return "ok"


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='0.0.0.0', port=6001)
