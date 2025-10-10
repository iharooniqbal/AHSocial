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