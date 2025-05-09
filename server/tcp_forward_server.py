import socket
import threading
import json
import logging
from logging.handlers import RotatingFileHandler

# ========== 配置 ==========
TCP_PORT = 6006
TIMEOUT_SECONDS = 300  # 5分钟超时
clients = {}  # device_id -> conn

# ========== 日志设置 ==========
log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
log_handler = RotatingFileHandler('logs/tcp_serial_proxy.log', maxBytes=1_000_000, backupCount=3)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger('logs/tcp_serial_proxy')
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


def handle_client(conn, addr):
    device_id = None
    conn.settimeout(TIMEOUT_SECONDS)  # 设置空闲超时

    try:
        while True:
            try:
                raw = conn.recv(4096)
                if not raw:
                    break
            except socket.timeout:
                print(f"[超时] 连接 {addr} 超过 {TIMEOUT_SECONDS} 秒无响应，自动断开")
                logger.warning("连接超时断开：%s", addr)
                break

            try:
                msg = json.loads(raw.decode())

                # "type": "data",
                # "from": DEVICE_ID,
                # "to": TARGET_ID,
                # "payload": text

                # "type": "register",
                # "device_id": DEVICE_ID

                if msg['type'] == 'register':
                    device_id = msg['device_id']
                    clients[device_id] = conn
                    print(f"[注册] {device_id} 注册自 {addr}")
                    logger.info("设备注册：%s 来自 %s", device_id, addr)

                elif msg['type'] == 'data':
                    target = msg['to']
                    if target in clients:
                        print(f"[转发] {msg['from']} -> {target}: {msg['payload']}")
                        clients[target].sendall(json.dumps(msg).encode())
                        logger.info("消息转发成功：%s", msg['payload'])
                    else:
                        print(f"[警告] 目标设备 {target} 未注册")
                        logger.warning("目标未注册：%s", target)

            except json.JSONDecodeError:
                print("[错误] JSON 解析失败")
                logger.error("JSON 解析失败，来自 %s", addr)

    finally:
        if device_id and device_id in clients:
            del clients[device_id]
            print(f"[断开] {device_id} 已断开连接")
            logger.warning("设备断开：%s", device_id)
        conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', TCP_PORT))
    server.listen()
    print(f"[服务器] TCP 服务器监听中，端口 {TCP_PORT}...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == '__main__':
    main()
