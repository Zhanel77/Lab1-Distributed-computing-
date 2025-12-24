import json
import socket
import time
import uuid
from datetime import datetime

SERVER_HOST = "52.91.37.181"   
SERVER_PORT = 5000

TIMEOUT_SEC = 2
MAX_RETRIES = 3

def rpc_call(method: str, params):
    request = {
        "request_id": str(uuid.uuid4()),
        "method": method,
        "params": params,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    payload = json.dumps(request).encode("utf-8")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
                c.settimeout(TIMEOUT_SEC)
                c.connect((SERVER_HOST, SERVER_PORT))
                c.sendall(payload)

                resp_raw = c.recv(4096).decode("utf-8", errors="replace")
                resp = json.loads(resp_raw)

                print(f"[OK] attempt={attempt} response={resp}")
                return resp

        except socket.timeout:
            print(f"[TIMEOUT] attempt={attempt} no response in {TIMEOUT_SEC}s -> retrying...")
        except ConnectionRefusedError:
            print(f"[REFUSED] attempt={attempt} connection refused -> retrying...")
        except Exception as e:
            print(f"[ERROR] attempt={attempt} {e} -> retrying...")

        time.sleep(0.3)

    print("[FAIL] All retries used. RPC failed.")
    return None

if __name__ == "__main__":

    rpc_call("add", {"a": 5, "b": 7})
