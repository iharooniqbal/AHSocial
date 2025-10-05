from flask import Flask, render_template, request, redirect, url_for, flash
import os, json

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "replace-with-a-random-secret"

POSTS_FILE = 'posts.json'

def load_posts():
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_posts(posts):
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

@app.route('/splash')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/explore')
def explore():
    posts = load_posts()
    return render_template('explore.html', posts=posts)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        image = request.form.get('image', '').strip()
        if not title or not image:
            flash('Please provide both title and image URL.')
            return redirect(url_for('upload'))

        posts = load_posts()
        posts.insert(0, {'title': title, 'image': image})
        save_posts(posts)
        return redirect(url_for('explore'))
    return render_template('upload.html')

@app.route('/profile')
def profile():
    posts = load_posts()
    return render_template('profile.html', posts=posts)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name', '')
        message = request.form.get('message', '')
        flash('Thanks for your feedback, {}'.format(name or 'friend'))
        return redirect(url_for('index'))
    return render_template('feedback.html')

if __name__ == '__main__':
    app.run(debug=True)
