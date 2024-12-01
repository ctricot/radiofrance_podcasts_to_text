from datetime import datetime


def log_message(message: str):
    """Helper function to print messages with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")