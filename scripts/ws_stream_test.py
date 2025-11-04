import time
import threading
import json
import sys

# Try imports and install if missing
try:
    import requests
except Exception:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

try:
    from websocket import create_connection, WebSocketTimeoutException
except Exception:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'websocket-client'])
    from websocket import create_connection, WebSocketTimeoutException


def recv_loop(ws, stop_event):
    print('WebSocket recv loop started')
    ws.settimeout(1)
    try:
        while not stop_event.is_set():
            try:
                msg = ws.recv()
                if not msg:
                    continue
                print('WS MSG:', msg)
                data = None
                try:
                    data = json.loads(msg)
                except Exception:
                    pass
                if data and data.get('type') == 'assistant_delta' and data.get('final'):
                    print('Received final assistant_delta, stopping receive loop')
                    stop_event.set()
                    break
            except WebSocketTimeoutException:
                continue
            except Exception as e:
                print('WS recv error:', e)
                break
    finally:
        try:
            ws.close()
        except Exception:
            pass
        print('WebSocket recv loop ended')


BASE = 'http://localhost:8000'

print('Creating session...')
resp = requests.post(f'{BASE}/api/v1/chat/sessions', json={'title': 'WS Test Session'})
if resp.status_code not in (200, 201):
    print('Failed to create session:', resp.status_code, resp.text)
    sys.exit(1)
session = resp.json()
sid = session.get('id')
print('Session created id=', sid)

# Open websocket
ws_url = f'ws://localhost:8000/api/v1/chat/ws/sessions/{sid}'
print('Connecting websocket to', ws_url)
ws = create_connection(ws_url)
stop_event = threading.Event()
recv_t = threading.Thread(target=recv_loop, args=(ws, stop_event), daemon=True)
recv_t.start()

# Give websocket a moment
time.sleep(0.5)

print('Posting message to trigger AI response...')
post_resp = requests.post(f'{BASE}/api/v1/chat/sessions/{sid}/messages', data={'content': 'Please summarize: Patient shows elevated fasting glucose of 115 mg/dL and HbA1c 6.0%.'})
print('POST resp status', post_resp.status_code)
try:
    print('POST resp json:', post_resp.json())
except Exception as e:
    print('POST resp text:', post_resp.text)

# Wait up to 30s for streaming to finish
for i in range(30):
    if stop_event.is_set():
        break
    time.sleep(1)

print('Stopping test, cleaning up')
stop_event.set()
recv_t.join(timeout=2)
print('Done')
