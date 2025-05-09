import os
import yaml


class Config:
    base_dir = os.path.dirname(__file__)  # 获取 config.py 所在目录
    path = os.path.join(base_dir, 'config_server.yml')  # 构造完整路径
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    SQLALCHEMY_DATABASE_URI = config['mysql']['uri']
    JWT_SECRET_KEY = config['jwt_secret_key']
    TCP_PORT = config['tcp']['port']
    TIMEOUT_SECONDS = config['tcp']['timeout_seconds']

