import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
login = LoginManager()
login.init_app(app)
login.LOGIN_URL='/login'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True 

# 创建bootstrap对象
bootstrap = Bootstrap(app)

from app import views, models

