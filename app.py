"""
Entry point for Render deployment
This file redirects to the actual app in web_app folder
"""
import sys
import os

# Add web_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))

# Import and run the actual app
from web_app.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'

    print("=" * 60)
    print(" TRANSTAR-NAGEL WEB INTERFACE ".center(60))
    print("=" * 60)
    print(f"✅ Сервер запущен на порту {port}")
    print("=" * 60)

    app.run(debug=debug_mode, host='0.0.0.0', port=port)