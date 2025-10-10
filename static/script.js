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

console.log("main.js loaded");


function toggleLike(btn) {
  if (btn.classList.contains('liked')) {
    btn.classList.remove('liked');
    btn.textContent = '❤️ Like';
  } else {
    btn.classList.add('liked');
    btn.textContent = '💖 Liked';
  }
}

function toggleComment(id) {
  const section = document.getElementById(`comment-${id}`);
  if (section.style.display === 'none') {
    section.style.display = 'block';
  } else {
    section.style.display = 'none';
  }
}

function sharePost(url) {
  navigator.clipboard.writeText(url);
  alert("Post link copied to clipboard!");
}
