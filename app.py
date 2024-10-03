from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Miniit123$'
app.config['MYSQL_DB'] = 'flask_users'

db = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login if not logged in

class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='posts')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home_post'))
        else:
            flash('Login Unsuccessful. Please check your username and password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home_post():
    if request.method == 'POST':
        post_content = request.form['content']
        new_post = Post(content=post_content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')

    # Fetch all posts for the homepage
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes_count += 1
    db.session.commit()
    return {'success': True, 'likes': post.likes_count}

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
