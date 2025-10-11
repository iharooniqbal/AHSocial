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

// Smooth Like toggle
function toggleLike(btn) {
  btn.classList.toggle('liked');
  if (btn.classList.contains('liked')) {
    btn.textContent = '💖 Liked';
    btn.style.transform = 'scale(1.2)';
    setTimeout(() => btn.style.transform = 'scale(1)', 200);
  } else {
    btn.textContent = '❤️ Like';
    btn.style.transform = 'scale(0.9)';
    setTimeout(() => btn.style.transform = 'scale(1)', 200);
  }
}

// Smooth Comment toggle
function toggleComment(id) {
  const section = document.getElementById(`comment-${id}`);
  if (!section) return;

  section.classList.toggle('show');
}

// Share post
function sharePost(url) {
  navigator.clipboard.writeText(url);
  alert("Post link copied to clipboard!");
}
