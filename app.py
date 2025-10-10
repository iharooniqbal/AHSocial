from flask import Flask, render_template, request, redirect, url_for, flash
import os, json, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'change-this-secret-for-production'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
POSTS_DB = os.path.join('static', 'posts.json')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov', 'avi'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_posts():
    try:
        with open(POSTS_DB, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_posts(posts):
    with open(POSTS_DB, 'w') as f:
        json.dump(posts, f, indent=2)

# --- Routes ---
@app.route('/')
def index():
    posts = list(reversed(load_posts()))
    return render_template('index.html', posts=posts)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        caption = request.form.get('caption', '')
        file = request.files.get('media')

        if not file or file.filename == '':
            flash('Please choose a file')
            return redirect(url_for('upload'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(save_path)

            posts = load_posts()
            posts.append({
                "filename": unique_name,
                "caption": caption
            })
            save_posts(posts)
            flash('Upload successful!')
            return redirect(url_for('index'))
        else:
            flash('File type not allowed')
            return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/explore')
def explore():
    posts = load_posts()
    return render_template('explore.html', posts=posts)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        flash('Feedback received! Thank you.')
        return redirect(url_for('feedback'))
    return render_template('feedback.html')

@app.route('/profile')
def profile():
    posts = load_posts()
    return render_template('profile.html', posts=posts)

# --- Main ---
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    if not os.path.exists(POSTS_DB):
        with open(POSTS_DB, 'w') as f:
            json.dump([], f)
    app.run(debug=True)