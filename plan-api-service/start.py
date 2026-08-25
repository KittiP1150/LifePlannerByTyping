import uvicorn
import webbrowser
import threading
import time
from app.main import app 

def open_browser():
    time.sleep(1.5)
    webbrowser.open("localhost:8000")

if __name__ == '__main__':
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")