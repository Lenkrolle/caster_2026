#!/usr/bin/env python3
"""
Локальний сервер для запуску програми Caster.

Запускає HTTP сервер на порту 8000 в папці де лежить цей скрипт,
автоматично відкриває браузер на http://localhost:8000/caster.html
і закриває сервер при виході (Ctrl+C).

Запуск:
  python3 start_caster.py

Працює на Windows, macOS, Linux. Потребує тільки Python 3
(вбудований модуль http.server — нічого додатково встановлювати не треба).
"""

import http.server
import socketserver
import webbrowser
import threading
import os
import sys
import time

PORT = 8000
HTML_FILE = "caster.html"


def get_app_dir():
    """
    Знайти папку з файлами програми.
    Якщо запущено як звичайний .py файл — це папка зі скриптом.
    Якщо запущено як зібраний PyInstaller .exe/.app — це тимчасова
    папка куди PyInstaller розпаковує додані файли (--add-data).
    """
    if getattr(sys, 'frozen', False):
        # Запущено як упакований виконуваний файл (PyInstaller)
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def find_free_port(start_port):
    """Якщо порт зайнятий — спробувати наступні 10 портів."""
    import socket
    port = start_port
    for _ in range(10):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start_port  # якщо все зайняте — повернути початковий і нехай впаде з помилкою


def main():
    # Знайти папку з файлами програми (звичайний скрипт або упакований .exe)
    script_dir = get_app_dir()
    os.chdir(script_dir)

    if not os.path.exists(HTML_FILE):
        print(f"⚠️  Файл {HTML_FILE} не знайдено в папці {script_dir}")
        print("    Поклади start_caster.py в ту саму папку що і caster.html")
        input("Натисни Enter щоб закрити...")
        sys.exit(1)

    port = find_free_port(PORT)

    handler = http.server.SimpleHTTPRequestHandler

    class QuietHandler(handler):
        # Прибрати зайвий лог запитів в консоль — щоб не засмічувати вивід
        def log_message(self, format, *args):
            pass

    with socketserver.TCPServer(("127.0.0.1", port), QuietHandler) as httpd:
        url = f"http://localhost:{port}/{HTML_FILE}"
        
        # Визначити ОС щоб показати правильне ім'я файлу
        if sys.platform == "win32":
            script_name = "start_caster.bat"
        elif sys.platform == "darwin":
            script_name = "start_caster.command"
        else:
            script_name = "start_caster.py"
        
        print("=" * 60)
        print("  🚀 Caster — запущено")
        print("=" * 60)
        print(f"  Адреса:  {url}")
        print("")
        print("  ⚠️  Важливо!")
        print(f"  Запускай програму через файл {script_name},")
        print("  Так програма матиме доступ до папки з файлами на диску.")
        print("  Синхронізація буде працювати без проблем.")
        print("")
        print("  Щоб зупинити сервер — натисни Ctrl+C")
        print("=" * 60)

        # Відкрити браузер через секунду — щоб сервер встиг стартувати
        def open_browser():
            time.sleep(1)
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nЗупиняю сервер...")
            httpd.shutdown()
            print("Сервер закрито. До побачення!")


if __name__ == "__main__":
    main()
