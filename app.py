import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, flash, render_template,\
    redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

if os.path.exists("env.py"):
    import env
    app.config["MONGO_URI"] = env.MONGO_URI
    app.config['SECRET_KEY'] = env.SECRET_KEY
else:
    app.config["MONGO_URI"] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


app.config['MONGO_DBNAME'] = 'gameDB'


mongo = PyMongo(app)


""" converts users regular youtube
link to embeded link to display in iframe """


def convert_embed(trailer_link):
    new_url = trailer_link.replace("watch?v=", "embed/")
    trailer_link = new_url

    return trailer_link


""" Custom 500 error page
(used for error with search function
outlined in readme) """


@app.errorhandler(500)
def internal_error(error):
    flash('Please fill out all fields')
    return render_template('games.html',
                           genre=mongo.db.genre.find(),
                           games=mongo.db.games.find(),
                           age_rating=mongo.db.age_rating.find(),
                           dev=mongo.db.developer.find(),
                           plat=mongo.db.platform.find(),
                           vr=mongo.db.vr_capable.find()), 500


""" Route for home page """


@app.route('/')
@app.route('/home_page')
def home_page():
    return render_template('index.html', is_index=True)


""" route for about page """


@app.route('/about')
def about():
    return render_template('about.html', game=mongo.db.games.find())


""" route for games page displays games image and title.
    provides a link to the individual games page and a search function """


@app.route('/games', methods=['POST', 'GET'])
def games():

    return render_template('games.html',
                           genre=mongo.db.genre.find(),
                           games=mongo.db.games.find(),
                           age_rating=mongo.db.age_rating.find(),
                           dev=mongo.db.developer.find(),
                           plat=mongo.db.platform.find(),
                           vr=mongo.db.vr_capable.find())


""" Route for search function from games page
    Search based on certain criteria
    and uses regular expression and ignores case
    if no results found returns to games page and displays message to user """


@app.route('/search')
def search():

    games = mongo.db.games
    query = {"title": {'$regex': request.args.get('search', ''),
             '$options': 'i'}}
    if request.args.get('genre'):
        query['genre_name'] = {'$regex': request.args.get('genre'),
                               '$options': 'i'}
    if request.args.get('age'):
        query['age_rating'] = {'$regex': request.args.get('age'),
                               '$options': 'i'}
    if request.args.get('platform'):
        query['platform'] = {'$regex': request.args.get('platform'),
                             '$options': 'i'}
    if request.args.get('developer'):
        query['developer'] = {'$regex': request.args.get('developer'),
                              '$options': 'i'}
    print(query)
    result = games.find(query)
    if result.count() <= 0:
        flash('No results found, please try again')

    return render_template('games.html',
                           genre=mongo.db.genre.find(),
                           games=result,
                           age_rating=mongo.db.age_rating.find(),
                           dev=mongo.db.developer.find(),
                           plat=mongo.db.platform.find(),
                           vr=mongo.db.vr_capable.find())


""" Route to display info about the game chosen from games page """


@app.route('/games/<game_id>')
def game_page(game_id):
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('game.html',
                           genre=mongo.db.genre.find(),
                           game=the_game,
                           games=mongo.db.games.find(),
                           is_game_page=True)


""" Route for login page
    returns user to home page if already logged in
    Takes username from form and checks against database
    takes password from form and checks against database(uses password hashing)
    if either username or password is wrong displays message to user """


@app.route('/login', methods=['POST', 'GET'])
def login():

    if 'username' in session:
        flash('you are already logged in')
        return redirect(url_for('home_page'))

    if request.method == 'POST':
        users = mongo.db.users
        user_login = users.find_one({'name': request.form.get('username')})

        if user_login:
            if check_password_hash(user_login['password'],
                                   request.form.get('password')):
                session['username'] = request.form.get('username')
                flash('Welcome back ' + session['username'])
                return redirect(url_for('home_page'))
            flash('Invalid credentials')
    return render_template('login.html', is_index=True)


