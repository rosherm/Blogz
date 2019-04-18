from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    title_error = ""
    entry_error = ""
    if request.method == 'POST':
        title_name = request.form['title']
        entry = request.form['entry']

        
        if not title_name:
            title_error = "Error: Title Needed!"

        if not entry:
            entry_error = "Error: Body Needed!"

        if entry_error or title_error:
            return render_template('newpost.html', title_name = title_name, entry = entry, title_error = title_error, entry_error = entry_error)
       
        blog_post = Blog(title_name, entry)
        db.session.add(blog_post)
        db.session.commit()

        return redirect('/blog?id='+ str(blog_post.id))
  
    return render_template('newpost.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    AllBlogs = Blog.query.all()

    idlink = request.args.get("id")

    if idlink:
        singleblog = Blog.query.filter_by(id = int(idlink)).first()
        singlebloglist = [singleblog]
        return render_template('blog.html', AllBlogs = singlebloglist)

    return render_template('blog.html', AllBlogs = AllBlogs, title = "Build A Blog")



if __name__ == '__main__':
    app.run()