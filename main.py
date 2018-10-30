from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:wrangler@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def index():
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id = int(blog_id)).first()
        return render_template('blog.html', title = blog.title, blog=blog)
    blogs = Blog.query.all()
    return render_template('index.html',title='Blogs', blogs = blogs)

@app.route('/newpost', methods = ['GET','POST'])
def post():
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        title_error = ''
        body_error = ''
    
        if title == '' or body == '':
            if title == '':
                title_error = 'title required'

            if body == '':
                body_error = 'Insert text into field'

            return render_template('addnewpost.html', title="New Post", blog_title = title, title_error = title_error, body = body, body_error = body_error)
            
        else:
            blog = Blog(title, body)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id='+str(blog.id))

    return render_template('addnewpost.html', title="New Post")

if __name__ == '__main__':
    app.run()