from flask import Flask, render_template, request, redirect, url_for, flash, session
import os, json, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'change-this-secret-for-production'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
POSTS_DB = os.path.join('static', 'posts.json')
USERS_DB = os.path.join('static', 'users.json')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov', 'avi'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# --- Authentication ---
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
                flash('Username or email already exists!')
                return redirect(url_for('signup'))

        users.append({'username': username, 'email': email, 'password': password})
        save_json(USERS_DB, users)
        flash('Signup successful! You can now login.')
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
                session['user'] = u['username']
                flash('Login successful!')
                return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# --- Posts / Main ---
@app.route('/')
def index():
    posts = list(reversed(load_json(POSTS_DB)))
    user = session.get('user')
    return render_template('index.html', posts=posts, user=user)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        caption = request.form.get('caption', '')
        file = request.files.get('media')

        if not file or file.filename == '':
            flash('Please choose a file')
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
                "user": session['user']
            })
            save_json(POSTS_DB, posts)
            flash('Upload successful!')
            return redirect(url_for('index'))
        else:
            flash('File type not allowed')
            return redirect(url_for('upload'))

    return render_template('upload.html')

@app.route('/explore')
def explore():
    posts = load_json(POSTS_DB)
    user = session.get('user')
    return render_template('explore.html', posts=posts, user=user)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        flash('Feedback received! Thank you.')
        return redirect(url_for('feedback'))
    return render_template('feedback.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    posts = load_json(POSTS_DB)
    user_posts = [p for p in posts if p.get("user") == session['user']]
    return render_template('profile.html', posts=user_posts, user=session['user'])

# --- Run App ---
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    for f in [POSTS_DB, USERS_DB]:
        if not os.path.exists(f):
            with open(f, 'w') as j:
                json.dump([], j)
                # --- Ensure required files/folders exist ---
os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)

if not os.path.exists(os.path.join('static', 'posts.json')):
    with open(os.path.join('static', 'posts.json'), 'w') as f:
        json.dump([], f)

if not os.path.exists(os.path.join('static', 'users.json')):
    with open(os.path.join('static', 'users.json'), 'w') as f:
        json.dump([], f)

    app.run(debug=True)
