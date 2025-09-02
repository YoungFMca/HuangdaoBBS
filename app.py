from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.jinja_env.auto_reload=True
app.config['TEMPLATES_AUTO_RELOAD']=True
db = SQLAlchemy(app)

# 上传目录
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 数据表
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    author = db.Column(db.String(20))
    time = db.Column(db.DateTime, default=datetime.now)
    image_filename = db.Column(db.String(200))  # 注意这里长度改长一点，20 不够

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.now)

# 首页
@app.route('/')
def index():
    posts = Post.query.order_by(Post.time.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/snake')
def snake():
    return render_template('snake.html')

# 发帖页面
@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']

        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename  # 存数据库时只存文件名

        # 存入数据库
        post = Post(
            title=title,
            content=content,
            author=author,
            image_filename=image_filename
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('new_post.html')

# 帖子详情+评论
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.time.asc()).all()
    if request.method == 'POST':
        content = request.form['content']
        comment = Comment(post_id=post_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post_id))
    return render_template('post_detail.html', post=post, comments=comments)
@app.route('/signup',methods=['POST','GET'])
def signup():
    return render_template('')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