""" Route for signup
    takes username from form and checks if user
    already exists in database to stop duplication of users
    takes password from form, hashes for security
    if successfull logs user in and displays success message
    and redirects to home page
    otherwise if username is taken displays message to user to try again"""


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form.get('username')})

        if not existing_user:
            hashpw = generate_password_hash(request.form.get('password'))
            users.insert_one({'name': request.form.get('username'),
                             'password': hashpw})
            session['username'] = request.form.get('username')
            flash('You have registered and been logged in as ' +
                  session['username'])
            return redirect(url_for('home_page'))
        flash('That username already exists, please try again')

    return render_template('signup.html', is_index=True)


""" Route for logout, clears session to remove login
displays message and redirects to home page """


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out, Goodbye')
    return redirect(url_for('home_page'))


""" Route for add game page which displays a form to take user input
    about the game, but only if the user is logged in """


@app.route('/add_game')
def add_game():
    if 'username' in session:
        return render_template('add_game.html',
                               genre=mongo.db.genre.find(),
                               platform=mongo.db.platform.find(),
                               vr=mongo.db.vr_capable.find(),
                               age_rating=mongo.db.age_rating.find(),
                               add_game=True)
    else:
        flash('You need to be logged in to add a game')
        return redirect(url_for('login'))


""" Route to insert game into Database based on form input on add game page
    checks if title already exists to stop duplicate games
    checks if developer entered already exists
    if not add it to developer collectio
    for search function(**case sensitive**)
    adds game to database and displays confirm message to user """


@app.route('/insert_game', methods=['POST'])
def insert_game():
    dev_col = mongo.db.developer
    add_game_form = request.form.to_dict()
    title = add_game_form['title']
    add_game_form['trailer_link'] = \
        convert_embed(add_game_form['trailer_link'])
    game = mongo.db.games
    existing_title = game.find_one({'title': request.form.get('title')})
    existing_dev = dev_col.find_one({'dev': request.form.get('developer')})
    add_game_form.update({'username': session['username']})

    if existing_title:
        flash('This game already exists in the database')
    elif existing_dev:
        game.insert(add_game_form)
        flash("Thank you, " + title + " has been added to the database :)")
    elif not existing_dev:
        dev_col.insert_one({'dev': add_game_form['developer']})
        game.insert(add_game_form)
        flash("Thank you, " + title + " has been added to the database :)")
    else:
        flash('An unexpected error has occured, please try again')
    return redirect(url_for('games'))


""" Route for edit game
    takes game id to target specific game
    if not logged in redirect to login page """


@app.route('/edit_game/<game_id>')
def edit_game(game_id):
    if 'username' not in session:
        flash('You need to login to edit a game')
        return redirect(url_for('login'))
    the_game = mongo.db.games.find_one({'_id': ObjectId(game_id)})
    return render_template('edit_game.html',
                           game=the_game, genre=mongo.db.genre.find(),
                           platform=mongo.db.platform.find(),
                           vr=mongo.db.vr_capable.find(),
                           age_rating=mongo.db.age_rating.find(),
                           add_game=True)


""" Route to update game based on edit game form
    uses convert_embed function
    if successful displays message to user """


@app.route('/update_game/<game_id>', methods=['POST'])
def update_game(game_id):
    game = mongo.db.games
    title = request.form.get('title')
    add_game_form = request.form.to_dict()
    add_game_form['trailer_link'] =\
        convert_embed(add_game_form['trailer_link'])
    game.update_one({'_id': ObjectId(game_id)},

                    {
                    "$set":
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
                        'playthrough_time':
                        request.form.get('playthrough_time'),
                        'vr_capable': request.form.get('vr_capable')
                    }})

    flash(title + ' has been updated')
    return redirect(url_for('games'))


""" Route to delete game
    user has to be logged in
    sends success message to user """


@app.route('/delete_game/<game_id>')
def delete_game(game_id):
    if 'username' not in session:
        flash('You need to be logged in to delete a game')
        return redirect(url_for('login'))
    game = mongo.db.games
    flash('The Game has been deleted')
    game.delete_one({'_id': ObjectId(game_id)})
    return redirect(url_for('games'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)
