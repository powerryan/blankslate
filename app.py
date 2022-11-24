import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SECRET_KEY'] = 'YCeiu4894238TW6d7IBU289drt4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sqlite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_SECRET_KEY'] = 'YUyo675f679h2GH36RRew45rT'

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
@app.route('/<var>')
def home(var):
    return var

import routes

def getApp():
    return app

if __name__ == "__main__":
    app.run()
