import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if os.path.exists("env.py"):
   import env

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'gameDB'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)


@app.route('/')
@app.route('/home_page')
def home_page():
    return render_template('index.html')

@app.route('/games')
def games():
    return render_template('games.html', games=mongo.db.games.find())

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)