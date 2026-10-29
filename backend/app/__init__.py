from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # 配置数据库连接（优先读取 .env 中的 DATABASE_URL，默认使用本地 SQLite）
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///outdoor_events.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    # 初始化 DB
    db.init_app(app)

    # 自动创建数据库表
    with app.app_context():
        from . import models  # 导入模型文件
        db.create_all()  # 在本地生成 SQLite 数据库文件

    return app