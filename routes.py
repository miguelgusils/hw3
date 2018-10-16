#import libraries
from flask import Flask, flash, render_template, request, url_for, redirect, jsonify, session
from models import db, User, Post
from forms import LoginForm, SignupForm, NewpostForm
from passlib.hash import sha256_crypt
#import Heroku
## To run from Heroku ##
from flask_heroku import Heroku
#app = Flask(__name__)
#heroku = Heroku(app)

## To run Local ##
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/hw3_db'

app.secret_key = "cscie14a-hw3"
db.init_app(app)

#routes
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        session_user = User.query.filter_by(username=session['username']).first()
        posts = Post.query.filter_by(author=session_user.uid).all()
        return render_template('index.html', title='Home', posts=posts, session_username=session_user.username)
    else:
        all_posts = Post.query.all()
        return render_template('index.html', title='Home', posts=all_posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    form = LoginForm()
    print(request.method)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        check_pw = sha256_crypt.verify(password, user.password)
        if user is None or not check_pw:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            session['username'] = username
            return redirect(url_for('index'))
    else:
        return render_template('login.html', title='Login', form=form)

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    form = NewpostForm()
    if request.method == 'POST':
        session_user = User.query.filter_by(username=session['username']).first()
        content = request.form['content']
        new_post = Post(author=session_user.uid, content=content)
        db.session.add(new_post)
        db.session.commit()
        flash('Congratulations, you have added a new post!')
        return redirect(url_for('index'))
    else:
        return render_template('newpost.html', title='Newpost', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('index'))

    form = SignupForm()
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('The username already exists. Please pick another one.')
            return redirect(url_for('signup'))
        else:
            user = User(username=username, password=sha256_crypt.hash(password))
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
    else:
        return render_template('signup.html', title='Signup', form=form)




if __name__ == "__main__":
    app.run(debug=True)
