document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  if (menu && nav) {
    menu.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      menu.setAttribute('aria-expanded', String(open));
    });
  }
  document.querySelectorAll('.notice').forEach((notice) => {
    window.setTimeout(() => notice.classList.add('notice-hide'), 7000);
  });
  document.querySelectorAll('.detail-thumbs img').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      const hero = document.querySelector('.detail-main-image img');
      if (hero) hero.src = thumb.src;
    });
  });
});
