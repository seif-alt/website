from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import mysql.connector
app = mysql.connector.Connect(
    host="localhost",
    user="root",
    password=""
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update with your MySQL username
app.config['MYSQL_PASSWORD'] = ''  # Update with your MySQL password
app.config['MYSQL_DB'] = 'allmaindata'

mysql = MySQL(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return User(user[0], user[1]) if user else None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/profile')
@login_required
def profile():
    cursor = mysql.connection.cursor()
    
    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user = cursor.fetchone()
    
    # Fetch user's posts
    cursor.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC", (current_user.id,))
    posts = cursor.fetchall()

    return render_template('profile.html', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            return redirect('/mainhomepage')
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/home')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash('Registration successful! Please log in.')
            return redirect('/login')
        except Exception as e:
            mysql.connection.rollback()
            flash('Username already exists! Please choose another.')

    return render_template('signup.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        image = request.files['image']
        caption = request.form['caption']
        image_path = os.path.join('static/uploads', image.filename)
        image.save(image_path)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO posts (user_id, image_url, caption) VALUES (%s, %s, %s)",
                       (current_user.id, image_path, caption))
        mysql.connection.commit()
        flash('Post uploaded successfully!')
        return redirect('/mainhomepage')
    return render_template('upload.html')

@app.route('/mainhomepage', methods=['GET', 'POST'])
def mainhomepage():
    cursor = mysql.connection.cursor()

    # Handle new post submission
    if request.method == 'POST':
        image = request.files['image']
        caption = request.form['caption']
        image_path = os.path.join('static/uploads', image.filename)
        image.save(image_path)

        cursor.execute("INSERT INTO posts (user_id, image_url, caption) VALUES (%s, %s, %s)",
                       (current_user.id, image_path, caption))
        mysql.connection.commit()
        flash('Post uploaded successfully!')

    # Fetch all posts
    cursor.execute("SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id ORDER BY created_at DESC")
    posts = cursor.fetchall()
    return render_template('mainhomepage.html', posts=posts)

@app.route('/homepageasguest')
def homepageasguest():
    return render_template('homepageasguest.html')

if __name__ == '__main__':
    app.run(debug=True)
