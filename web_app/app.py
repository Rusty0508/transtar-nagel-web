#!/usr/bin/env python3
"""
TRANSTAR-NAGEL Web Interface
Flask веб-приложение для обработки транспортных документов
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd

# Добавляем путь к основным модулям
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from transtar_nagel_final import FinalDocumentProcessor

app = Flask(__name__)
CORS(app)

# Конфигурация
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB макс размер
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'pdf'}

# Глобальная переменная для хранения прогресса
processing_status = {
    'status': 'idle',
    'progress': 0,
    'message': '',
    'details': {}
}

def allowed_file(filename):
    """Проверка допустимых расширений файлов"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Главная страница с интерфейсом"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Загрузка и обработка файлов"""
    global processing_status

    try:
        # Проверка наличия файлов
        if 'orders' not in request.files and 'gutschrifts' not in request.files:
            return jsonify({'error': 'Не загружены файлы'}), 400

        # Создание временных папок
        temp_dir = tempfile.mkdtemp()
        orders_dir = os.path.join(temp_dir, 'orders')
        gutschrifts_dir = os.path.join(temp_dir, 'gutschrifts')
        os.makedirs(orders_dir, exist_ok=True)
        os.makedirs(gutschrifts_dir, exist_ok=True)

        # Сохранение транспортных заказов
        order_files = request.files.getlist('orders')
        for file in order_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(orders_dir, filename))

        # Сохранение гутшрифтов
        gutschrift_files = request.files.getlist('gutschrifts')
        for file in gutschrift_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(gutschrifts_dir, filename))

        # Установка начального статуса
        processing_status = {
            'status': 'processing',
            'progress': 10,
            'message': 'Начинаю обработку документов...',
            'details': {
                'orders_count': len(order_files),
                'gutschrifts_count': len(gutschrift_files)
            }
        }

        # Парсинг документов
        processing_status['progress'] = 30
        processing_status['message'] = 'Обрабатываю документы...'

        processor = FinalDocumentProcessor()

        # Установка пользовательских путей для документов
        processor.orders_path = Path(orders_dir)
        processor.gutschrifts_path = Path(gutschrifts_dir)

        print(f"📁 Orders directory: {orders_dir}")
        print(f"   Files: {list(Path(orders_dir).glob('*.pdf'))}")
        print(f"📁 Gutschrifts directory: {gutschrifts_dir}")
        print(f"   Files: {list(Path(gutschrifts_dir).glob('*.pdf'))}")

        # Загрузка документов
        processing_status['progress'] = 40
        processing_status['message'] = 'Загружаю документы...'
        processor.load_documents()

        processing_status['details']['parsed_orders'] = len(processor.transport_orders)
        processing_status['details']['parsed_gutschrifts'] = len(processor.gutschrifts)

        # Сопоставление документов
        processing_status['progress'] = 60
        processing_status['message'] = 'Сопоставляю заказы с гутшрифтами...'
        processor.match_documents()

        # Генерация отчета
        processing_status['progress'] = 80
        processing_status['message'] = 'Генерирую отчет...'
        matched_df = processor.generate_report()

        # Подготовка статистики
        matched_count = sum(1 for o in processor.transport_orders if o.gutschrift_number)
        unmatched_count = len(processor.transport_orders) - matched_count

        stats = {
            'orders_count': len(processor.transport_orders),
            'gutschrifts_count': len(processor.gutschrifts),
            'matched_count': matched_count,
            'unmatched_count': unmatched_count
        }

        # Генерация Excel отчета
        processing_status['progress'] = 90
        processing_status['message'] = 'Генерирую Excel отчет...'

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(parent_dir) / 'output'
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f'transtar_web_{timestamp}.xlsx'

        # Экспорт в Excel используя метод процессора
        processor.export_to_excel_custom(matched_df, str(output_file), stats)

        # Завершение обработки
        processing_status = {
            'status': 'completed',
            'progress': 100,
            'message': 'Обработка завершена успешно!',
            'details': {
                'orders_count': stats.get('orders_count', 0),
                'gutschrifts_count': stats.get('gutschrifts_count', 0),
                'matched_count': stats.get('matched_count', 0),
                'unmatched_count': stats.get('unmatched_count', 0),
                'output_file': str(output_file.name),
                'statistics': stats
            }
        }

        # Очистка временных файлов
        shutil.rmtree(temp_dir)

        return jsonify({
            'success': True,
            'file': str(output_file.name),
            'stats': processing_status['details']
        })

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()

        processing_status = {
            'status': 'error',
            'progress': 0,
            'message': f'Ошибка: {str(e)}',
            'details': {
                'error_type': type(e).__name__,
                'traceback': error_traceback
            }
        }

        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK:\n{error_traceback}")

        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@app.route('/status')
def get_status():
    """Получение текущего статуса обработки"""
    return jsonify(processing_status)

@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание готового Excel файла"""
    try:
        file_path = Path(parent_dir) / 'output' / filename
        if file_path.exists():
            return send_file(
                str(file_path),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({'error': 'Файл не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    """Получение истории обработанных файлов"""
    try:
        output_dir = Path(parent_dir) / 'output'
        files = []
        if output_dir.exists():
            for file in sorted(output_dir.glob('*.xlsx'), key=os.path.getmtime, reverse=True)[:10]:
                files.append({
                    'name': file.name,
                    'size': f"{file.stat().st_size / 1024:.1f} KB",
                    'date': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print(" TRANSTAR-NAGEL WEB INTERFACE ".center(60))
    print("=" * 60)
    print(f"✅ Сервер запущен на http://localhost:5001")
    print(f"📁 Результаты сохраняются в: {Path(parent_dir) / 'output'}")
    print("\nДля остановки нажмите Ctrl+C")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5001)