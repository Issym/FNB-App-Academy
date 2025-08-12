// menu toggle
const menuBtn = document.getElementById('menu-toggle');
const nav = document.getElementById('primary-nav');
if (menuBtn && nav) {
  menuBtn.addEventListener('click', () => {
    const expanded = menuBtn.getAttribute('aria-expanded') === 'true';
    menuBtn.setAttribute('aria-expanded', String(!expanded));
    nav.style.display = expanded ? 'none' : 'flex';
  });
  // ensure visible on resize
  window.addEventListener('resize', () => {
    if (window.innerWidth > 700 && nav) nav.style.display = 'flex';
  });
}

// animal search filter (if on animals.html)
const search = document.getElementById('animal-search');
if (search) {
  search.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    document.querySelectorAll('.animal-item').forEach(item => {
      const name = item.getAttribute('data-name') || item.querySelector('h3').textContent.toLowerCase();
      item.style.display = name.includes(q) ? '' : 'none';
    });
  });
}

// lazy images tiny enhancement: add loading attr to images if not present
document.querySelectorAll('img').forEach(img => {
  if (!img.getAttribute('loading')) img.setAttribute('loading', 'lazy');
});
