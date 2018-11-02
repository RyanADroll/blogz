from flask import Flask, redirect, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:wrangler@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = "abcdefghijklmnopqrstuvwxyz"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')

def index():
    users = User.query.all()
    return render_template('index.html', users = users)


@app.route('/login', methods = ['POST', 'GET'])

def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Log in successful.')
            return redirect('/newpost')
        elif not user:
            flash("No record of username", 'error')
        else: 
            flash("Incorrect password", 'error')

    return render_template('login.html')


@app.route('/signup', methods = ['POST', 'GET'])

def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        current_user = User.query.filter_by(username = username).first()

        if current_user:
            flash('Username already in use', 'error')
        elif not username or not password or not verify:
            flash('Fill out all fields', 'error')
        elif password != verify:
            flash('Passwords do not match', 'error')
        elif len(password) < 3 or len(username) < 3:
            flash(' username or password incorrect', 'error')
        else: 
            new_user = User(username, password)
            session['username'] = username
            db.session.add(new_user)
            db.session.commit()
            return redirect('/newpost')

    return render_template('signup.html')


@app.route('/logout')

def logout():

    del session['username']
    return redirect('/')


@app.route('/blog', methods = ['POST', 'GET'])

def blog():

    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('display-post.html', title = post.title, post = post)

    if user_id:
        posts = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('singleuser.html', posts = posts)

    return render_template('blog.html', title = "Blogs", posts = Blog.query.all())


@app.route('/newpost', methods = ['POST', 'GET'])

def add_blog():

    username = session['username']
    owner = User.query.filter_by(username = username).first()
    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        if (not new_post_title) or (not new_post_body):
            error = "You done goofed, please fill out both feilds"
            return render_template('add-blog.html', post_title = new_post_title, post_body = new_post_body, error = error)
        else:
            post = Blog(new_post_title, new_post_body, owner)
            db.session.add(post)
            db.session.commit()
            return redirect('/blog?id='+str(post.id))
    return render_template('add-blog.html', title = 'Add Blog', owner = owner)


if __name__ == '__main__':
    app.run()