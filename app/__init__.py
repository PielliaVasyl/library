__author__ = 'Piellia Vasyl'
from flask import Flask

app = Flask(__name__)
from app import views
