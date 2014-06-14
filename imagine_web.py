from flask import Flask
from flask import request
from flask import session

import imagine

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

database = SqliteDatabase(DATABASE)
