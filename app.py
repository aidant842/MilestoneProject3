import os
from flask import Flask, flash, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if os.path.exists("env.py"):
   import env
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'gameDB'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

mongo = PyMongo(app)


def convert_embed(trailer_link):
    new_url = trailer_link.replace("watch?v=", "embed/")
    trailer_link = new_url

    return trailer_link



@app.route('/')
@app.route('/home_page')
def home_page():
    return render_template('index.html')

@app.route('/games', methods=['POST', 'GET'])
def games():

    return render_template('games.html', genre=mongo.db.genre.find(), games=mongo.db.games.find(),
                            age_rating=mongo.db.age_rating.find(), dev=mongo.db.developer.find(), plat=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find())

@app.route('/search', methods = ['POST', 'GET'])
def search():
    
    games = mongo.db.games
    query = games.find({
        'genre_name': request.form.get('genre')
    })

    return render_template('games.html', genre=mongo.db.genre.find(), games=query,
                            age_rating=mongo.db.age_rating.find(), dev=mongo.db.developer.find(), plat=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find())
    

@app.route('/games/<game_id>')
def game_page(game_id):
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('game.html', genre=mongo.db.genre.find(), game=the_game, games=mongo.db.games.find())

@app.route('/login', methods=['POST', 'GET'])
def login():

    if 'username' in session:
            return 'you are already logged in'
       
    if request.method == 'POST':
        users=mongo.db.users
        user_login = users.find_one({'name': request.form.get('username')})

        if user_login:
            if check_password_hash(user_login['password'], request.form.get('password')):
                session['username'] = request.form.get('username')
                flash('You are logged in')
                return redirect(url_for('home_page'))
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form.get('username')})

        if not existing_user:
            hashpw = generate_password_hash(request.form.get('password'))
            users.insert_one({'name': request.form.get('username'), 'password': hashpw})
            session['username'] = request.form.get('username')
            return redirect(url_for('home_page'))
        flash('that username already exists')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out')
    return render_template('index.html')

@app.route('/addGame')
def addGame():
    if 'username' in session:
        return render_template('addGame.html', genre=mongo.db.genre.find(), platform=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find(), age_rating=mongo.db.age_rating.find())
    else:
        flash('you need to be logged in to add a game')
        return redirect(url_for('home_page'))                        

@app.route('/insert_game', methods=['POST'])  
def insert_game():
    flash('game added to database')
    add_game_form = request.form.to_dict()
    add_game_form['trailer_link'] = convert_embed(add_game_form['trailer_link'])
    game = mongo.db.games
    game.insert_many([request.form.to_dict(), add_game_form])
    return redirect(url_for('games'))

@app.route('/edit_game/<game_id>')
def edit_game(game_id):
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('edit_game.html', game=the_game, genre=mongo.db.genre.find(), platform=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find(), age_rating=mongo.db.age_rating.find())

@app.route('/update_game/<game_id>', methods=['POST'])
def update_game(game_id):
    game = mongo.db.games
    game.update_one({'_id' : ObjectId(game_id)},
    
    {"$set": 
    {
        'title': request.form.get('title'),
        'genre_name': request.form.get('genre_name'),
        'description': request.form.get('description'),
        'shop_link': request.form.get('shop_link'),
        'review': request.form.get('review'),
        'age_rating': request.form.get('age_rating'),
        'image': request.form.get('image'),
        'platform': request.form.get('platform'),
        'release_date': request.form.get('release_date'),
        'languages': request.form.get('languages'),
        'developer': request.form.get('developer'),
        'trailer_link': request.form.get('trailer_link'),
        'playthrough_time': request.form.get('playthrough_time'),
        'vr_capable': request.form.get('vr_capable')
    }})

    flash('Game Edited')

    return redirect(url_for('games'))

@app.route('/delete_game/<game_id>')
def delete_game(game_id):
    game=mongo.db.games
    game.delete_one({'_id': ObjectId(game_id)})

    return redirect(url_for('games'))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)