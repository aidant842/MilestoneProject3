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
    return render_template('games.html', genre=mongo.db.genre.find(), games=mongo.db.games.find(),
                            age_rating=mongo.db.age_rating.find(), dev=mongo.db.developer.find(), plat=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find())

@app.route('/games/<game_id>')
def game_page(game_id):
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('game.html', genre=mongo.db.genre.find(), game=the_game, games=mongo.db.games.find())

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/addGame')
def addGame():
    return render_template('addGame.html', genre=mongo.db.genre.find(), platform=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find(), age_rating=mongo.db.age_rating.find())

@app.route('/insert_game', methods = ['POST'])  
def insert_game():
    game = mongo.db.games
    game.insert(request.form.to_dict(), {'complete': 'false'})
    return redirect(url_for('games')) 

@app.route('/edit_game/<game_id>')
def edit_game(game_id):
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('edit_game.html', game=the_game, genre=mongo.db.genre.find(), platform=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find(), age_rating=mongo.db.age_rating.find())                             

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)