from flask import Flask, render_template, request, redirect, url_for, flash, session
import os, json, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'change-this-secret-for-production'

from datetime import timedelta

app.permanent_session_lifetime = timedelta(days=30)  # keep login for 30 days


# --- Paths ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
POSTS_DB = os.path.join('static', 'posts.json')
USERS_DB = os.path.join('static', 'users.json')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov', 'avi'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Ensure folders & files exist ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
for f in [POSTS_DB, USERS_DB]:
    if not os.path.exists(f):
        with open(f, 'w') as j:
            json.dump([], j, indent=2)

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_posts():
    return load_json(POSTS_DB)


# --- Routes ---

@app.route('/')
def index():
    posts = list(reversed(load_posts()))
    user = session.get('user')
    return render_template('index.html', posts=posts, user=user)


# --- Auth ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        users = load_json(USERS_DB)

        # Check if user exists
        for u in users:
            if u['username'] == username or u['email'] == email:
                flash('Username or email already exists in HAR NECT!')
                return redirect(url_for('signup'))

        users.append({'username': username, 'email': email, 'password': password})
        save_json(USERS_DB, users)
        flash('Signup successful! You can now login to HAR NECT.')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_json(USERS_DB)
        for u in users:
            if (u['username'] == username or u['email'] == username) and u['password'] == password:
                session.permanent = True  # 👈 this line makes the session last longer
                session['user'] = u['username']
                flash('Login successful! Welcome to HAR NECT.')
                return redirect(url_for('index'))

        flash('Invalid username or password for HAR NECT.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully from HAR NECT.')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        flash('Please login first to HAR NECT.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        caption = request.form.get('caption', '')
        file = request.files.get('media')

        if not file or file.filename == '':
            flash('Please choose a file to upload to HAR NECT')
            return redirect(url_for('upload'))

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(save_path)

            posts = load_json(POSTS_DB)
            posts.append({
                "filename": unique_name,
                "caption": caption,
                "user": session['user'],
                "likes": [],
                "comments": []
            })

            save_json(POSTS_DB, posts)
            flash('Upload successful to HAR NECT!')
            return redirect(url_for('index'))
        else:
            flash('File type not allowed in HAR NECT')
            return redirect(url_for('upload'))

    return render_template('upload.html')


# --- Likes ---
@app.route('/like/<filename>', methods=['POST'])
def like_post(filename):
    if 'user' not in session:
        flash("Please login first to HAR NECT.")
        return redirect(url_for('login'))

    posts = load_json(POSTS_DB)
    for post in posts:
        if post['filename'] == filename:
            user = session['user']
            if user in post.get('likes', []):
                post['likes'].remove(user)  # Unlike
            else:
                post.setdefault('likes', []).append(user)
            save_json(POSTS_DB, posts)
            break

    return redirect(url_for('index'))


# --- Comments ---
@app.route('/comment/<filename>', methods=['POST'])
def comment_post(filename):
    if 'user' not in session:
        flash("Please login first to HAR NECT.")
        return redirect(url_for('login'))

    comment = request.form.get('comment', '').strip()
    if not comment:
        flash("Comment cannot be empty in HAR NECT.")
        return redirect(url_for('index'))

    posts = load_json(POSTS_DB)
    for post in posts:
        if post['filename'] == filename:
            post.setdefault('comments', []).append({
                "user": session['user'],
                "text": comment
            })
            save_json(POSTS_DB, posts)
            break

    return redirect(url_for('index'))


# --- Other Pages ---
@app.route('/explore')
def explore():
    posts = list(reversed(load_posts()))
    user = session.get('user', None)
    return render_template('explore.html', posts=posts, user=user)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        flash('Feedback received! Thank you for contributing to HAR NECT.')
        return redirect(url_for('feedback'))
    return render_template('feedback.html')


@app.route('/profile')
def profile():
    user = session.get('user', None)
    posts = [p for p in load_posts() if p.get('user') == user] if user else []
    return render_template('profile.html', posts=posts, user=user)


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
