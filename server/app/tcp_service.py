import socket, threading, json, time, logging
from logging.handlers import RotatingFileHandler
from flask import current_app

# ========== 配置 ==========
TCP_PORT = current_app.config['TCP_PORT']
TIMEOUT_SECONDS = current_app.config['TIMEOUT_SECONDS']
clients = {}  # device_id -> conn
runtime_logs = []  # 仅本次运行期间的日志

log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
log_handler = RotatingFileHandler('logs/tcp_serial_proxy.log', maxBytes=1_000_000, backupCount=3)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger('tcp_serial_proxy')
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


def log_runtime(level, message):
    log_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{level.upper()}] {message}"
    runtime_logs.append(log_entry)
    getattr(logger, level)(message)


class TCPServerThread(threading.Thread):
    _instance = None

    def __init__(self, host='0.0.0.0', port=TCP_PORT):
        if TCPServerThread._instance:
            raise RuntimeError("TCPServerThread is already running")
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        TCPServerThread._instance = self

    def run(self):
        logger.info(f"[TCP] 启动 TCP 监听 {self.port}")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
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
                    log_runtime('warning', f"连接超时断开：{addr}")
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
                        log_runtime('info', f"设备注册：{device_id} 来自 {addr}")

                    elif msg['type'] == 'data':
                        target = msg['to']
                        if target in clients:
                            print(f"[转发] {msg['from']} -> {target}: {msg['payload']}")
                            clients[target].sendall(json.dumps(msg).encode())
                            logger.info("消息转发成功：%s", msg['payload'])
                            log_runtime('info', f"消息转发成功：{msg['from']} -> {target}: {msg['payload']}")
                        else:
                            print(f"[警告] 目标设备 {target} 未注册")
                            logger.warning("目标未注册：%s", target)
                            log_runtime('warning', f"目标未注册：{target}")

                except json.JSONDecodeError:
                    print("[错误] JSON 解析失败")
                    logger.error("JSON 解析失败，来自 %s", addr)
                    log_runtime('error', f"JSON 解析失败，来自 {addr}")

        finally:
            if device_id and device_id in clients:
                del clients[device_id]
                print(f"[断开] {device_id} 已断开连接")
                logger.warning("设备断开：%s", device_id)
                log_runtime('warning', f"设备断开：{device_id}")
            conn.close()
