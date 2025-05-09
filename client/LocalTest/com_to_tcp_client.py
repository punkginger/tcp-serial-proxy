import socket
import serial
import json
import time
import threading
import yaml

# 读取config
with open("../config_sender.yml", "r") as f:
    cfg = yaml.safe_load(f)

DEVICE_ID = cfg["device"]["device_id"]
TARGET_ID = cfg["device"]["target_id"]
COM_PORT = cfg["serial"]["com_port"]
BAUDRATE = cfg["serial"]["baudrate"]
SERVER_IP = cfg["server"]["ip"]
SERVER_PORT = cfg["server"]["port"]

def send_thread(ser, sock):
    while True:
        data = ser.readline()
        if data:
            text = data.decode(errors='ignore').strip()
            payload = {
                "type": "data",
                "from": DEVICE_ID,
                "to": TARGET_ID,
                "payload": text
            }
            try:
                sock.sendall(json.dumps(payload).encode())
                print(f"[发送] {text}")
            except:
                print("[错误] 发送失败")
        time.sleep(0.1)


def recv_thread(ser, sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            msg = json.loads(data.decode())
            if msg['type'] == 'data' and msg['to'] == DEVICE_ID:
                payload = msg['payload']
                print(f"[接收] 来自 {msg['from']}: {payload}")
                ser.write((payload + '\n').encode())
        except:
            print("[错误] 接收失败")
            break


def main():
    ser = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    # 注册设备
    register_msg = json.dumps({"type": "register", "device_id": DEVICE_ID})
    sock.sendall(register_msg.encode())
    print("[注册] 已连接并注册到服务器")

    # 启动双线程
    threading.Thread(target=send_thread, args=(ser, sock), daemon=True).start()
    threading.Thread(target=recv_thread, args=(ser, sock), daemon=True).start()

    # 防止主线程退出
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
