document.addEventListener('DOMContentLoaded', () => {

  // ==========================
  // THEME TOGGLE
  // ==========================
  const themeToggle = document.getElementById('themeToggle');
  const body = document.body;

  if (localStorage.getItem('theme') === 'dark') {
      body.classList.add('dark');
      if (themeToggle) themeToggle.textContent = '☀️';
  }

  if (themeToggle) {
      themeToggle.addEventListener('click', () => {
          body.classList.toggle('dark');
          if (body.classList.contains('dark')) {
              themeToggle.textContent = '☀️';
              localStorage.setItem('theme', 'dark');
          } else {
              themeToggle.textContent = '🌙';
              localStorage.setItem('theme', 'light');
          }
      });
  }

  // ==========================
  // LIKE POST
  // ==========================
  window.likePost = function(event, filename, btn) {
      event.preventDefault();
      fetch(`/like_post/${filename}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
      })
      .then(res => res.json())
      .then(data => {
          if (data.error) return alert(data.error);
          if (data.liked) {
              btn.textContent = `💖 ${data.likes} Likes`;
              btn.classList.add('liked');
          } else {
              btn.textContent = `❤️ ${data.likes} Likes`;
              btn.classList.remove('liked');
          }
      })
      .catch(err => console.error(err));
  };

  // ==========================
  // SUBMIT COMMENT
  // ==========================
  window.submitComment = function(event, filename) {
      event.preventDefault();
      const form = event.target;
      const input = form.querySelector('input[name="comment"]');
      const text = input.value.trim();
      if (!text) return;

      fetch(`/comment_post/${filename}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ comment: text })
      })
      .then(res => res.json())
      .then(data => {
          if (data.error) return alert(data.error);

          const commentsDiv = document.getElementById(`comments-${filename}`);
          const p = document.createElement('p');
          const lastComment = data.comments[data.comments.length - 1];
          p.innerHTML = `<strong>@${lastComment.user}:</strong> ${lastComment.text}`;
          commentsDiv.appendChild(p);
          input.value = '';
      })
      .catch(err => console.error(err));
  };

  // ==========================
  // SHARE POST
  // ==========================
  window.sharePost = function(url) {
      navigator.clipboard.writeText(url)
          .then(() => alert('Post link copied to clipboard!'))
          .catch(err => console.error(err));
  };

  // ==========================
  // DELETE POST
  // ==========================
  window.deletePost = function(filename) {
      if (!confirm("Are you sure you want to delete this post?")) return;

      fetch(`/delete_post/${filename}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
      })
      .then(res => res.json())
      .then(data => {
          if (data.error) return alert(data.error);
          const el = document.getElementById(`post-${filename}`);
          if (el) el.remove();
      })
      .catch(err => console.error(err));
  };

  // ==========================
  // STORY MODAL
  // ==========================
  let storyTimeout;

  window.openStory = function(imgSrc, username){
      document.getElementById('storyImage').src = imgSrc;
      document.getElementById('storyUser').innerText = username;
      document.getElementById('storyModal').style.display = 'flex';

      let progress = document.getElementById('progressBar');
      progress.style.width = '0%';
      let width = 0;
      clearInterval(storyTimeout);

      storyTimeout = setInterval(()=>{
          if(width >= 100){
              closeStory();
          } else {
              width += 1;
              progress.style.width = width + '%';
          }
      }, 50);
  };

  window.closeStory = function(){
      clearInterval(storyTimeout);
      document.getElementById('storyModal').style.display = 'none';
  };

  // ==========================
  // FOLLOW / UNFOLLOW
  // ==========================
  window.toggleFollow = function(profileUser, btn) {
      fetch(`/follow/${profileUser}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
      })
      .then(res => res.json())
      .then(data => {
          if (data.error) return alert(data.error);

          if (data.action === 'followed') {
              btn.textContent = 'Unfollow';
          } else {
              btn.textContent = 'Follow';
          }

          const followersSpan = document.getElementById('followersCount');
          if (followersSpan) followersSpan.textContent = `${data.followers_count} followers`;
      })
      .catch(err => console.error(err));
  };

});