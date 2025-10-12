from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'change-this-secret-for-production'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# In-memory "database"
# -------------------------
users = {}  # username -> {password, bio, profile_pic, email, followers, following}
posts = []  # list of posts: {filename, user, caption, likes:[users], comments:[{user,text}], type: 'story' or 'post'}

# -------------------------
# AUTH ROUTES
# -------------------------
@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users and users[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        e = request.form['email']
        p = request.form['password']
        if u in users:
            return render_template('signup.html', error='Username already exists')
        users[u] = {
            'password': p,
            'bio': '',
            'profile_pic': 'user.png',
            'email': e,
            'followers': set(),
            'following': set()
        }
        session['user'] = u
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# -------------------------
# MAIN ROUTES
# -------------------------
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    story_posts = [p for p in posts if p['type'] == 'story']
    feed_posts = [p for p in posts if p['type'] == 'post']
    return render_template('index.html', user=session['user'], posts=feed_posts, stories=story_posts)

@app.route('/explore')
def explore():
    query = request.args.get('query', '')
    results = []
    for u, data in users.items():
        if query.lower() in u.lower():
            results.append({'type':'user','username':u})
    for p in posts:
        if query.lower() in p.get('caption','').lower() and p['type']=='post':
            results.append({'type':'post','user':p['user'],'filename':p['filename'],'caption':p.get('caption')})
    return render_template('explore.html', user=session.get('user'), posts=posts, results=results, query=query)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        f = request.files.get('media')
        if not f:
            return "No file selected", 400
        filename = str(uuid.uuid4()) + '_' + secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
        caption = request.form.get('caption', '')
        is_story = 'is_story' in request.form
        posts.append({
            'filename': filename,
            'user': session['user'],
            'caption': caption,
            'likes': [],
            'comments': [],
            'type': 'story' if is_story else 'post'
        })
        return redirect(url_for('index'))
    return render_template('upload.html', user=session.get('user'))

@app.route('/profile/<username>', methods=['GET','POST'])
def profile(username):
    if username not in users:
        return "User not found", 404
    user_data = users[username]
    if request.method == 'POST' and session.get('user') == username:
        new_username = request.form.get('username')
        bio = request.form.get('bio')
        profile_pic_file = request.files.get('profile_pic')
        if new_username and new_username != username:
            users[new_username] = users.pop(username)
            session['user'] = new_username
            username = new_username
        if bio is not None:
            users[username]['bio'] = bio
        if profile_pic_file:
            filename = str(uuid.uuid4()) + '_' + secure_filename(profile_pic_file.filename)
            profile_pic_file.save(os.path.join(UPLOAD_FOLDER, filename))
            users[username]['profile_pic'] = filename
        return redirect(url_for('profile', username=username))
    user_posts = [p for p in posts if p['user']==username]
    return render_template('profile.html', user=session.get('user'), profile_user=username, user_data=user_data, posts=user_posts)

# -------------------------
# AJAX ROUTES
# -------------------------
@app.route('/like_post/<filename>', methods=['POST'])
def like_post(filename):
    u = session.get('user')
    if not u:
        return jsonify({'error':'Not logged in'}), 401
    for p in posts:
        if p['filename']==filename:
            if u in p['likes']:
                p['likes'].remove(u)
                liked=False
            else:
                p['likes'].append(u)
                liked=True
            return jsonify({'liked': liked, 'likes': len(p['likes'])})
    return jsonify({'error':'Post not found'}), 404

@app.route('/comment_post/<filename>', methods=['POST'])
def comment_post(filename):
    u = session.get('user')
    if not u:
        return jsonify({'error':'Not logged in'}), 401
    data = request.get_json()
    text = data.get('comment')
    if not text:
        return jsonify({'error':'Empty comment'}), 400
    for p in posts:
        if p['filename']==filename:
            p['comments'].append({'user':u,'text':text})
            return jsonify({'comments': p['comments']})
    return jsonify({'error':'Post not found'}), 404

@app.route('/delete_post/<filename>', methods=['POST'])
def delete_post(filename):
    u = session.get('user')
    for p in posts:
        if p['filename']==filename and p['user']==u:
            posts.remove(p)
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, filename))
            except:
                pass
            return jsonify({'success':True})
    return jsonify({'error':'Not allowed or post not found'}), 403

# -------------------------
# FOLLOW / UNFOLLOW
# -------------------------
@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    current_user = session.get('user')
    if not current_user:
        return jsonify({'error':'Not logged in'}), 401
    if username not in users:
        return jsonify({'error':'User not found'}), 404
    if username == current_user:
        return jsonify({'error':'Cannot follow yourself'}), 400

    if current_user in users[username]['followers']:
        # Unfollow
        users[username]['followers'].remove(current_user)
        users[current_user]['following'].remove(username)
        action = 'unfollowed'
    else:
        # Follow
        users[username]['followers'].add(current_user)
        users[current_user]['following'].add(username)
        action = 'followed'

    return jsonify({
        'action': action,
        'followers_count': len(users[username]['followers'])
    })

# -------------------------
# Feedback
# -------------------------
feedbacks = []
@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if request.method=='POST':
        data = request.get_json()
        name = data.get('name','Anonymous')
        message = data.get('message','')
        if message.strip():
            feedbacks.append({'name': name, 'message': message})
        return jsonify(feedbacks)
    return render_template('feedback.html', user=session.get('user'), feedbacks=feedbacks)

if __name__=="__main__":
    app.run(debug=True)
