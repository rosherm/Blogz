from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "G68iIG854"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        errorcount = 0
        error = ""
        error1 = ""
        error2 = ""
        error3 = ""

        existing_user = User.query.filter_by(username=username).first()

        if (not password) or (password.strip() == "") or " " in password or len(password) < 3 or len(password) > 20:
            error1 = "That's not a valid password"
            errorcount += 1
        
        if (not verify) or (verify.strip() == "") or verify != password:
            error2 = "That's not a valid verify password"
            errorcount += 1

        if (not username) or (username.strip() == "") or " " in username or len(username) < 3 or len(username) > 20:
            error = "That's not a valid username"
            errorcount += 1
            username = ""
            
        if existing_user:
            error3 = "Username already in use"
            errorcount += 1
        
        if errorcount is not 0:
            return render_template('signup.html', username = username, error = error, error1 = error1, error2=error2, error3=error3 )
        
        else:

            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            return redirect("/newpost")

    return  render_template('signup.html')
        


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    title_error = ""
    entry_error = ""
    if request.method == 'POST':
        title_name = request.form['title']
        entry = request.form['entry']
        user = User.query.filter_by(username = session['username']).first()
       
        if not title_name:
            title_error = "Error: Title Needed!"

        if not entry:
            entry_error = "Error: Body Needed!"

        if entry_error or title_error:
            return render_template('newpost.html', title_name = title_name, entry = entry, title_error = title_error, entry_error = entry_error)
       
     
        blog_post = Blog(title_name, entry, user)
        db.session.add(blog_post)
        db.session.commit()

   
        return redirect('/blog?id='+ str(blog_post.id) )
  
    return render_template('newpost.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    Allusers = User.query.all()

    idlink = request.args.get("id")

   
    if idlink:
        singleuser = User.query.filter_by(id = int(idlink)).first()
        singleuserlist = [singleuser]
        return render_template('blog.html', Allusers = singleuserlist)

    return render_template('index.html', Allusers = Allusers, title = "Blog Users!")

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    userlink = request.args.get("user")

    if userlink:
        username = User.query.filter_by(username = userlink).first()


       # blogs = Blog.query.filter_by(owner_id = userlink).all()
        return render_template('singleUser.html', AllBlogs = username.blogs, username= userlink)
  

    AllBlogs = Blog.query.all()

    idlink = request.args.get("id")

    if idlink:
        singleblog = Blog.query.filter_by(id = int(idlink)).first()
        singlebloglist = [singleblog]
        return render_template('blog.html', AllBlogs = singlebloglist)

    return render_template('blog.html', AllBlogs = AllBlogs, title = "Build A Blog")


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



if __name__ == '__main__':
    app.run()