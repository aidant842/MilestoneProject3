import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, flash, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from os import path
if os.path.exists("env.py"):
   import env


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'gameDB'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

mongo = PyMongo(app)


def convert_embed(trailer_link):
    new_url = trailer_link.replace("watch?v=", "embed/")
    trailer_link = new_url

    return trailer_link


@app.errorhandler(500)
def internal_error(error):
    flash('Please fill out all fields')
    return render_template('games.html', genre=mongo.db.genre.find(), games=mongo.db.games.find(),
                            age_rating=mongo.db.age_rating.find(), dev=mongo.db.developer.find(), plat=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find()), 500


@app.route('/')
@app.route('/home_page')
def home_page():
    return render_template('index.html', is_index=True)


@app.route('/about')
def about():
    return render_template('about.html', game=mongo.db.games.find())


@app.route('/games', methods=['POST', 'GET'])
def games():

    return render_template('games.html', genre=mongo.db.genre.find(), games=mongo.db.games.find(),
                            age_rating=mongo.db.age_rating.find(), dev=mongo.db.developer.find(), plat=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find())


@app.route('/search', methods=['POST', 'GET'])
def search():

    games = mongo.db.games
    query = {
        'genre_name': {'$regex': request.form.get('genre'), '$options': 'i'},
        'age_rating': {'$regex': request.form.get('age'), '$options': 'i'},
        'platform': {'$regex': request.form.get('platform'), '$options': 'i'},
        'developer': {'$regex': request.form.get('developer'), '$options': 'i'}
    }
    result = games.find(query)
    if result.count() <= 0:
        flash('No results found, please try again')

    return render_template('games.html', genre=mongo.db.genre.find(), games=result,
                            age_rating=mongo.db.age_rating.find(), dev=mongo.db.developer.find(), plat=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find())


@app.route('/games/<game_id>')
def game_page(game_id):
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('game.html', genre=mongo.db.genre.find(), game=the_game, games=mongo.db.games.find())


@app.route('/login', methods=['POST', 'GET'])
def login():

    if 'username' in session:
        flash('you are already logged in')
        return redirect(url_for('home_page'))

    if request.method == 'POST':
        users = mongo.db.users
        user_login = users.find_one({'name': request.form.get('username')})

        if user_login:
            if check_password_hash(user_login['password'], request.form.get('password')):
                session['username'] = request.form.get('username')
                flash('Welcome back ' + session['username'])
                return redirect(url_for('home_page'))
            flash('Invalid credentials')
    return render_template('login.html', is_index=True)


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form.get('username')})

        if not existing_user:
            hashpw = generate_password_hash(request.form.get('password'))
            users.insert_one({'name': request.form.get('username'), 'password': hashpw})
            session['username'] = request.form.get('username')
            flash('You have registered and been logged in as ' + session['username'])
            return redirect(url_for('home_page'))
        flash('That username already exists, please try again')

    return render_template('signup.html', is_index=True)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out, Goodbye')
    return redirect(url_for('home_page'))


@app.route('/addGame')
def addGame():
    if 'username' in session:
        return render_template('addGame.html', genre=mongo.db.genre.find(), platform=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find(), age_rating=mongo.db.age_rating.find(), add_game=True)
    else:
        flash('You need to be logged in to add a game')
        return redirect(url_for('login'))


@app.route('/insert_game', methods=['POST'])
def insert_game():
    dev_col = mongo.db.developer
    add_game_form = request.form.to_dict()
    title = add_game_form['title']
    add_game_form['trailer_link'] = convert_embed(add_game_form['trailer_link'])
    game = mongo.db.games
    existing_title = game.find_one({'title': request.form.get('title')})
    existing_dev = dev_col.find_one({'dev': request.form.get('developer')})

    if existing_title:
        flash('This game already exists in the database')
    elif existing_dev:
        game.insert_one(add_game_form)
        flash("Thank you, " + title + " has been added to the database :)")  
    elif not existing_dev:
        dev_col.insert_one({'dev': add_game_form['developer']})
        game.insert_one(add_game_form)
        flash("Thank you, " + title + " has been added to the database :)")
    else:
        flash('An unexpected error has occured, please try again')
    return redirect(url_for('games'))


@app.route('/edit_game/<game_id>')
def edit_game(game_id):
    if not 'username' in session:
        flash('You need to login to edit a game')
        return redirect(url_for('login'))
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('edit_game.html', game=the_game, genre=mongo.db.genre.find(), platform=mongo.db.platform.find(),
                            vr=mongo.db.vr_capable.find(), age_rating=mongo.db.age_rating.find(), add_game=True)


@app.route('/update_game/<game_id>', methods=['POST'])
def update_game(game_id):
    game = mongo.db.games
    title = request.form.get('title')
    add_game_form = request.form.to_dict()
    add_game_form['trailer_link'] = convert_embed(add_game_form['trailer_link'])
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
        'trailer_link': add_game_form['trailer_link'],
        'playthrough_time': request.form.get('playthrough_time'),
        'vr_capable': request.form.get('vr_capable')
    }})
    flash(title + ' has been updated')
    return redirect(url_for('games'))


@app.route('/delete_game/<game_id>')
def delete_game(game_id):
    if not 'username' in session:
        flash('You need to be logged in to delete a game')
        return redirect(url_for('login'))
    game = mongo.db.games
    flash('The Game has been deleted')
    game.delete_one({'_id': ObjectId(game_id)})
    return redirect(url_for('games'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)