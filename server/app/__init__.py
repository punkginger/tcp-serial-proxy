from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__, static_folder='../static')

    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # 注册蓝图
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    from app.views.tcp import tcp_bp
    app.register_blueprint(tcp_bp, url_prefix='/api')

    return app
