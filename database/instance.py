from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')  # remonte d'un cran
static_dir = os.path.join(base_dir, '..', 'static')

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/easyy/Developpement/Python/FAQIA/database/faqia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)